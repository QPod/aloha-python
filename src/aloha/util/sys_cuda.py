__all__ = ('get_cuda_info',)

from collections import namedtuple

from ..logger import LOG

Status = namedtuple('Status', 'version,gpu_availability')


def get_gpu_status_for_tf(*args, **kwargs) -> dict:
    status = Status(version=None, gpu_availability=False)
    try:
        import tensorflow as tf
        LOG.info('tensorflow version = %s' % tf.__version__)
        status = Status(
            version=tf.__version__,
            gpu_availability=tf.test.is_gpu_available()
        )
    except Exception as e:
        LOG.error('Error detecting CUDA availability for tensorflow')
        LOG.error(str(e))
    return status._asdict()


def get_gpu_status_for_torch(*args, **kwargs) -> dict:
    status = Status(version=None, gpu_availability=False)
    try:
        import torch
        LOG.info('torch version = %s' % torch.__version__)
        status = Status(
            version=torch.__version__,
            gpu_availability=torch.cuda.is_available()
        )
    except Exception as e:
        LOG.error('Error detecting CUDA availability for torch')
        LOG.error(str(e))
    return status._asdict()


def get_gpu_status_for_paddle(*args, **kwargs) -> dict:
    status = Status(version=None, gpu_availability=False)
    try:
        import paddle
        LOG.info('Paddlepaddle version = %s' % paddle.__version__)
        paddle.utils.run_check()
        status = Status(
            version=paddle.__version__,
            gpu_availability=True
        )
    except Exception as e:
        LOG.error('Error detecting CUDA availability for paddle')
        LOG.error(str(e))
    return status._asdict()


def get_cuda_info(*args, **kwargs) -> dict:
    return {
        "cuda_availability_for_torch": get_gpu_status_for_torch(),
        "cuda_availability_for_tf": get_gpu_status_for_tf(),
        "cuda_availability_for_paddle": get_gpu_status_for_paddle(),
    }


def main(*args, **kwargs):
    data = get_cuda_info()
    import json
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
