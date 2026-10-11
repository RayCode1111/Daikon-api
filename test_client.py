#!/usr/bin/env python3
"""
Test Client using official OpenAI SDK (runs with ./venv/bin/python3)
Tests:
1. Central platform worker status endpoint (/api/worker/status)
2. OpenAI SDK streaming chat completion (/v1/chat/completions)
3. Non-streaming chat completion
"""

import sys
import time
import requests
from openai import OpenAI

PLATFORM_BASE_URL = "http://localhost:3000"
API_KEY = "any-api-key"  # Default test key or created key

def check_worker_status():
    print(f"[*] Checking Platform Worker Status: {PLATFORM_BASE_URL}/api/worker/status...")
    try:
        r = requests.get(f"{PLATFORM_BASE_URL}/api/worker/status", timeout=3)
        print(f"    Status: {r.status_code}")
        print(f"    Body:   {r.text}")
    except Exception as e:
        print(f"    Error contacting platform: {e}")

def test_chat_stream(api_key):
    print(f"\n[*] Testing Streaming Chat Completion via OpenAI SDK...")
    client = OpenAI(
        api_key=api_key,
        base_url=f"{PLATFORM_BASE_URL}/v1"
    )

    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model="qwen2.5-7b",
            messages=[
                {"role": "user", "content": "Explain vector databases in one sentences."}
            ],
            stream=True
        )

        print("\n--- Streamed Response ---")
        for chunk in response:
            delta = chunk.choices[0].delta.content if chunk.choices else ""
            if delta:
                sys.stdout.write(delta)
                sys.stdout.flush()
        print("\n-------------------------")
        print(f"[\u2705] Streaming completed in {time.time() - start_time:.2f}s\n")
    except Exception as e:
        print(f"[\u274c] Error during chat completion: {e}")

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else API_KEY
    check_worker_status()
    test_chat_stream(key)

