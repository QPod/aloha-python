import queue
import threading

from .base import BaseStreamer, BaseWorker, TIMEOUT_WORKER, logger


class ThreadedWorker(BaseWorker):
    def __init__(self, func_predict: callable, batch_size: int, max_latency: float,
                 request_queue, response_queue, *args, **kwargs):
        super().__init__(func_predict, batch_size, max_latency, *args, **kwargs)
        self._request_queue = request_queue
        self._response_queue = response_queue


class ThreadedStreamer(BaseStreamer):
    def __init__(self, predict_function: callable, batch_size: int, max_latency: float = 0.1, worker_timeout: float = TIMEOUT_WORKER):
        super().__init__(worker_timeout=worker_timeout)

        self._input_queue = queue.Queue()
        self._output_queue = queue.Queue()

        self._worker_destroy_event = threading.Event()
        self._worker = ThreadedWorker(
            predict_function, batch_size, max_latency, self._input_queue, self._output_queue,
            destroy_event=self._worker_destroy_event
        )
        self._worker_thread = threading.Thread(target=self._worker.run_forever, name="thread_worker")
        self._worker_thread.daemon = True
        self._worker_thread.start()
        self._delay_setup()

    def destroy_workers(self):
        self._worker_destroy_event.set()
        self._worker_thread.join(timeout=self._worker_timeout)
        if self._worker_thread.is_alive():
            raise TimeoutError("worker_thread destroy timeout")
        logger.info("workers destroyed")
