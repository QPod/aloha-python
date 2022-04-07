# ! `pip install pynvml`, reference: https://github.com/gpuopenanalytics/pynvml

from collections import namedtuple

from ..logger import LOG

try:
    import pynvml
except ImportError:
    raise RuntimeError('Please install package `pynvml` first!')

Device = namedtuple('Device', field_names='index,name,arch')
DeviceStatus = namedtuple('DeviceStatus', field_names='mem_total,mem_free,mem_used,gpu_rate,mem_rate')


class NvInfo:
    def __init__(self):
        self.nv = pynvml
        self.nv.nvmlInit()
        ver: bytes = self.nv.nvmlSystemGetDriverVersion()
        version = ver.decode(encoding='UTF-8')
        LOG.info('Nvidia Driver version: %s' % version)

    def __del__(self):
        self.nv.nvmlShutdown()

    @property
    def get_device_count(self) -> int:
        try:
            return self.nv.nvmlDeviceGetCount()
        except pynvml.NVMLError as e:
            return 0

    def get_device_list(self) -> list:
        list_device = []
        for i in range(self.get_device_count):
            handler = self._get_device_handler(index_device=i)
            print(self.nv.nvmlDeviceGetArchitecture(handler))
            device = Device(
                index=i,
                name=self.nv.nvmlDeviceGetName(handler).decode(encoding='UTF-8'),
                arch=self.nv.nvmlDeviceGetArchitecture(handler)
            )

            list_device.append(device)

        return list_device

    def _get_device_handler(self, index_device=0):
        return self.nv.nvmlDeviceGetHandleByIndex(index_device)

    def get_device_status(self, index_device=0) -> DeviceStatus:
        handler = self._get_device_handler(index_device=index_device)
        mem_info = self.nv.nvmlDeviceGetMemoryInfo(handler)
        util_info = self.nv.nvmlDeviceGetUtilizationRates(handler)
        return DeviceStatus(
            mem_total=mem_info.total,
            mem_free=mem_info.free,
            mem_used=mem_info.used,
            gpu_rate=util_info.gpu,
            mem_rate=util_info.memory
        )


def main(*args, **kwargs):
    import json
    n = NvInfo()
    list_devices = n.get_device_list()
    for i, d in enumerate(list_devices):
        status = n.get_device_status(index_device=i)
        item = {
            'device': d._asdict(),
            'status': status._asdict()
        }
        print(json.dumps(item))


if __name__ == '__main__':
    main()
