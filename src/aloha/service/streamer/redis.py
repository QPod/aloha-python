import multiprocessing
import os
import pickle
import queue
import threading
import time

from redis import Redis

from .base import BaseStreamer, BaseWorker, TIMEOUT, TIME_SLEEP, logger


class RedisWorker(BaseWorker):
    def __init__(self, func_predict, batch_size: int, max_latency=0.1,
                 redis_broker="localhost:6379", prefix='',
                 model_init_args=None, model_init_kwargs=None, *args, **kwargs):
        # assert issubclass(model_class, ManagedModel)
        super().__init__(func_predict, batch_size, max_latency, *args, **kwargs)
        self._request_queue = queue.Queue()
        # redis worker does not need a response queue

        self.prefix = prefix
        self._model_init_args = model_init_args or []
        self._model_init_kwargs = model_init_kwargs or {}
        self._redis_broker = redis_broker
        self._redis = _RedisServer(0, self._redis_broker, self.prefix)

        self.back_thread = threading.Thread(target=self._loop_recv_request, name="thread_recv_request")
        self.back_thread.daemon = True
        self.back_thread.start()

    def _send_response(self, client_id, task_id, request_id, model_output):
        # override the parent method
        self._redis.send_response(client_id, task_id, request_id, model_output)

    def run_forever(self, gpu_id=None):
        logger.info("[gpu worker %d] init model on gpu:%s" % (os.getpid(), gpu_id))
        model_class = self.func_predict
        self._model = model_class(gpu_id)
        self._model.init_model(*self._model_init_args, **self._model_init_kwargs)
        self._predict = self._model.predict

        super().run_forever()

    def _loop_recv_request(self):
        logger.info("[gpu worker %d] start loop_recv_request" % (os.getpid()))
        while True:
            message = self._redis.recv_request(timeout=TIMEOUT)
            if message:
                (client_id, task_id, request_id, request_item) = pickle.loads(message)
                self._request_queue.put((client_id, task_id, request_id, request_item))
            else:
                # sleep if recv timeout
                time.sleep(TIME_SLEEP)


class RedisStreamer(BaseStreamer):
    """
    1. input batch as a task
    2. distribute every single item in batch to redis
    3. backend loop collecting results
    3. output batch result for a task when every single item is returned
    """

    def __init__(self, redis_broker="localhost:6379", prefix=''):
        super().__init__()

        # redis streamer does not need input_queue/output_queue

        self.prefix = prefix
        self._redis_broker = redis_broker
        self._redis = _RedisClient(self._client_id, self._redis_broker, self.prefix)
        self._delay_setup()

    def _send_request(self, task_id, request_id, model_input):
        self._redis.send_request(task_id, request_id, model_input)

    def _recv_response(self, timeout=TIMEOUT):
        return self._redis.recv_response(timeout)

    def destroy_workers(self):
        pass


def _setup_redis_worker_and_runforever(
        model_class, batch_size, max_latency, gpu_id, redis_broker, prefix='', model_init_args=None, model_init_kwargs=None
):
    redis_worker = RedisWorker(
        model_class, batch_size, max_latency, redis_broker=redis_broker, prefix=prefix,
        model_init_args=model_init_args, model_init_kwargs=model_init_kwargs
    )
    redis_worker.run_forever(gpu_id)


def run_redis_workers_forever(
        model_class, batch_size, max_latency=0.1,
        worker_num=1, cuda_devices=None, redis_broker="localhost:6379",
        prefix='', mp_start_method='spawn', model_init_args=None, model_init_kwargs=None
):
    procs = []
    mp = multiprocessing.get_context(mp_start_method)
    for i in range(worker_num):
        if cuda_devices is not None:
            gpu_id = cuda_devices[i % len(cuda_devices)]
        else:
            gpu_id = None
        args = (model_class, batch_size, max_latency, gpu_id, redis_broker, prefix, model_init_args, model_init_kwargs)
        p = mp.Process(target=_setup_redis_worker_and_runforever, args=args, name="stream_worker", daemon=True)
        p.start()
        procs.append(p)

    for p in procs:
        p.join()


class _RedisAgent:
    def __init__(self, redis_id, redis_broker='localhost:6379', prefix=''):
        self._redis_id = redis_id
        self._redis_host = redis_broker.split(":")[0]
        self._redis_port = int(redis_broker.split(":")[1])
        self._redis_request_queue_name = "request_queue" + prefix
        self._redis_response_pb_prefix = "response_pb_" + prefix
        self._redis = Redis(host=self._redis_host, port=self._redis_port)
        self._response_pb = self._redis.pubsub(ignore_subscribe_messages=True)
        self._setup()

    def _setup(self):
        raise NotImplementedError

    def _response_pb_name(self, redis_id):
        return self._redis_response_pb_prefix + redis_id


class _RedisClient(_RedisAgent):
    def _setup(self):
        self._response_pb.subscribe(self._response_pb_name(self._redis_id))

    def send_request(self, task_id, request_id, model_input):
        message = (self._redis_id, task_id, request_id, model_input)
        self._redis.lpush(self._redis_request_queue_name, pickle.dumps(message))

    def recv_response(self, timeout):
        message = self._response_pb.get_message(timeout=timeout)
        if message:
            return pickle.loads(message["data"])


class _RedisServer(_RedisAgent):
    def _setup(self):
        self._response_pb.psubscribe(self._redis_response_pb_prefix + "*")  # server subscribe all pubsub

    def recv_request(self, timeout):
        message = self._redis.blpop(self._redis_request_queue_name, timeout=timeout)
        if message:  # (queue_name, data)
            return message[1]

    def send_response(self, client_id, task_id, request_id, model_output):
        message = (task_id, request_id, model_output)
        channel_name = self._response_pb_name(client_id)
        self._redis.publish(channel_name, pickle.dumps(message))
