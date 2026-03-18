import psutil
import pynvml
import time

# Initialise NVML once at import time
try:
    pynvml.nvmlInit()
    _nvml_available = True
except pynvml.NVMLError:
    _nvml_available = False

# Keep a reference to the last disk I/O snapshot for delta calculation
_last_disk_io = None
_last_disk_time = None


def _get_cpu() -> dict:
    return {
        "percent": psutil.cpu_percent(interval=0.5),
        "cores":   psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),
        "model":   _cpu_model(),
    }


def _cpu_model() -> str:
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":")[1].strip()
    except Exception:
        pass
    return "Unknown CPU"


def _get_gpu() -> dict | None:
    if not _nvml_available:
        return None
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        util   = pynvml.nvmlDeviceGetUtilizationRates(handle)
        mem    = pynvml.nvmlDeviceGetMemoryInfo(handle)
        temp   = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        return {
            "percent":       float(util.gpu),
            "vram_used_gb":  round(mem.used  / 1024 ** 3, 2),
            "vram_total_gb": round(mem.total / 1024 ** 3, 2),
            "temp_c":        int(temp),
        }
    except pynvml.NVMLError:
        return None


def _get_ram() -> dict:
    vm = psutil.virtual_memory()
    return {
        "percent":  vm.percent,
        "used_gb":  round(vm.used  / 1024 ** 3, 2),
        "total_gb": round(vm.total / 1024 ** 3, 2),
    }


def _get_disk() -> dict:
    global _last_disk_io, _last_disk_time

    usage   = psutil.disk_usage("/")
    now     = time.monotonic()
    current = psutil.disk_io_counters()

    read_mbps  = 0.0
    write_mbps = 0.0

    if _last_disk_io is not None and _last_disk_time is not None:
        elapsed = now - _last_disk_time
        if elapsed > 0:
            read_mbps  = round((current.read_bytes  - _last_disk_io.read_bytes)  / elapsed / 1024 ** 2, 2)
            write_mbps = round((current.write_bytes - _last_disk_io.write_bytes) / elapsed / 1024 ** 2, 2)

    _last_disk_io   = current
    _last_disk_time = now

    return {
        "percent":    round(usage.percent, 1),
        "used_tb":    round(usage.used  / 1024 ** 4, 3),
        "total_tb":   round(usage.total / 1024 ** 4, 3),
        "read_mbps":  max(read_mbps,  0.0),
        "write_mbps": max(write_mbps, 0.0),
    }


def _get_temps() -> dict:
    temps = {
        "cpu_c":         None,
        "gpu_c":         None,
        "nvme_c":        None,
        "motherboard_c": None,
    }

    # CPU and motherboard via psutil sensors
    try:
        sensors = psutil.sensors_temperatures()

        # CPU — try common sensor names in order of preference
        for name in ("k10temp", "coretemp", "cpu_thermal", "cpu-thermal"):
            if name in sensors:
                entries = sensors[name]
                for label in ("Tctl", "Package id 0", ""):
                    match = next((e for e in entries if e.label == label), None)
                    if match:
                        temps["cpu_c"] = int(match.current)
                        break
                if temps["cpu_c"] is None and entries:
                    temps["cpu_c"] = int(entries[0].current)
                break

        # Motherboard
        for name in ("nct6775", "nct6779", "w83627ehf", "it8728"):
            if name in sensors:
                match = next((e for e in sensors[name] if "SYSTIN" in e.label or "SYS" in e.label), None)
                if match:
                    temps["motherboard_c"] = int(match.current)
                break

        # NVMe
        for name, entries in sensors.items():
            if "nvme" in name.lower():
                if entries:
                    temps["nvme_c"] = int(entries[0].current)
                break

    except (AttributeError, Exception):
        pass

    # GPU temp from NVML
    if _nvml_available:
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            temps["gpu_c"] = int(pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU))
        except pynvml.NVMLError:
            pass

    return temps


def _get_uptime() -> int:
    return int(time.time() - psutil.boot_time())


def collect() -> dict:
    """Return a full system snapshot as a dictionary."""
    return {
        "cpu":            _get_cpu(),
        "gpu":            _get_gpu(),
        "ram":            _get_ram(),
        "disk":           _get_disk(),
        "temps":          _get_temps(),
        "uptime_seconds": _get_uptime(),
    }