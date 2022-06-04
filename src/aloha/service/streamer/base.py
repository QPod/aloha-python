import abc
import logging
import os
import queue
import threading
import time
import uuid
import weakref

TIME_SLEEP = 0.001
TIMEOUT = 1.0
TIMEOUT_WORKER = 20

logger = logging.getLogger()


# logger.setLevel("INFO")


class FutureCache(dict):
    # Dict for weakref only
    pass


class Future:
    def __init__(self, task_id, task_size: int, future_cache_ref):
        self._id = task_id
        self._size = task_size
        self._future_cache_ref = future_cache_ref
        self._outputs = []
        self._finish_event = threading.Event()

    def done(self):
        return self._finish_event.is_set()

    def result(self, timeout=None):
        if self._size == 0:
            self._finish_event.set()
            return []
        finished = self._finish_event.wait(timeout)

        if not finished:
            raise TimeoutError("Task: %d Timeout" % self._id)

        # remove from future_cache
        future_cache = self._future_cache_ref()
        if future_cache is not None:
            del future_cache[self._id]

        # [(request_id, output), ...] sorted by request_id
        self._outputs.sort(key=lambda i: i[0])
        # restore batch result from outputs
        batch_result = [i[1] for i in self._outputs]

        return batch_result

    def append_result(self, it_id, it_output):
        self._outputs.append((it_id, it_output))
        if len(self._outputs) >= self._size:
            self._finish_event.set()


class BaseWorker(abc.ABC):
    __slots__ = ('_request_queue', '_response_queue')

    def __init__(self, func_predict: callable, batch_size: int, max_latency: float, destroy_event=None, *args, **kwargs):
        # assert callable(predict_function)
        self.pid = os.getpid()
        self.func_predict = func_predict
        self.batch_size = batch_size
        self.max_latency = max_latency
        self.destroy_event = destroy_event  # kwargs.get("destroy_event", None)

    def _recv_request(self, timeout: float = TIMEOUT):
        try:
            item = self._request_queue.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError
        else:
            return item

    def _send_response(self, client_id, task_id, request_id, model_output):
        self._response_queue.put((task_id, request_id, model_output))

    def run_forever(self, *args, **kwargs):
        self.pid = os.getpid()  # overwrite the pid
        logger.info("[gpu worker %d] %s start working" % (self.pid, self))

        while True:
            handled = self._run_once()
            if self.destroy_event and self.destroy_event.is_set():
                break
            if not handled:
                # sleep if no data handled last time
                time.sleep(TIME_SLEEP)
        logger.info("[gpu worker %d] %s shutdown" % (self.pid, self))

    def model_predict(self, batch_input):
        batch_result = self.func_predict(batch_input)
        assert len(batch_input) == len(batch_result), "input batch size {} and output batch size {} must be equal.".format(len(batch_input), len(batch_result))
        return batch_result

    def _run_once(self):
        batch = []
        start_time = time.time()
        for i in range(self.batch_size):
            try:
                item = self._recv_request(timeout=self.max_latency)
            except TimeoutError:
                # each item timeout exceed the max latency
                break
            else:
                batch.append(item)
            if (time.time() - start_time) > self.max_latency:
                # total batch time exceeds the max latency
                break
        if not batch:
            return 0

        model_inputs = [i[3] for i in batch]
        model_outputs = self.model_predict(model_inputs)

        # send results to response
        for i, item in enumerate(batch):
            client_id, task_id, request_id, _ = item
            self._send_response(client_id, task_id, request_id, model_outputs[i])

        batch_size = len(batch)
        logger.info("[gpu worker %d] run_once batch_size: %d start_at: %s spend: %s" % (
            self.pid, batch_size, start_time, time.time() - start_time))
        return batch_size


class BaseStreamer(abc.ABC):
    __slots__ = ('_input_queue', '_output_queue')

    def __init__(self, worker_timeout: float = TIMEOUT_WORKER, *args, **kwargs):
        self._client_id = str(uuid.uuid4())
        self._task_id = 0
        self._future_cache = FutureCache()  # {task_id: future}
        self._worker_timeout = worker_timeout  # kwargs.get("worker_timeout", TIMEOUT_WORKER)

        self.back_thread = threading.Thread(target=self._loop_collect_result, name="thread_collect_result")
        self.back_thread.daemon = True
        self.lock = threading.Lock()

    def _send_request(self, task_id, request_id, model_input):
        self._input_queue.put((0, task_id, request_id, model_input))

    def _recv_response(self, timeout=TIMEOUT):
        try:
            message = self._output_queue.get(timeout=timeout)
        except queue.Empty:
            message = None
        return message

    @abc.abstractmethod
    def destroy_workers(self):
        raise NotImplementedError

    def _delay_setup(self):
        self.back_thread.start()

    def _input(self, batch: list) -> int:
        """input a batch, distribute each item to mq, return task_id"""
        # task id in one client
        self.lock.acquire()
        task_id = self._task_id
        self._task_id += 1
        self.lock.release()
        # request id in one task
        request_id = 0

        future = Future(task_id, len(batch), weakref.ref(self._future_cache))
        self._future_cache[task_id] = future

        for model_input in batch:
            self._send_request(task_id, request_id, model_input)
            request_id += 1

        return task_id

    def _loop_collect_result(self):
        logger.info("start _loop_collect_result")
        while True:
            message = self._recv_response(timeout=TIMEOUT)
            if message:
                (task_id, request_id, item) = message
                future = self._future_cache[task_id]
                future.append_result(request_id, item)
            else:
                # todo
                time.sleep(TIME_SLEEP)

    def _output(self, task_id: int) -> list:
        future = self._future_cache[task_id]
        batch_result = future.result(self._worker_timeout)
        return batch_result

    def submit(self, batch):
        task_id = self._input(batch)
        future = self._future_cache[task_id]
        return future

    def predict(self, batch):
        task_id = self._input(batch)
        ret = self._output(task_id)
        assert len(batch) == len(ret), "input batch size {} and output batch size {} must be equal.".format(len(batch), len(ret))
        return ret
