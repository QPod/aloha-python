import multiprocessing
import os

from .base import BaseStreamer, BaseWorker, TIMEOUT_WORKER, logger
from .managed_model import ManagedModel


class MultiProcessWorker(BaseWorker):
    def __init__(self, func_predict: callable, batch_size: int, max_latency: float,
                 request_queue, response_queue, model_init_args, model_init_kwargs: dict, *args, **kwargs):
        super().__init__(func_predict, batch_size, max_latency, *args, **kwargs)
        self._request_queue = request_queue
        self._response_queue = response_queue
        self._model_init_args = model_init_args or []
        self._model_init_kwargs = model_init_kwargs or {}

    def run_forever(self, gpu_id=None, ready_event=None, destroy_event=None):
        # if it is a managed model, lazy init model after forked & set CUDA_VISIBLE_DEVICES
        if isinstance(self.func_predict, type) and issubclass(self.func_predict, ManagedModel):
            model_class = self.func_predict
            logger.info("[gpu worker %d] init model on gpu:%s" % (os.getpid(), gpu_id))
            self._model = model_class(gpu_id)
            self._model.init_model(*self._model_init_args, **self._model_init_kwargs)
            logger.info("[gpu worker %d] init model on gpu:%s" % (os.getpid(), gpu_id))
            self._predict = self._model.predict
            if ready_event:
                ready_event.set()  # tell father process that init is finished
        if destroy_event is not None:
            self.destroy_event = destroy_event
        super().run_forever()


class MultiProcessStreamer(BaseStreamer):
    def __init__(self, func_predict: callable, batch_size: int, max_latency: float = 0.1, worker_num: int = 1,
                 cuda_devices=None, model_init_args=None, model_init_kwargs: dict = None, wait_for_worker_ready: bool = False,
                 mp_start_method='spawn', worker_timeout: float = TIMEOUT_WORKER):
        super().__init__(worker_timeout=worker_timeout)

        self.multiprocess = multiprocessing.get_context(mp_start_method)
        self._input_queue = self.multiprocess.Queue()
        self._output_queue = self.multiprocess.Queue()

        self.worker_num = worker_num
        self.cuda_devices = cuda_devices

        self._worker = MultiProcessWorker(
            func_predict, batch_size, max_latency, self._input_queue, self._output_queue,
            model_init_args, model_init_kwargs
        )
        self._worker_processes = []
        self._worker_ready_events = []
        self._worker_destroy_events = []
        self._setup_gpu_worker()
        if wait_for_worker_ready:
            self._wait_for_worker_ready()
        self._delay_setup()

    def _setup_gpu_worker(self):
        for i in range(self.worker_num):
            ready_event = self.multiprocess.Event()
            destroy_event = self.multiprocess.Event()
            if self.cuda_devices is not None:
                gpu_id = self.cuda_devices[i % len(self.cuda_devices)]
                args = (gpu_id, ready_event, destroy_event)
            else:
                args = (None, ready_event, destroy_event)
            p = self.multiprocess.Process(target=self._worker.run_forever, args=args, name="stream_worker", daemon=True)
            p.start()
            self._worker_processes.append(p)
            self._worker_ready_events.append(ready_event)
            self._worker_destroy_events.append(destroy_event)

    def _wait_for_worker_ready(self, timeout=None):
        if timeout is None:
            timeout = self._worker_timeout
        # wait for all workers finishing init
        for i, e in enumerate(self._worker_ready_events):
            # todo: select all events with timeout
            is_ready = e.wait(timeout)
            logger.info("gpu worker:%d ready state: %s" % (i, is_ready))

    def destroy_workers(self):
        for e in self._worker_destroy_events:
            e.set()
        for p in self._worker_processes:
            p.join(timeout=self._worker_timeout)
            if p.is_alive():
                raise TimeoutError("worker_process destroy timeout")
        logger.info("workers destroyed")
