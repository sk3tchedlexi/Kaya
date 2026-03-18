# ∿ Kaya

Kaya is a short, portfolio project, turned full application. It was made to monitor system resources, docker images, and processes. With eye-appealing graphs and panes you can see exactly how much strain your server is under!

![Kaya Dashboard Screenshot](screenshot.png)

# ∿ Requirements

- Ubuntu (or compatible Linux) host
- Docker + Docker Compose **or** CasaOS
- NVIDIDA GPU (Optional, if present; NVIDIA driver 535+ must be installed before deploying)
- ``kernel.sysrq`` must be enabled for shutdown/restart buttons to work (see "Enabling Shutdown/Restart")

# ∿ Installation

To install **Kaya** via CasaOS, simply open the App Store, navigate to the "Custom Install" menu, select "Import" in the top right, and paste the contents of the docker-compose.yml inside the text field, or upload it directly.

To install **Kaya** through Docker Compose, first Clone the repo, then run ``docker compose up -d`` and then access the Dashboard at ``http://your-server-ip:9783``

# ∿ Enabling Shutdown/Restart

- Run ``echo 1 | sudo tee /proc/sys/kernel/sysrq`` on the host
- To make permanent: ``echo "kernel.sysrq = 1" | sudo tee -a /etc/sysctl.conf``

# ∿ GPU support

- Requires NVIDIA driver installed on the host
- Device nodes ``/dev/nvidia*`` must exist before deploying the container
- pynvml reads GPU stats via mounted host libraries

# ∿ Features

- CPU, GPU, RAM, Disk usage with history charts
- Temperature monitoring (CPU, GPU, NVMe, Motherboard)
- Docker container list
- Process viewer (top CPU / top RAM)
- Shutdown and restart buttons
- Settings: refresh interval, light/dark theme, custom wallpaper
