from aloha.service.v0 import APIHandler
from aloha.util.sys_cuda import get_cuda_info
from aloha.util.sys_gpu import get_gpu_info
from aloha.util.sys_info import get_sys_info


class SysStatusInfo(APIHandler):
    @staticmethod
    def get_sys_info(kind: str = None, **kwargs) -> dict:
        kinds = ['sys', 'gpu', 'cuda']
        if kind is None:
            pass
        else:
            kinds = [kind]

        dict_func = {
            "sys": get_sys_info,
            "gpu": get_gpu_info,
            "cuda": get_cuda_info,
        }
        ret = {}
        for k in kinds:
            ret.update({k: dict_func.get(k, get_sys_info)()})

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
