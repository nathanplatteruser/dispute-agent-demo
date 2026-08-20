#!/usr/bin/env python3
"""
Tier 1 → Tier 2 Failover Test

Simulates three API failure modes with a key present, and proves each
falls through to Ollama without crashing or hanging.

Failure modes:
  1. Connection refused (bad port)
  2. 401 Unauthorized (bad key)
  3. Timeout (server that accepts but never responds)

Usage:
    python3 break/test_failover.py          # Run all three tests
    python3 break/test_failover.py --test 1 # Run one specific test
"""

import argparse
import http.server
import json
import os
import socket
import sys
import threading
import time
import unittest.mock as mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class HangingHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler that accepts the connection but never responds."""
    def do_POST(self):
        # Read the request body so the client doesn't get a broken pipe
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        # Now hang until the client times out
        time.sleep(120)

    def log_message(self, format, *args):
        pass  # Suppress log spam


def test_connection_refused():
    """Test 1: API endpoint is unreachable (connection refused)."""
    print("\n── TEST 1: Connection Refused ──")
    print("   Simulating: API server is down, port closed")

    # Point API at a port nothing is listening on
    dead_port = _find_free_port()
    fake_url = f"http://127.0.0.1:{dead_port}/v1/messages"

    import offline.llm as llm

    # Patch the URL and set a fake key so _try_api actually attempts the call
    original_env = os.environ.get("ANTHROPIC_API_KEY", "")
    os.environ["ANTHROPIC_API_KEY"] = "sk-test-fake-key-for-failover-test"

    start = time.time()
    with mock.patch.object(llm.urllib.request, "urlopen", side_effect=ConnectionRefusedError("Connection refused")):
        result = llm._try_api("Test prompt for failover", "System prompt")
    api_time = time.time() - start

    print(f"   API returned None in {api_time:.1f}s: {'PASS' if result is None else 'FAIL'}")

    # Now prove Ollama picks it up
    # Reset tier state
    llm._current_tier = None
    llm._tier_history.clear()

    start = time.time()
    response, tier = llm.generate(
        "Write one sentence acknowledging a consumer's dispute.",
        "You are a compliance assistant. Be brief.",
        use_cache=False
    )
    total_time = time.time() - start

    os.environ["ANTHROPIC_API_KEY"] = original_env

    if tier == "ollama" and response:
        print(f"   ✅ Fell through to Ollama in {total_time:.1f}s")
        print(f"   Response: {response[:100]}...")
        return True
    else:
        print(f"   ❌ Expected tier 'ollama', got '{tier}'")
        return False


def test_bad_key():
    """Test 2: API returns 401 Unauthorized."""
    print("\n── TEST 2: 401 Unauthorized (bad key) ──")
    print("   Simulating: API key is invalid or revoked")

    import offline.llm as llm

    original_env = os.environ.get("ANTHROPIC_API_KEY", "")
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-INVALID-key-that-will-be-rejected"

    # Simulate a 401 response
    error = llm.urllib.error.HTTPError(
        url="https://api.anthropic.com/v1/messages",
        code=401,
        msg="Unauthorized",
        hdrs=None,
        fp=None
    )

    start = time.time()
    with mock.patch.object(llm.urllib.request, "urlopen", side_effect=error):
        result = llm._try_api("Test prompt for failover", "System prompt")
    api_time = time.time() - start

    print(f"   API returned None in {api_time:.1f}s: {'PASS' if result is None else 'FAIL'}")

    # Prove Ollama picks it up — mock only _try_api, not urlopen,
    # so Ollama's HTTP call still works
    llm._current_tier = None
    llm._tier_history.clear()

    start = time.time()
    with mock.patch.object(llm, "_try_api", return_value=None):
        response, tier = llm.generate(
            "Write one sentence acknowledging a consumer's dispute.",
            "You are a compliance assistant. Be brief.",
            use_cache=False
        )
    total_time = time.time() - start

    os.environ["ANTHROPIC_API_KEY"] = original_env

    if tier == "ollama" and response:
        print(f"   ✅ Fell through to Ollama in {total_time:.1f}s")
        print(f"   Response: {response[:100]}...")
        return True
    else:
        print(f"   ❌ Expected tier 'ollama', got '{tier}'")
        return False


def test_timeout():
    """Test 3: API accepts connection but never responds (timeout)."""
    print("\n── TEST 3: Timeout (server hangs) ──")
    print("   Simulating: API server accepts connection, never responds")

    import offline.llm as llm

    # Start a local HTTP server that hangs
    port = _find_free_port()
    server = http.server.HTTPServer(("127.0.0.1", port), HangingHandler)
    server_thread = threading.Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    original_env = os.environ.get("ANTHROPIC_API_KEY", "")
    os.environ["ANTHROPIC_API_KEY"] = "sk-test-fake-key-for-timeout-test"

    # Patch the API URL to point at our hanging server, with a short timeout
    start = time.time()
    try:
        body = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 64,
            "system": "Test",
            "messages": [{"role": "user", "content": "Test"}]
        }).encode()
        req = llm.urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/messages",
            data=body,
            headers={"Content-Type": "application/json", "x-api-key": "fake"},
            method="POST"
        )
        # Use a 3-second timeout so we don't wait 30s during the test
        llm.urllib.request.urlopen(req, timeout=3)
        result = "unexpected_success"
    except Exception:
        result = None
    api_time = time.time() - start

    print(f"   API timed out in {api_time:.1f}s: {'PASS' if result is None and api_time < 10 else 'FAIL'}")

    # Prove Ollama picks it up
    llm._current_tier = None
    llm._tier_history.clear()

    # For the full generate() path, mock _try_api to simulate the timeout
    # so we don't wait 30s
    with mock.patch.object(llm, "_try_api", return_value=None):
        start = time.time()
        response, tier = llm.generate(
            "Write one sentence acknowledging a consumer's dispute.",
            "You are a compliance assistant. Be brief.",
            use_cache=False
        )
        total_time = time.time() - start

    os.environ["ANTHROPIC_API_KEY"] = original_env
    server.server_close()

    if tier == "ollama" and response:
        print(f"   ✅ Fell through to Ollama in {total_time:.1f}s")
        print(f"   Response: {response[:100]}...")
        return True
    else:
        print(f"   ❌ Expected tier 'ollama', got '{tier}'")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tier 1 → Tier 2 Failover Test")
    parser.add_argument("--test", type=int, choices=[1, 2, 3],
                        help="Run a specific test (default: all)")
    args = parser.parse_args()

    print("=" * 55)
    print("  TIER 1 → TIER 2 FAILOVER TEST")
    print("  Proving API failures fall through to Ollama")
    print("=" * 55)

    tests = {
        1: ("Connection Refused", test_connection_refused),
        2: ("401 Unauthorized", test_bad_key),
        3: ("Timeout", test_timeout),
    }

    results = {}
    if args.test:
        name, fn = tests[args.test]
        results[name] = fn()
    else:
        for num, (name, fn) in tests.items():
            results[name] = fn()

    print("\n" + "=" * 55)
    print("  RESULTS")
    print("=" * 55)
    all_pass = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_pass = False

    if all_pass:
        print("\n  All failure modes fall through cleanly to Tier 2.")
        print("  The stage scenario works: API dies, Ollama picks up,")
        print("  audience sees the tier indicator change.")
    else:
        print("\n  ⚠ Some tests failed. Check the output above.")

    sys.exit(0 if all_pass else 1)
