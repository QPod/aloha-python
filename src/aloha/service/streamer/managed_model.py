import abc
import os


class ManagedModel(abc.ABC):
    def __init__(self, gpu_id=None, *args, **kwargs):
        self.model = None
        self.gpu_id = gpu_id
        self.set_gpu_id(self.gpu_id)

    @staticmethod
    def set_gpu_id(gpu_id=None):
        if gpu_id is not None:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    @abc.abstractmethod
    def init_model(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def predict(self, batch: list) -> list:
        raise NotImplementedError
