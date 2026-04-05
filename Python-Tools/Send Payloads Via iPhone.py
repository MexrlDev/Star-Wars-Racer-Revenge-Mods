# Star Wars Revenge iPhone Payload sender
# Made by MexrlDev - Code Ver: 1.4

import socket
import subprocess
import platform
import sys
import os

# ========== CONFIGURE THESE ==========
DEFAULT_ROUTER_IP = ""   # <<< CHANGE to your PS4's IP address
DEFAULT_PORT = 9026
DEFAULT_PAYLOAD_NAME = ""   # <<< Change to payload name!! Can be .lua, .bin, .elf, etc.
# =====================================

# Helpers to load bin and etc lol..
def find_payload_file(name):
    """
    Look for file in:
      1. exact path
      2. current directory (./name)
      3. ./payloads/name
      4. ./lua/name
    Returns full path or None.
    """
    if os.path.exists(name) and os.path.isfile(name):
        return name
    candidates = [
        os.path.join(".", name),
        os.path.join(".", "payloads", name),
        os.path.join(".", "lua", name),
    ]
    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            return cand
    return None

def load_payload_file(filename):
    """
    Read ANY file (binary or text) as bytes.
    Returns bytes object, or None if error.
    """
    path = find_payload_file(filename)
    if not path:
        print(f"â File not found: {filename}")
        print(f"  Looked in: current folder, ./payloads/, ./lua/")
        return None
    try:
        with open(path, 'rb') as f:   # binary mode
            content = f.read()
        print(f"â Loaded file: {path} ({len(content)} bytes)")
        return content
    except Exception as e:
        print(f"â Error reading {path}: {e}")
        return None

# Network functions
def get_router_ip():
    """Detect default gateway (for fallback if DEFAULT_ROUTER_IP not set)."""
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
            except (subprocess.CalledProcessError, FileNotFoundError):
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

def send_payload(data, host, port):
    """Send raw bytes to host:port."""
    # data should already be bytes... hopefully they font byte me lol
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(data)
        print(f"â Sent {len(data)} bytes to {host}:{port}")
        return True
    except socket.error as e:
        print(f"â Socket error: {e}")
        if e.errno == 65:  # No route to host
            print("\n TIPS:")
            print("  - Is the PS4 on and connected to the same WiâFi?")
            print("  - Is the PS4âs IP address correct?")
            print(f"  - Current target: {host}:{port}")
            print("  - Try pinging the IP from another device.")
        return False
    except Exception as e:
        print(f"â Error: {e}")
        return False
    finally:
        sock.close()


# Main
def main():
    # Determine target IP and port
    host = DEFAULT_ROUTER_IP.strip()
    if not host:
        host = get_router_ip()
        if not host:
            print("ERROR: Could not determine router IP. Please set DEFAULT_ROUTER_IP in the script.")
            sys.exit(1)
    port = DEFAULT_PORT

    # Determine payload filename
    payload_filename = None
    if len(sys.argv) > 1:
        # First argument might be IP:port or just IP
        first = sys.argv[1]
        if ':' in first:
            parts = first.split(':', 1)
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                print(f"Invalid port, using {DEFAULT_PORT}")
        else:
            host = first
        # Second argument (if any) is payload filename
        if len(sys.argv) >= 3:
            payload_filename = sys.argv[2]
        # Third argument (if present and port not set) is port
        if len(sys.argv) >= 4 and ':' not in first:
            if sys.argv[3].isdigit():
                port = int(sys.argv[3])
    else:
        payload_filename = DEFAULT_PAYLOAD_NAME

    if not payload_filename:
        print("No payload file specified. Set DEFAULT_PAYLOAD_NAME or pass as argument.")
        sys.exit(1)

    # Loads the file
    payload_bytes = load_payload_file(payload_filename)
    if payload_bytes is None:
        sys.exit(1)   # File not found or read error

    # Sends it
    print(f"\nâ Target: {host}:{port}")
    print(f"â Payload: {payload_filename}")
    send_payload(payload_bytes, host, port)

if __name__ == "__main__":
    main()
