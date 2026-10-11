#!/usr/bin/env python3
"""
Mock vLLM Worker for Local Testing (Runs on localhost:8001)
Simulates a Google Colab vLLM server serving Qwen2.5-7B-Instruct.
Handles:
1. Local OpenAI-compatible /v1/models and /v1/chat/completions (streaming & non-streaming)
2. Auto-registration with Central Platform at http://localhost:3000/api/worker/register
3. Heartbeat pings every 15s to http://localhost:3000/api/worker/heartbeat
4. Clean deregistration on exit
"""

import sys
import time
import json
import uuid
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

WORKER_PORT = 8001
PLATFORM_URL = "http://localhost:3000"
WORKER_SECRET = "colab-worker-secret-key-123"
MODEL_NAME = "qwen2.5-7b"
WORKER_ID = f"local-mock-worker-{uuid.uuid4().hex[:6]}"

running = True

class MockVLLMHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[Mock vLLM :{WORKER_PORT}] {self.address_string()} - {format%args}\n")

    def do_GET(self):
        if self.path == "/v1/models" or self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {
                "object": "list",
                "data": [
                    {
                        "id": MODEL_NAME,
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": "vllm"
                    },
                    {
                        "id": "qwen2.5-7b-instruct",
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": "vllm"
                    }
                ]
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/v1/chat/completions":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            body = json.loads(post_data) if post_data else {}
            stream = body.get("stream", False)

            req_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
            created = int(time.time())

            mock_reply = "Hello from local simulated Qwen2.5-7B vLLM! Your API hosting platform is working perfectly."

            if stream:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()

                words = mock_reply.split(" ")
                for i, word in enumerate(words):
                    chunk = {
                        "id": req_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": MODEL_NAME,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": word + (" " if i < len(words) - 1 else "")},
                                "finish_reason": None
                            }
                        ]
                    }
                    self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    time.sleep(0.08)

                # Final chunk
                final_chunk = {
                    "id": req_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": MODEL_NAME,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 12,
                        "completion_tokens": len(words),
                        "total_tokens": 12 + len(words)
                    }
                }
                self.wfile.write(f"data: {json.dumps(final_chunk)}\n\n".encode("utf-8"))
                self.wfile.write(b"data: [DONE]\n\n")
                self.wfile.flush()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                resp = {
                    "id": req_id,
                    "object": "chat.completion",
                    "created": created,
                    "model": MODEL_NAME,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": mock_reply
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 12,
                        "completion_tokens": len(mock_reply.split()),
                        "total_tokens": 12 + len(mock_reply.split())
                    }
                }
                self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def heartbeat_loop():
    global running
    print(f"[*] Starting Heartbeat loop to {PLATFORM_URL}/api/worker/heartbeat every 15s...")
    while running:
        time.sleep(15)
        if not running:
            break
        try:
            r = requests.post(f"{PLATFORM_URL}/api/worker/heartbeat", json={
                "worker_id": WORKER_ID,
                "secret": WORKER_SECRET
            }, timeout=4)
            if r.status_code == 200:
                print(f"[Heartbeat] \u2705 Heartbeat accepted by platform at {time.strftime('%H:%M:%S')}")
            else:
                print(f"[Heartbeat] \u26a0\ufe0f Heartbeat response {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[Heartbeat] Error connecting to platform: {e}")

def main():
    global running
    server = HTTPServer(("0.0.0.0", WORKER_PORT), MockVLLMHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"[\u2705] Mock vLLM Server listening on http://localhost:{WORKER_PORT}")

    # Register with Central Platform
    reg_payload = {
        "worker_id": WORKER_ID,
        "model_name": MODEL_NAME,
        "endpoint_url": f"http://localhost:{WORKER_PORT}",
        "secret": WORKER_SECRET,
        "gpu_info": "Local Simulated Tesla T4"
    }

    print(f"[*] Registering worker with platform: {PLATFORM_URL}/api/worker/register...")
    try:
        r = requests.post(f"{PLATFORM_URL}/api/worker/register", json=reg_payload, timeout=5)
        print(f"[*] Registration response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[\u26a0\ufe0f] Could not connect to platform to register: {e}")
        print("    (Make sure New-API platform is running on port 3000)")

    hb_thread = threading.Thread(target=heartbeat_loop, daemon=True)
    hb_thread.start()

    print("\nPress Ctrl+C to stop the mock worker and deregister.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping mock worker...")
        running = False
        try:
            requests.post(f"{PLATFORM_URL}/api/worker/deregister", json={
                "worker_id": WORKER_ID,
                "secret": WORKER_SECRET
            }, timeout=3)
            print("[\u2705] Deregistered worker successfully.")
        except Exception:
            pass
        server.shutdown()
        print("Mock worker stopped.")

if __name__ == "__main__":
    main()

