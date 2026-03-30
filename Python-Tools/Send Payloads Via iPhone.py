# Modified by MexrlDev to run on any iphone by using python apps
import socket
import subprocess
import platform
import sys

# ==================================================
# CONFIGURATION: Set your router IP here if you want.
# Leave empty to auto-detect (or prompt if detection fails).
# ==================================================
DEFAULT_IP = ""   # <-- Put your router IP here, youll see it when you run the jit exploit
# ==================================================

# The Lua payload to send
LUA_CODE = """
-- Hello script
send_notification("Hello from remote lua!")
"""

def get_router_ip():
    """Return the default gateway (router IP) for the current system."""
    system = platform.system().lower()

    try:
        if system == "windows":
            output = subprocess.check_output("ipconfig", shell=True, text=True)
            lines = output.splitlines()
            for i, line in enumerate(lines):
                if "Default Gateway" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        gateway = parts[1].strip()
                        if gateway and gateway != "0.0.0.0":
                            return gateway
        else:
            try:
                output = subprocess.check_output("ip route show default", shell=True, text=True)
                parts = output.split()
                for i, part in enumerate(parts):
                    if part == "via" and i + 1 < len(parts):
                        gateway = parts[i + 1]
                        return gateway
            except subprocess.CalledProcessError:
                output = subprocess.check_output("netstat -rn", shell=True, text=True)
                lines = output.splitlines()
                for line in lines:
                    if "default" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            gateway = parts[1]
                            if gateway != "0.0.0.0":
                                return gateway
    except Exception:
        pass
    return None

def send_payload(data, host, port=9026):
    """Send raw data over TCP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(data)
        print("Sent {} bytes to {}:{}".format(len(data), host, port))
    except Exception as e:
        print("Error sending payload: {}".format(e))
    finally:
        sock.close()

def parse_host_port(arg):
    """Parse a string like '192.168.1.1:9026' into (host, port)."""
    if ':' in arg:
        parts = arg.split(':', 1)
        try:
            port = int(parts[1])
            return parts[0], port
        except ValueError:
            pass
    return arg, None

def main():
    host = None
    port = None

    if len(sys.argv) >= 2:
        h, p = parse_host_port(sys.argv[1])
        host = h
        if p is not None:
            port = p

    if len(sys.argv) >= 3 and port is None:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Invalid port: {}, using default 9026".format(sys.argv[2]))

    if host is None:
        if DEFAULT_IP.strip():
            host = DEFAULT_IP.strip()
        else:
            host = get_router_ip()
            if not host:
                print("Could not detect router IP automatically.")
                host = input("Please enter the router IP manually: ").strip()
                if not host:
                    print("No IP provided. Exiting.")
                    sys.exit(1)
            else:
                print("Using detected router IP: {}".format(host))

    if port is None:
        port = 9026

    data = LUA_CODE.strip().encode('utf-8')
    send_payload(data, host, port)

if __name__ == "__main__":
    main()
