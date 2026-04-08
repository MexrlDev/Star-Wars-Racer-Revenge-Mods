"""
EgyDevTeam NES ROM Uploader (iPhone Port)
Uploads ROMs to PS4/PS5 FTP server without sending the launcher.
"""

import socket
import os
import time
import sys
from ftplib import FTP

# ========== CONFIGURE THESE ==========
DEFAULT_PS5_IP = "192.168.10.248"   # Change to your PS4/PS5 IP
DEFAULT_ROMS_DIR = "roms"            # Folder containing .nes files
FTP_PORT = 1337
# =====================================

def wait_for_ftp(host, port, timeout=50):
    """Wait for FTP banner, return True if ready."""
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
    """Tell FTP server to close gracefully."""
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
    """Upload ROM files to FTP server."""
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

def scan_roms(roms_dir, extensions):
    """Find all ROM files with given extensions."""
    if not os.path.isdir(roms_dir):
        return []
    return sorted([
        os.path.join(roms_dir, f) for f in os.listdir(roms_dir)
        if os.path.splitext(f)[1].lower() in extensions
        and os.path.isfile(os.path.join(roms_dir, f))
    ])

def main():
    ps5_ip = DEFAULT_PS5_IP
    roms_dir = DEFAULT_ROMS_DIR
    extensions = {'.nes'}
    ftp_wait = 10
    skip_exit = False

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--roms-dir' and i+1 < len(sys.argv):
            roms_dir = sys.argv[i+1]
            i += 2
        elif arg == '--ext' and i+1 < len(sys.argv):
            extensions = set(e if e.startswith('.') else '.'+e for e in sys.argv[i+1].split(','))
            i += 2
        elif arg == '--ftp-wait' and i+1 < len(sys.argv):
            ftp_wait = int(sys.argv[i+1])
            i += 2
        elif arg == '--skip-exit':
            skip_exit = True
            i += 1
        elif not arg.startswith('--'):
            ps5_ip = arg
            i += 1
        else:
            print(f"Unknown argument: {arg}")
            i += 1

    script_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(roms_dir):
        roms_dir = os.path.join(script_dir, roms_dir)

    print(f"EgyDevTeam NES ROM Uploader")
    print(f"  PS4/PS5: {ps5_ip}  ROMs: {roms_dir}")
    print()

    print("[1] Scanning ROMs...")
    roms = scan_roms(roms_dir, extensions)
    if not roms:
        print(f"  No ROMs found in {roms_dir}")
        return
    print(f"  Found {len(roms)} ROM(s)")
    print()

    print(f"[2] Waiting for FTP server on PS4/PS5...")
    ftp_ready = wait_for_ftp(ps5_ip, FTP_PORT, ftp_wait)
    if not ftp_ready:
        print("  Retrying once more...")
        time.sleep(1)
        ftp_ready = wait_for_ftp(ps5_ip, FTP_PORT, ftp_wait)

    if not ftp_ready:
        print("  FTP server not responding. Is the emulator already running?")
        return

    print("  FTP server ready")
    print()
    print("[3] Uploading ROMs...")
    try:
        upload_roms(ps5_ip, roms)
    except Exception as e:
        print(f"  FTP error: {e}")
        if not skip_exit:
            send_site_exit(ps5_ip, FTP_PORT)
    else:
        if not skip_exit:
            print("  Releasing FTP server...")
            send_site_exit(ps5_ip, FTP_PORT)

    print("Done!")

if __name__ == '__main__':
    main()
