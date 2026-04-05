"""
EgyDevTeam NES Launcher iPhone Port

Set DEFAULT_PS5_IP below and run it, it’ll do the job.
"""

import socket
import os
import time
import sys
from ftplib import FTP

# ========== CONFIGURE THESE ==========
DEFAULT_PS5_IP = "192.168.10.248"   # <<< change it to your PS4/PS5 IP
DEFAULT_ROMS_DIR = "roms"   # <<< Needs to be .nes, put them all into the roms folder
DEFAULT_LAUNCHER = "nes.lua"   # Lua payload file to load
PAYLOAD_PORT = 9026
FTP_PORT = 1337
# =====================================

# File search
def find_file(name, subdirs=["payloads", "lua"]):
    """Look for file in current folder.."""
    if os.path.exists(name) and os.path.isfile(name):
        return name
    candidates = [os.path.join(".", name)]
    for sub in subdirs:
        candidates.append(os.path.join(".", sub, name))
    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            return cand
    return None

def load_binary_file(filepath):
    """Read any file as bytes."""
    path = find_file(filepath)
    if not path:
        print(f"File not found: {filepath}")
        print(f"  Looked in: current folder, ./payloads/, ./lua/")
        return None
    try:
        with open(path, 'rb') as f:
            data = f.read()
        print(f"Loaded {os.path.basename(path)} ({len(data):,} bytes)")
        return data
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

# Network functions
def send_payload(host, filepath):
    """Send raw file bytes to PS5 payload port."""
    data = load_binary_file(filepath)
    if data is None:
        return False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect((host, PAYLOAD_PORT))
        sock.sendall(data)
        print(f"  Sent {os.path.basename(filepath)} ({len(data):,} bytes)")
        return True
    except Exception as e:
        print(f"Send error: {e}")
        return False
    finally:
        sock.close()

def wait_for_ftp(host, port, timeout=50):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        banner = s.recv(256)
        s.close()
        return b'220' in banner
    except:
        try:
            s.close()
        except:
            pass
        return False

def send_site_exit(host, port):
    try:
        ftp = FTP()
        ftp.connect(host, port, timeout=10)
        ftp.login('anonymous', '')
        ftp.sendcmd('SITE EXIT')
        ftp.quit()
        print("  FTP server released")
    except Exception as e:
        print(f"  [WARN] Could not release FTP: {e}")

def upload_roms(host, roms, port=FTP_PORT):
    total = len(roms)
    total_size = sum(os.path.getsize(r) for r in roms)
    print(f"  {total} files ({total_size / 1048576:.1f} MB)")

    ftp = FTP()
    ftp.connect(host, port, timeout=15)
    ftp.login('anonymous', '')
    ftp.sendcmd('TYPE I')

    existing = set()
    try:
        existing = set(ftp.nlst())
    except:
        pass

    # count actual uploads
    to_upload = 0
    for rom_path in roms:
        fn = os.path.basename(rom_path)
        sz = os.path.getsize(rom_path)
        if fn in existing:
            try:
                if ftp.size(fn) == sz:
                    continue
            except:
                pass
        to_upload += 1

    try:
        ftp.sendcmd(f'SITE TOTAL {to_upload}')
    except:
        pass

    uploaded = 0
    skipped = 0
    bytes_sent = 0
    t0 = time.time()

    for i, rom_path in enumerate(roms, 1):
        fn = os.path.basename(rom_path)
        sz = os.path.getsize(rom_path)

        if fn in existing:
            try:
                if ftp.size(fn) == sz:
                    skipped += 1
                    if skipped % 50 == 0 or i == total:
                        print(f"  [{i*100//total:3d}%] Skipped {fn}")
                    continue
            except:
                pass

        try:
            with open(rom_path, 'rb') as f:
                ftp.storbinary(f'STOR {fn}', f, blocksize=8192)
            uploaded += 1
            bytes_sent += sz
        except Exception as e:
            print(f"  [ERR] {fn}: {e}")
            continue

        if uploaded <= 5 or uploaded == to_upload or uploaded % 25 == 0:
            elapsed = time.time() - t0
            speed = bytes_sent / elapsed / 1024 if elapsed > 0 else 0
            pct = i * 100 // total
            print(f"  {pct:3d}% | {uploaded}/{to_upload} | {speed:.0f} KB/s | {fn}")

    elapsed = time.time() - t0
    print(f"  Done: {uploaded} uploaded, {skipped} skipped "
          f"({bytes_sent / 1048576:.1f} MB in {elapsed:.1f}s)")

    try:
        ftp.sendcmd('SITE EXIT')
    except:
        pass
    try:
        ftp.quit()
    except:
        pass

# ROM scanning
def scan_roms(roms_dir, extensions):
    if not os.path.isdir(roms_dir):
        return []
    return sorted([
        os.path.join(roms_dir, f) for f in os.listdir(roms_dir)
        if os.path.splitext(f)[1].lower() in extensions
        and os.path.isfile(os.path.join(roms_dir, f))
    ])

# Main
def main():
    # Parse arguments manually
    ps5_ip = DEFAULT_PS5_IP
    roms_dir = DEFAULT_ROMS_DIR
    launcher = DEFAULT_LAUNCHER
    skip_upload = False
    extensions = {'.nes'}
    ftp_wait = 10

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--roms-dir' and i+1 < len(sys.argv):
            roms_dir = sys.argv[i+1]
            i += 2
        elif arg == '--launcher' and i+1 < len(sys.argv):
            launcher = sys.argv[i+1]
            i += 2
        elif arg == '--skip-upload':
            skip_upload = True
            i += 1
        elif arg == '--ext' and i+1 < len(sys.argv):
            extensions = set(e if e.startswith('.') else '.'+e for e in sys.argv[i+1].split(','))
            i += 2
        elif arg == '--ftp-wait' and i+1 < len(sys.argv):
            ftp_wait = int(sys.argv[i+1])
            i += 2
        elif not arg.startswith('--'):
            ps5_ip = arg
            i += 1
        else:
            print(f"Unknown argument: {arg}")
            i += 1

    # Resolve paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(roms_dir):
        roms_dir = os.path.join(script_dir, roms_dir)
    if not os.path.isabs(launcher):
        launcher = os.path.join(script_dir, launcher)

    print(f"EgyDevTeam NES Launcher (iPhone)")
    print(f"  PS4/PS5: {ps5_ip}  ROMs: {roms_dir}")
    print()

    roms = []
    if not skip_upload:
        print("[1] Scanning ROMs...")
        roms = scan_roms(roms_dir, extensions)
        if not roms:
            print(f"  No ROMs found in {roms_dir}")
            print(f"  Will launch emulator without uploading.")
        else:
            print(f"  Found {len(roms)} ROM(s)")
        print()

    print("[2] Launching emulator...")
    if not send_payload(ps5_ip, launcher):
        print("  Failed to send launcher. Exiting.")
        return
    print()

    print(f"[3] Waiting for FTP server on PS4/PS5...")
    
    # --- RETRY LOGIC (first attempt) ---
    ftp_ready = wait_for_ftp(ps5_ip, FTP_PORT, ftp_wait)
    if not ftp_ready:
        print(f"  FTP server not ready yet, retrying in 1 second...")
        time.sleep(1)
        ftp_ready = wait_for_ftp(ps5_ip, FTP_PORT, ftp_wait)
        if not ftp_ready:
            print(f"  FTP server still not responding after second attempt.")
            print(f"  You may need to run the script again.")
    
    if ftp_ready:
        print(f"  FTP server ready")
        if roms and not skip_upload:
            print()
            print("[4] Uploading ROMs...")
            try:
                upload_roms(ps5_ip, roms)
            except Exception as e:
                print(f"  FTP error: {e}")
                send_site_exit(ps5_ip, FTP_PORT)
        else:
            print("  Releasing FTP server...")
            send_site_exit(ps5_ip, FTP_PORT)
    else:
        # If still not ready after retries, just skip upload/release
        print("  Skipping FTP operations.")
    
    print("Done!")

if __name__ == '__main__':
    main()
