"""
Khedut AI (ખેડૂત AI) - 1-Click Full-Stack Application Launcher
=============================================================
Starts the complete real AI agricultural assistant backend:
- Two-Stage PyTorch Leaf Disease Vision Engine (Tomato, Chilli, Paddy, Wheat, Bt Cotton, Potato, Maize, Groundnut)
- SQLite Database for scan history & user crops
- Open-Meteo Agricultural Weather & Spray Advisories
- Agricultural Agronomist Chatbot
- APMC Mandi Market Prices

Provides 3 access URLs:
1. Localhost URL (for this PC)
2. Local Wi-Fi Network URL (for phones & devices on the same Wi-Fi)
3. Worldwide Public Internet URL (accessible from ANY phone or website in the world)
"""

import os
import sys
import re
import time
import socket
import atexit
import threading
import subprocess
import webbrowser
import urllib.request
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "Khedut_AI" / "backend"
CF_EXE = ROOT_DIR / "cloudflared.exe"

# Global subprocess handle for tunnel
tunnel_proc = None

def get_local_ip() -> str:
    """Detects this machine's local IPv4 address on the Wi-Fi/LAN network."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Checks whether the specified port is currently listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def wait_for_server(url: str, timeout_sec: int = 40) -> bool:
    """Polls the server health endpoint until it returns HTTP 200."""
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "KhedutLauncher/1.0"})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def cleanup_tunnel():
    """Ensures background cloudflared tunnel is cleanly terminated upon exit."""
    global tunnel_proc
    if tunnel_proc and tunnel_proc.poll() is None:
        try:
            tunnel_proc.terminate()
            tunnel_proc.wait(timeout=2)
        except Exception:
            tunnel_proc.kill()

atexit.register(cleanup_tunnel)

def start_public_tunnel(port: int = 8000) -> str:
    """Spawns Cloudflare Tunnel to expose the local server with a free public HTTPS URL."""
    global tunnel_proc
    if not CF_EXE.exists():
        return None

    try:
        cmd = [
            str(CF_EXE), "tunnel",
            "--url", f"http://127.0.0.1:{port}",
            "--http-host-header", f"127.0.0.1:{port}"
        ]
        tunnel_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Read lines looking for the trycloudflare URL
        start_time = time.time()
        while time.time() - start_time < 12:
            line = tunnel_proc.stdout.readline()
            if not line:
                break
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                return match.group(0)
    except Exception as e:
        print(f"[!] Note on public tunnel: {e}")
    return None

def main():
    print("=" * 72)
    print("        KHEDUT AI (ખેડૂત AI) - SMART FARMING ASSISTANT")
    print("=" * 72)
    print("[1/3] Preparing Python environment & PyTorch AI neural networks...")

    # Ensure backend directory is in sys.path
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))
    os.chdir(BACKEND_DIR)

    port = 8000
    local_ip = get_local_ip()
    local_url = f"http://localhost:{port}"
    wifi_url = f"http://{local_ip}:{port}"
    health_url = f"http://127.0.0.1:{port}/api/health"

    if is_port_in_use(port, "127.0.0.1"):
        print(f"[!] Port {port} is already active. Checking if Khedut AI is already running...")
        if wait_for_server(health_url, timeout_sec=2):
            print(f"[OK] Khedut AI is already online and healthy!")
            print(f"     Local URL:    {local_url}")
            print(f"     Wi-Fi URL:    {wifi_url}")
            webbrowser.open(local_url)
            print("\nPress Ctrl+C to close.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                return

    print("[2/3] Starting Khedut AI Server (Uvicorn + FastAPI + PyTorch Vision)...")
    print(f"      (Loading vision models: Tomato, Chilli, Rice, Wheat, Cotton, etc.)")

    # Background coordinator for tunnel and browser
    def post_startup():
        if wait_for_server(health_url, timeout_sec=40):
            # Start public HTTPS tunnel
            print("\n[+] Generating Worldwide Public URL via Cloudflare...")
            public_url = start_public_tunnel(port)

            print("\n" + "=" * 72)
            print("  SUCCESS: KHEDUT AI IS LIVE & READY ACROSS ALL NETWORKS! ")
            print("=" * 72)
            print(f"  💻 This PC:             {local_url}")
            print(f"  📱 Phone (Same Wi-Fi):  {wifi_url}")
            if public_url:
                print(f"  🌍 ANY PHONE / WEBSITE: {public_url}")
            print(f"  📚 API Documentation:   {local_url}/docs")
            print("=" * 72)
            if public_url:
                print(f"\n  👉 You can share this URL with ANYONE or open it on any mobile phone:")
                print(f"     {public_url}\n")
            
            # Open browser locally
            time.sleep(0.3)
            webbrowser.open(local_url)

    threading.Thread(target=post_startup, daemon=True).start()

    # Run Uvicorn listening on 0.0.0.0
    try:
        import uvicorn
        import main as backend_main
        # Binding to 0.0.0.0 allows connections from local network and tunnels
        uvicorn.run(backend_main.app, host="0.0.0.0", port=port, log_level="warning")
    except KeyboardInterrupt:
        print("\n[!] Shutting down Khedut AI Server. Goodbye!")
    finally:
        cleanup_tunnel()

if __name__ == "__main__":
    main()
