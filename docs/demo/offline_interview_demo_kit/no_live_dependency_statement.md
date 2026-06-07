# No Live Dependency Statement

The Day48 offline portfolio demo does not require live router or switch access.

No SSH is required.

No device configuration will be changed.

The demo will not change NAT, IP, VRRP, WireGuard, firewall, interface, route, reboot, reset, or device settings.

The demo does not require GitHub, internet access, VPN, WireGuard peers, iperf3 endpoints, MikroTik devices, Cisco devices, routers, switches, or firewalls.

Existing committed source code, committed documentation, local tests, local report-index behavior, local dashboard routes, and existing evidence references are enough to demonstrate the architecture and workflow.

Live testing is intentionally separated from the portfolio demo flow for safety. Live VRRP validation, live WireGuard execution, SSH-based validation, iperf3 performance testing, and device-changing workflows should only be run in a controlled lab environment with explicit operator intent.
