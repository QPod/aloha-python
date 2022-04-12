__all__ = ('get_gpu_info',)

# ! `pip install pynvml`, reference: https://github.com/gpuopenanalytics/pynvml

from collections import namedtuple

from ..logger import LOG

try:
    import pynvml
    from pynvml import NVMLError
except ImportError:
    raise RuntimeError('Please install package `pynvml` first!')

Device = namedtuple('Device', field_names='index,name,arch')
DeviceStatus = namedtuple('DeviceStatus', field_names='mem_total,mem_free,mem_used,gpu_rate,mem_rate')


class NvInfo:
    def __init__(self):
        self.nv = pynvml

        try:
            self.nv.nvmlInit()
            ver: bytes = self.nv.nvmlSystemGetDriverVersion()
            version = ver.decode(encoding='UTF-8')
            LOG.info('Nvidia Driver version: %s' % version)
        except NVMLError as e:
            LOG.info('NVML library NOT found!')
            LOG.info(str(e))

    def __del__(self):
        try:
            self.nv.nvmlShutdown()
        except (OSError, NVMLError):
            pass

    @property
    def get_device_count(self) -> int:
        try:
            return self.nv.nvmlDeviceGetCount()
        except NVMLError:
            return 0

    def get_device_list(self) -> list:
        list_device = []
        for i in range(self.get_device_count):
            handler = self._get_device_handler(index_device=i)
            name, arch = None, None

            try:
                name = self.nv.nvmlDeviceGetName(handler).decode(encoding='UTF-8')
            except NVMLError as e:
                LOG.info('Failed to get device name!')
                LOG.info(str(e))

            try:
                arch = self.nv.nvmlDeviceGetArchitecture(handler)
            except NVMLError as e:
                LOG.info('Failed to get device architecture!')
                LOG.info(str(e))

            device = Device(index=i, name=name, arch=arch)
            LOG.info('Found device {index} info: name={name}; arch={arch}'.format(**device._asdict()))
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


def get_gpu_info() -> dict:
    nv_info = NvInfo()
    result = []
    list_devices = nv_info.get_device_list()
    for i, d in enumerate(list_devices):
        status = nv_info.get_device_status(index_device=i)
        item = {
            'device': d._asdict(),
            'status': status._asdict()
        }
        result.append(item)

    return {
        "gpu_info": result
    }


def main(*args, **kwargs):
    info_gpus = get_gpu_info()
    import json
    print(json.dumps(info_gpus, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
