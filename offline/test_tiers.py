#!/usr/bin/env python3
"""
Test all three offline tiers.

Usage:
    python3 offline/test_tiers.py              # Test whatever is available
    python3 offline/test_tiers.py --tier cache  # Test cache only (offline)
    python3 offline/test_tiers.py --tier ollama # Test Ollama only
    python3 offline/test_tiers.py --tier api    # Test API only
"""

import sys
import os
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from offline.llm import generate, tier_status_line, _load_cache, CACHE_DIR


def test_tier(tier_name=None):
    test_prompt = "Write a one-sentence dispute response acknowledging receipt of a consumer's identity theft claim."
    test_system = "You are a compliance letter drafter. Be brief."

    print(f"Testing: {tier_name or 'auto-fallback'}")
    print(f"Prompt: {test_prompt[:60]}...")

    response, tier = generate(test_prompt, test_system, force_tier=tier_name)

    if response:
        print(f"\n✅ Tier '{tier}' responded:")
        print(f"   {response[:200]}")
        print(f"   Status: {tier_status_line()}")
        return True
    else:
        print(f"\n❌ Tier '{tier_name or 'auto'}' failed")
        return False


def test_cache_integrity():
    """Check that cached responses exist and are readable."""
    cache_files = list(CACHE_DIR.glob("*.json"))
    print(f"\nCache directory: {CACHE_DIR}")
    print(f"Cached responses: {len(cache_files)}")

    if cache_files:
        import json
        for f in cache_files[:3]:
            with open(f) as fh:
                data = json.load(fh)
                print(f"  {f.name}: tier={data.get('tier', '?')}, response_len={len(data.get('response', ''))}")
        return True
    else:
        print("  ⚠ No cached responses. Run the pipeline once to populate the cache.")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=["api", "ollama", "cache", "all"], default="all")
    args = parser.parse_args()

    print("=" * 50)
    print("  OFFLINE TIER VERIFICATION")
    print("=" * 50)

    results = {}

    if args.tier in ("all", "cache"):
        print("\n--- TIER 3: CACHE ---")
        results["cache"] = test_cache_integrity()
        if results["cache"]:
            results["cache_response"] = test_tier("cache")

    if args.tier in ("all", "ollama"):
        print("\n--- TIER 2: OLLAMA ---")
        results["ollama"] = test_tier("ollama")

    if args.tier in ("all", "api"):
        print("\n--- TIER 1: API ---")
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if api_key:
            results["api"] = test_tier("api")
        else:
            print("  ⚠ No ANTHROPIC_API_KEY set. Skipping API test.")
            results["api"] = None

    if args.tier == "all":
        print("\n--- AUTO-FALLBACK ---")
        results["auto"] = test_tier(None)

    print("\n" + "=" * 50)
    print("  RESULTS")
    print("=" * 50)
    for k, v in results.items():
        status = "✅" if v else ("⚠ skipped" if v is None else "❌")
        print(f"  {k}: {status}")
