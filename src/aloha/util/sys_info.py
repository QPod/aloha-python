__all__ = ('get_sys_info',)

import platform
from datetime import datetime

import psutil

from ..logger import LOG

LOG.debug('Using psutil == %s' % psutil.__version__)


def get_size(bytes, suffix="B"):
    """Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_os_info(*args, **kwargs) -> dict:
    ret = {}

    boot_time = datetime.fromtimestamp(psutil.boot_time())
    ret['boot_time'] = boot_time.strftime('%Y-%m-%d %H:%M:%S.%f')

    uname = platform.uname()
    ret.update(uname._asdict())
    return ret


def get_cpu_info(*args, **kwargs) -> dict:
    cpu_freq = psutil.cpu_freq()  # CPU frequencies
    ret = {
        "num_cores_physical": psutil.cpu_count(logical=False),
        "num_cores_total": psutil.cpu_count(logical=True),
        "freq_max_mhz": f"{cpu_freq.max:.2f}",
        "freq_min_mhz": f"{cpu_freq.min:.2f}",
        "freq_cur_mhz": f"{cpu_freq.current:.2f}",
        "cpu_percent_total": f"{psutil.cpu_percent()}%",
    }
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        ret['cpu_percent_core_%02d' % i] = f"{percentage}%"

    return ret


def get_mem_info(*args, **kwargs) -> dict:
    svmem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "vm_total": f"{get_size(svmem.total)}",
        "vm_available": f"{get_size(svmem.available)}",
        "vm_used": f"{get_size(svmem.used)}",
        "vm_percent": f"{svmem.percent}%",

        "swap_total": f"{get_size(swap.total)}",
        "swap_free": f"{get_size(swap.free)}",
        "swap_used": f"{get_size(swap.used)}",
        "swap_percent": f"{swap.percent}%",
    }


def get_disk_info(*args, **kwargs) -> dict:
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    partitions = psutil.disk_partitions()

    ret = {
        "io_total_read": f"{get_size(disk_io.read_bytes)}",
        "io_total_write": f"{get_size(disk_io.write_bytes)}",
        "partitions": []
    }

    for partition in partitions:
        part = {
            "device": f"{partition.device}",
            "mount_point": f"{partition.mountpoint}",
            "fs_type": f"{partition.fstype}",
        }

        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            part.update({
                "size_total": f"{get_size(partition_usage.total)}",
                "size_used": f"{get_size(partition_usage.used)}",
                "size_free": f"{get_size(partition_usage.free)}",
                "percent_used": f"{partition_usage.percent}%",
            })
        except PermissionError:
            pass  # this can be caught due to the disk that isn't ready

        ret["partitions"].append(part)

    return ret


def get_net_info(*args, **kwargs) -> dict:
    # get IO statistics since boot
    net_io = psutil.net_io_counters()

    # get all network interfaces (virtual and physical)
    if_addresses = psutil.net_if_addrs()

    ret = {
        "net_total_sent": f"{get_size(net_io.bytes_sent)}",
        "net_total_received": f"{get_size(net_io.bytes_recv)}",
        "interfaces": []
    }

    for interface_name, interface_addresses in if_addresses.items():
        interface = {"name": interface_name}

        for address in interface_addresses:
            family = str(address.family).split('.')[-1]
            family = {'AF_LINK': 'mac', 'AF_INET': 'ipv4', 'AF_INET6': 'ipv6'}.get(family, family)

            interface['%s_address' % family] = address.address
            interface['%s_netmask' % family] = address.netmask
            interface['%s_broadcast' % family] = address.broadcast

        ret['interfaces'].append(interface)

    return ret


def get_sys_info(*args, **kwargs) -> dict:
    return {
        "os_info": get_os_info(),
        "cpu_info": get_cpu_info(),
        "mem_info": get_mem_info(),
        "disk_info": get_disk_info(),
        "net_info": get_net_info(),
    }


def main():
    data = get_sys_info()
    import json
    data = json.dumps(data, ensure_ascii=False, indent=2)
    print(data)


if __name__ == '__main__':
    main()
