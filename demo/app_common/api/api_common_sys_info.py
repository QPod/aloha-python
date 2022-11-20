from aloha.service.api.v0 import APIHandler
from aloha.util import (sys_info, sys_gpu, sys_cuda)


class SysStatusInfo(APIHandler):
    @staticmethod
    def get_sys_info(kind: str = None, **kwargs) -> dict:
        kinds = ['sys', 'gpu', 'cuda']
        if kind is None:
            pass
        else:
            kinds = [kind]

        dict_func = {
            "sys": sys_info.get_sys_info,
            "os": sys_info.get_os_info,
            "cpu": sys_info.get_cpu_info,
            "mem": sys_info.get_mem_info,
            "disk": sys_info.get_disk_info,
            "net": sys_info.get_net_info,

            "gpu": sys_gpu.get_gpu_info,
            "cuda": sys_cuda.get_cuda_info,
            "cuda-torch": sys_cuda.get_gpu_status_for_torch,
            "cuda-tf": sys_cuda.get_gpu_status_for_tf,
            "cuda-paddle": sys_cuda.get_gpu_status_for_paddle,
        }
        ret = {}
        for k in kinds:
            ret.update({k: dict_func.get(k, sys_info.get_sys_info)()})

        return ret

    def response(self, kind: str = None, *args, **kwargs) -> dict:
        return self.get_sys_info(kind=kind)

    async def get(self, kind: str = None, *args, **kwargs):
        data = self.get_sys_info(kind=kind)
        return self.finish(data)


default_handlers = [
    (r"/api/common/sys_info", SysStatusInfo),
    (r"/api/common/sys_info/(.*)", SysStatusInfo),
]
