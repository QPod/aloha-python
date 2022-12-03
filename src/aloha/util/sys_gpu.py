__all__ = ('get_gpu_info',)

# ! `pip install pynvml`, reference: https://github.com/gpuopenanalytics/pynvml

from collections import namedtuple

from ..logger import LOG

try:
    import pynvml as nvml
    from pynvml.smi import nvidia_smi

    LOG.debug('Using pynvml == %s' % nvml.__version__)
except ImportError:
    LOG.warn('Package `pynvml` NOT installed! Cannot get GPU info.')
    nvml = nvidia_smi = None

Device = namedtuple('Device', field_names='index,name,arch')
DeviceStatus = namedtuple('DeviceStatus', field_names='mem_total,mem_free,mem_used,gpu_rate,mem_rate')


class NvInfo:
    def __init__(self):
        global nvml
        if nvml is None:
            return
        try:
            nvml.nvmlInit()
            LOG.debug('NVML loaded and initialized successfully.')
        except Exception as e:
            LOG.error('Fail to initialize NVML!')
            nvml = None

    def __del__(self):
        try:
            if nvml is not None:
                nvml.nvmlShutdown()
        except Exception as e:
            LOG.error('Exception removing NvInfo: %s' % e)

    @staticmethod
    def get_driver_version() -> str:
        if nvml is not None:
            try:
                ver: bytes = nvml.nvmlSystemGetDriverVersion()
                LOG.debug('GPU driver version %s' % str(ver))
                return ver.decode(encoding='UTF-8')
            except Exception as e:
                LOG.info('NVML library error: %s' % str(e))
        return 'Unknown'

    @staticmethod
    def get_device_count() -> int:
        try:
            return nvml.nvmlDeviceGetCount()
        except Exception as e:
            LOG.info('NVML library error: %s' % str(e))
            return 0

    def get_device_list(self) -> list:
        list_device = []
        for i in range(self.get_device_count()):
            handler = self._get_device_handler(index_device=i)
            name, arch = None, None

            try:
                name = nvml.nvmlDeviceGetName(handler).decode(encoding='UTF-8')
            except Exception as e:
                LOG.info('Failed to get device name!')
                LOG.info(str(e))

            try:
                arch = nvml.nvmlDeviceGetArchitecture(handler)
            except Exception as e:
                LOG.info('Failed to get device architecture!')
                LOG.info(str(e))

            device = Device(index=i, name=name, arch=arch)
            LOG.debug('Found device {index} info: name={name}; arch={arch}'.format(**device._asdict()))
            list_device.append(device)

        return list_device

    def _get_device_handler(self, index_device=0):
        return nvml.nvmlDeviceGetHandleByIndex(index_device)

    def get_device_status(self, index_device=0) -> DeviceStatus:
        handler = self._get_device_handler(index_device=index_device)
        mem_info = nvml.nvmlDeviceGetMemoryInfo(handler)
        util_info = nvml.nvmlDeviceGetUtilizationRates(handler)
        return DeviceStatus(
            mem_total=mem_info.total,
            mem_free=mem_info.free,
            mem_used=mem_info.used,
            gpu_rate=util_info.gpu,
            mem_rate=util_info.memory
        )

    @staticmethod
    def get_smi():
        if nvidia_smi is None:
            return
        try:
            return nvidia_smi.getInstance()
        except Exception as e:
            LOG.warn('Failed to get smi: %s' % str(e))
            return


def get_gpu_info(*args, **kwargs) -> dict:
    nv_info = NvInfo()
    list_device = []
    list_devices = nv_info.get_device_list()
    for i, d in enumerate(list_devices):
        status = nv_info.get_device_status(index_device=i)
        item = {
            'device': d._asdict(),
            'status': status._asdict()
        }
        list_device.append(item)

    ret = {
        "driver_version": nv_info.get_driver_version(),
        "devices": list_device,
    }

    smi = nv_info.get_smi()
    if smi is not None:
        if len(args) == 0:
            args = 'name;vbios_version;inforom.oem;compute-apps'.split(';')
        for k in args:
            ret[k] = smi.DeviceQuery(k)

    return {"gpu_info": ret}


def main(*args, **kwargs):
    info_gpus = get_gpu_info()
    import json
    print(json.dumps(info_gpus, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
