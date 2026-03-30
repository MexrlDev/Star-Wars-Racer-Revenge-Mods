# Modified by MexrlDev to run on any iphone by using python apps

# Code Ver: 1.3

import socket
import subprocess
import platform
import sys
import urllib.request
import urllib.error
import re


# IP Config

DEFAULT_ROUTER_IP = ""   # ADD… Your up here.. you can also find it in the Alert JIT Exploit give you.

DEFAULT_PORT = 9026

# Payloads – Add your own Lua scripts here!

LUA_PAYLOADS = {
    "hello": """
-- Hello script
send_notification("Hello from remote lua!")
""",
    "notification": """
-- Send a custom notification
local msg = "This is a test notification"
send_notification(msg)
""",
    # Add more Lua payloads below:
    # "my_script": """
    # -- Your Lua code here
    # send_notification("Hello from ps4 :D")
    # """,
}


# Binary Payloads

BINARY_PAYLOADS = {
    # "example_bin": "https://example.com/example.bin",
    # "example_elf": "https://example.com/example.elf",
}

# Utility Functions

def get_router_ip():
    """Try to detect the default gateway (router IP) using system commands."""
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
            # Try 'ip route' first (Linux, macOS with iproute2)
            try:
                output = subprocess.check_output("ip route show default", shell=True, text=True)
                parts = output.split()
                for i, part in enumerate(parts):
                    if part == "via" and i + 1 < len(parts):
                        gateway = parts[i + 1]
                        return gateway
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to 'netstat -rn' (macOS, BSD, etc.)
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

def get_router_ip_interactive():
    """Ask the user for the router IP manually."""
    print("Auto‑detection of router IP failed.")
    ip = input("Please enter your router IP (e.g., 192.168.1.1): ").strip()
    if not ip:
        print("No IP provided. Exiting.")
        sys.exit(1)
    return ip

def send_payload(data, host, port):
    """
    Send raw data (bytes) to host:port.
    data can be bytes or string (will be encoded to UTF-8).
    Returns True on success, False on error.
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(data)
        print(f"✓ Sent {len(data)} bytes to {host}:{port}")
        return True
    except Exception as e:
        print(f"✗ Error sending payload: {e}")
        return False
    finally:
        sock.close()

def fetch_url(url):
    """Download data from a URL with a 10‑second timeout. Returns bytes or None if error."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read()
    except urllib.error.URLError as e:
        print(f"✗ Failed to fetch URL: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error while fetching: {e}")
        return None

def is_url(string):
    """Return True if string looks like a URL (starts with http:// or https://)."""
    return string.startswith(('http://', 'https://'))

def load_from_url(url, force_type=None):
    """
    Fetch data from a URL.
    If force_type is 'lua' or 'bin', interpret accordingly.
    Otherwise, try to decode as UTF-8; if successful, treat as Lua text,
    else treat as binary.
    Returns (data, is_binary) where data is either string (Lua) or bytes (binary).
    """
    raw = fetch_url(url)
    if raw is None:
        return None, False

    if force_type == 'lua':
        try:
            text = raw.decode('utf-8')
            return text, False
        except UnicodeDecodeError:
            print("✗ The fetched content is not valid UTF‑8. Cannot send as Lua.")
            return None, False
    elif force_type == 'bin':
        return raw, True
    else:
        try:
            text = raw.decode('utf-8')
            return text, False
        except UnicodeDecodeError:
            return raw, True

def show_available_payloads():
    """Print all Lua and binary payloads with type indicators."""
    print("\nAvailable payloads:")
    if LUA_PAYLOADS:
        print("  [Lua]")
        for name in LUA_PAYLOADS:
            print(f"    - {name}")
    if BINARY_PAYLOADS:
        print("  [Binary]")
        for name in BINARY_PAYLOADS:
            print(f"    - {name}")
    print("You can also enter a URL (http:// or https://) to load a payload from the web.")
    print("  Prefix with 'lua:' or 'bin:' to force type (e.g., lua:https://...)\n")

def select_payload():
    """
    Interactively ask the user which payload to send.
    Returns a tuple: (payload_data, is_binary)
    """
    show_available_payloads()
    while True:
        choice = input("Enter payload name, URL, or 'q' to quit: ").strip().lower()
        if choice == 'q':
            sys.exit(0)


        force_type = None
        if choice.startswith('lua:'):
            force_type = 'lua'
            choice = choice[4:]
        elif choice.startswith('bin:'):
            force_type = 'bin'
            choice = choice[4:]

        if choice in LUA_PAYLOADS:
            return LUA_PAYLOADS[choice], False
        if choice in BINARY_PAYLOADS:
            url = BINARY_PAYLOADS[choice]
            print(f"Fetching binary from {url} ...")
            data, is_bin = load_from_url(url, force_type='bin')  # always binary
            if data is not None:
                return data, is_bin
            else:
                print(f"Failed to load binary payload '{choice}'. Try again.")
                continue

        # Check if it's a URL
        if is_url(choice):
            print(f"Fetching from {choice} ...")
            data, is_bin = load_from_url(choice, force_type)
            if data is not None:
                return data, is_bin
            else:
                print("Failed to load from URL. Try again.")
                continue

        print(f"Unknown payload '{choice}'. Please try again.")

def get_target_interactive(current_host, current_port):
    """Ask the user if they want to change the target host/port."""
    print(f"\nCurrent target: {current_host}:{current_port}")
    change = input("Change target? (y/n): ").strip().lower()
    if change != 'y':
        return current_host, current_port

    new_host = input(f"Enter new IP (default: {current_host}): ").strip()
    if not new_host:
        new_host = current_host

    port_str = input(f"Enter new port (default: {current_port}): ").strip()
    if port_str.isdigit():
        new_port = int(port_str)
    else:
        new_port = current_port

    return new_host, new_port

def interactive_loop():
    """Main interactive loop: choose target, payload, send, repeat."""

    host = DEFAULT_ROUTER_IP.strip() or get_router_ip()
    if not host:
        host = get_router_ip_interactive()
    port = DEFAULT_PORT

    while True:
        host, port = get_target_interactive(host, port)

        # Select payload
        payload_data, is_binary = select_payload()
        print(f"\nSending to {host}:{port}...")
        if is_binary:
            print(f"Sending binary data ({len(payload_data)} bytes)")
        else:
            print(f"Sending Lua script")

        send_payload(payload_data, host, port)

        again = input("\nSend another payload? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!")
            break

# Main

def main():
    if len(sys.argv) > 1:
        host = None
        port = None
        payload_arg = None

        arg = sys.argv[1]
        if ':' in arg:
            parts = arg.split(':', 1)
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                print(f"Invalid port in '{arg}', using default {DEFAULT_PORT}")
        else:
            host = arg

        if len(sys.argv) >= 3:
            payload_arg = sys.argv[2]

        if len(sys.argv) >= 4 and port is None:
            if payload_arg is None:
                payload_arg = sys.argv[2]
            if sys.argv[3].isdigit():
                port = int(sys.argv[3])

        # Determine host
        if host is None:
            if DEFAULT_ROUTER_IP.strip():
                host = DEFAULT_ROUTER_IP.strip()
            else:
                host = get_router_ip()
                if not host:
                    host = get_router_ip_interactive()

        if port is None:
            port = DEFAULT_PORT

        # Determine payload
        if payload_arg is None:
            print("No payload specified. Using interactive selection.")
            payload_data, is_binary = select_payload()
        else:
            force_type = None
            if payload_arg.startswith('lua:'):
                force_type = 'lua'
                payload_arg = payload_arg[4:]
            elif payload_arg.startswith('bin:'):
                force_type = 'bin'
                payload_arg = payload_arg[4:]
            if payload_arg in LUA_PAYLOADS:
                payload_data = LUA_PAYLOADS[payload_arg]
                is_binary = False
                print(f"Using Lua payload '{payload_arg}'")
            elif payload_arg in BINARY_PAYLOADS:
                url = BINARY_PAYLOADS[payload_arg]
                print(f"Fetching binary from {url} ...")
                payload_data, is_binary = load_from_url(url, force_type='bin')
                if payload_data is None:
                    print("Failed to load binary. Exiting.")
                    sys.exit(1)
                print(f"Using binary payload '{payload_arg}'")
            elif is_url(payload_arg):
                print(f"Fetching from {payload_arg} ...")
                payload_data, is_binary = load_from_url(payload_arg, force_type)
                if payload_data is None:
                    print("Failed to load from URL. Exiting.")
                    sys.exit(1)
                print("Using payload from URL")
            else:
                print(f"Unknown payload '{payload_arg}'.")
                show_available_payloads()
                payload_data, is_binary = select_payload()

        
        send_payload(payload_data, host, port)

    else:
        interactive_loop()

if __name__ == "__main__":
    main()
