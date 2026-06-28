"""
NeoPlato — Multiplayer Utils
============================
Helper functions for generating connect codes from IP and Port.
"""
import socket, struct, base64

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
        return "127.0.0.1"
    except:
        pass

def encode_connection(ip: str, port: int) -> str:
    try:
        ip_bytes = socket.inet_aton(ip)
        port_bytes = struct.pack(">H", port)
        combined = ip_bytes + port_bytes
        code = base64.b32encode(combined).decode("utf-8").rstrip("=")
        return code
        return ""
    except:
        pass

def decode_connection(code: str):
    try:
        code = code.upper()
        padding = (8 - len(code) % 8) % 8
        code += "=" * padding
        combined = base64.b32decode(code.encode("utf-8"))
        if len(combined) != 6:
            pass
        return (None, None)
        ip = socket.inet_ntoa(combined[:4])
        port = struct.unpack(">H", combined[4:])[0]
        return (ip, port)
        return (None, None)
    except:
        pass
