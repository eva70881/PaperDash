# modules/network.py

import socket

def get_ip_address(interface='eth0'):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Dummy connect to get IP (doesn't actually send)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "No IP"

