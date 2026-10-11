#!/usr/bin/env python3
import time
import sys
from pyngrok import ngrok

def main():
    print("[*] Starting ngrok tunnel for port 3000...", flush=True)
    tunnel = ngrok.connect(3000, "http")
    print(f"[*] NGROK_PUBLIC_URL: {tunnel.public_url}", flush=True)
    try:
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        print("[*] Stopping ngrok tunnel...", flush=True)
        ngrok.disconnect(tunnel.public_url)
        ngrok.kill()

if __name__ == "__main__":
    main()

