"""
EgyDevTeam EMU Log Listener

- Untested
"""

import socket
import sys
import time

DEFAULT_IP = "" # << ip here 
PORT = 9027
BUFFER_SIZE = 4096

def main():
    listen_ip = DEFAULT_IP

    # Allow custom IP
    if len(sys.argv) > 1:
        listen_ip = sys.argv[1]

    print("EgyDevTeam UDP Log Listener")
    print(f"  Protocol : UDP")
    print(f"  Bind     : {listen_ip}:{PORT}")
    print("  Waiting for logs...\n")

    # UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((listen_ip, PORT))
    except OSError as e:
        print(f"[ERROR] Bind failed: {e}")
        print("Use 0.0.0.0 or your real local IP")
        return

    count = 0
    start = time.time()

    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)  # UDP receive
            count += 1

            msg = data.decode(errors="ignore")
            elapsed = time.time() - start

            print(f"[{count:05d}] {addr[0]}:{addr[1]} | {elapsed:6.1f}s | {msg}", end="")

    except KeyboardInterrupt:
        print("\nStopping listener...")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
