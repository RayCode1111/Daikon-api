#!/usr/bin/env python3
"""
colab_worker_runner.py
Autonomous vLLM worker runner for Google Colab.
- Serves Qwen2.5-7B-Instruct-AWQ via vLLM
- Exposes port 8000 via Cloudflare Tunnel
- Automatically registers endpoint with central API gateway
- Emits periodic heartbeats to maintain ONLINE routing status
"""

import sys
import os
import time
import json
import re
import signal
import subprocess
import urllib.request
import urllib.error

# Configurations
DEFAULT_PLATFORM_URL = "https://daikon-api.onrender.com"
DEFAULT_SECRET = "colab-worker-secret-key-123"
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct-AWQ"
SERVED_MODEL_NAME = "qwen2.5-7b"
WORKER_ID = "colab-t4-qwen2.5"
VLLM_PORT = 8000
HEARTBEAT_INTERVAL = 15  # seconds

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [ColabWorker] {msg}", flush=True)

def ensure_cloudflared():
    log("Checking cloudflared binary...")
    if os.path.exists("/usr/local/bin/cloudflared"):
        log("cloudflared is already installed at /usr/local/bin/cloudflared.")
        return

    log("Downloading cloudflared binary...")
    cmd = "curl -L --silent --output /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && chmod +x /usr/local/bin/cloudflared"
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to install cloudflared: {res.returncode}")
    log("cloudflared installed successfully to /usr/local/bin/cloudflared.")

def ensure_vllm():
    log("Checking vLLM installation...")
    try:
        import vllm
        log("vLLM is already installed.")
    except ImportError:
        log("vLLM not found on this VM. Installing vLLM (takes ~1-2 minutes)...")
        res = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "vllm"])
        if res.returncode != 0:
            raise RuntimeError(f"Failed to install vllm: exit code {res.returncode}")
        log("vLLM installed successfully.")

def start_vllm():
    log(f"Starting vLLM server for {MODEL_ID} on port {VLLM_PORT}...")
    vllm_cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL_ID,
        "--served-model-name", SERVED_MODEL_NAME,
        "--port", str(VLLM_PORT),
        "--dtype", "float16",
        "--gpu-memory-utilization", "0.85",
        "--max-model-len", "8192"
    ]
    
    log_file = open("/tmp/vllm.log", "w")
    proc = subprocess.Popen(vllm_cmd, stdout=log_file, stderr=subprocess.STDOUT)
    
    # Wait for vLLM to become healthy
    log("Waiting for vLLM to initialize weights and start HTTP server...")
    url = f"http://127.0.0.1:{VLLM_PORT}/v1/models"
    start_time = time.time()
    while True:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    log("vLLM OpenAI server is HEALTHY and accepting requests!")
                    break
        except Exception:
            pass

        if proc.poll() is not None:
            with open("/tmp/vllm.log") as f:
                err = f.read()
            raise RuntimeError(f"vLLM process died unexpectedly:\n{err[-2000:]}")

        if time.time() - start_time > 600:
            raise TimeoutError("vLLM startup timed out after 10 minutes.")

        time.sleep(5)
        if os.path.exists("/tmp/vllm.log"):
            try:
                with open("/tmp/vllm.log", "r") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                    if lines:
                        log(f"[vLLM] {lines[-1]}")
            except Exception:
                pass

    return proc

def start_tunnel():
    bin_path = "/usr/local/bin/cloudflared" if os.path.exists("/usr/local/bin/cloudflared") else "cloudflared"
    log(f"Launching Cloudflare Tunnel ({bin_path}) for port {VLLM_PORT}...")
    tunnel_cmd = [bin_path, "tunnel", "--url", f"http://127.0.0.1:{VLLM_PORT}"]
    tunnel_log = open("/tmp/tunnel.log", "w")
    proc = subprocess.Popen(tunnel_cmd, stdout=tunnel_log, stderr=subprocess.STDOUT)

    log("Extracting public trycloudflare.com URL...")
    start_time = time.time()
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    public_url = None

    while time.time() - start_time < 60:
        if os.path.exists("/tmp/tunnel.log"):
            with open("/tmp/tunnel.log", "r") as f:
                content = f.read()
                matches = url_pattern.findall(content)
                if matches:
                    public_url = matches[0]
                    break
        time.sleep(2)

    if not public_url:
        raise RuntimeError("Failed to obtain Cloudflare Tunnel URL within 60s.")

    log(f"Public Tunnel active at: {public_url}")
    return proc, public_url

def register(platform_url, secret, endpoint_url):
    log(f"Registering worker with central platform at {platform_url}...")
    register_url = f"{platform_url.rstrip('/')}/api/worker/register"
    payload = json.dumps({
        "worker_id": WORKER_ID,
        "model_name": SERVED_MODEL_NAME,
        "endpoint_url": endpoint_url,
        "secret": secret,
        "gpu_info": "Tesla T4 (15GB)"
    }).encode("utf-8")

    req = urllib.request.Request(
        register_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "1",
            "User-Agent": "ColabWorker/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read().decode())
        log(f"Registration response: {body}")
        if not body.get("success"):
            raise RuntimeError(f"Registration rejected: {body}")

def send_heartbeat(platform_url, secret):
    hb_url = f"{platform_url.rstrip('/')}/api/worker/heartbeat"
    payload = json.dumps({
        "worker_id": WORKER_ID,
        "secret": secret
    }).encode("utf-8")

    req = urllib.request.Request(
        hb_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "1",
            "User-Agent": "ColabWorker/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())

def main():
    platform_url = os.environ.get("PLATFORM_URL", DEFAULT_PLATFORM_URL).strip()
    secret = os.environ.get("WORKER_SECRET", DEFAULT_SECRET).strip()
    
    # Only parse if explicit flags are given
    if "--platform" in sys.argv:
        idx = sys.argv.index("--platform")
        if idx + 1 < len(sys.argv):
            platform_url = sys.argv[idx + 1].strip()
    if "--secret" in sys.argv:
        idx = sys.argv.index("--secret")
        if idx + 1 < len(sys.argv):
            secret = sys.argv[idx + 1].strip()

    if not platform_url.startswith("http://") and not platform_url.startswith("https://"):
        platform_url = f"https://{platform_url}"

    log(f"Starting Colab worker runner targeting platform: {platform_url} (secret length: {len(secret)})")

    # Clean up any lingering processes on port 8000
    subprocess.run("fuser -k 8000/tcp 2>/dev/null || true", shell=True)
    subprocess.run("killall -q -9 cloudflared 2>/dev/null || true", shell=True)

    ensure_cloudflared()
    ensure_vllm()
    vllm_proc = start_vllm()
    tunnel_proc, public_url = start_tunnel()

    try:
        register(platform_url, secret, public_url)
        log("Entering heartbeat loop (interval: 15s)...")
        while True:
            time.sleep(HEARTBEAT_INTERVAL)
            try:
                res = send_heartbeat(platform_url, secret)
                log(f"Heartbeat sent: {res.get('status')}")
            except Exception as e:
                log(f"Warning: Heartbeat failed: {e}")
                if "404" in str(e):
                    log("Platform restarted or session lost. Re-registering...")
                    try:
                        register(platform_url, secret, public_url)
                    except Exception as reg_err:
                        log(f"Re-registration attempt failed: {reg_err}")
    except KeyboardInterrupt:
        log("Shutting down worker gracefully...")
    finally:
        log("Terminating background tunnel and vLLM processes...")
        tunnel_proc.terminate()
        vllm_proc.terminate()

if __name__ == "__main__":
    main()

