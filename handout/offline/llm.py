"""
LLM abstraction with three-tier offline fallback.

Tier 1: API (Anthropic Claude) — best quality, requires wifi
Tier 2: Local Ollama (llama3.1:8b) — slower, offline-capable
Tier 3: Cached responses keyed by input hash — instant, deterministic

Fallback is automatic. A status indicator shows which tier is active.
"""

import hashlib
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Status tracking — visible to UI and terminal
_current_tier = None
_tier_history = []


def get_current_tier():
    return _current_tier


def get_tier_history():
    return list(_tier_history)


def _cache_key(prompt, system=""):
    """Deterministic hash for caching."""
    content = f"{system}|||{prompt}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _load_cache(key):
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)["response"]
    return None


def _save_cache(key, response, tier_used):
    path = CACHE_DIR / f"{key}.json"
    with open(path, "w") as f:
        json.dump({"response": response, "tier": tier_used, "key": key}, f, indent=2)


def _try_api(prompt, system=""):
    """Tier 1: API call to Anthropic Claude."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None

    try:
        body = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 2048,
            "system": system or "You are a helpful assistant for a debt collection compliance system.",
            "messages": [{"role": "user", "content": prompt}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"]
    except Exception:
        return None


def _try_ollama(prompt, system=""):
    """Tier 2: Local Ollama model."""
    try:
        body = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "system": system or "You are a helpful assistant for a debt collection compliance system.",
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 1024}
        }).encode()

        req = urllib.request.Request(
            OLLAMA_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data.get("response", "")
    except Exception:
        return None


def generate(prompt, system="", use_cache=True, force_tier=None):
    """
    Generate text with automatic tier fallback.

    Returns (response_text, tier_used) tuple.
    tier_used is one of: "api", "ollama", "cache", "failed"
    """
    global _current_tier

    key = _cache_key(prompt, system)

    # If forcing a specific tier
    if force_tier == "api":
        result = _try_api(prompt, system)
        if result:
            _current_tier = "api"
            _tier_history.append("api")
            _save_cache(key, result, "api")
            return result, "api"
        return None, "failed"

    if force_tier == "ollama":
        result = _try_ollama(prompt, system)
        if result:
            _current_tier = "ollama"
            _tier_history.append("ollama")
            _save_cache(key, result, "ollama")
            return result, "ollama"
        return None, "failed"

    if force_tier == "cache":
        cached = _load_cache(key)
        if cached:
            _current_tier = "cache"
            _tier_history.append("cache")
            return cached, "cache"
        return None, "failed"

    # Normal fallback: API → Ollama → Cache
    # Tier 1: API
    result = _try_api(prompt, system)
    if result:
        _current_tier = "api"
        _tier_history.append("api")
        _save_cache(key, result, "api")
        return result, "api"

    # Tier 2: Ollama
    result = _try_ollama(prompt, system)
    if result:
        _current_tier = "ollama"
        _tier_history.append("ollama")
        _save_cache(key, result, "ollama")
        return result, "ollama"

    # Tier 3: Cache
    if use_cache:
        cached = _load_cache(key)
        if cached:
            _current_tier = "cache"
            _tier_history.append("cache")
            return cached, "cache"

    _current_tier = "failed"
    _tier_history.append("failed")
    return None, "failed"


def warm_cache(prompts_with_systems):
    """
    Pre-generate and cache responses for a list of (prompt, system) tuples.
    Used during rehearsal to build Tier 3 cache.
    """
    results = []
    for prompt, system in prompts_with_systems:
        response, tier = generate(prompt, system)
        results.append({"prompt_preview": prompt[:80], "tier": tier, "cached": response is not None})
        print(f"  Cached [{tier}]: {prompt[:60]}...")
    return results


def tier_status_line():
    """Human-readable status for terminal and UI."""
    tier = _current_tier or "not started"
    labels = {
        "api": "☁️  TIER 1 — Cloud API (best quality)",
        "ollama": "💻 TIER 2 — Local model (offline OK)",
        "cache": "📦 TIER 3 — Cached response (instant)",
        "failed": "❌ ALL TIERS FAILED",
        "not started": "⏳ Waiting..."
    }
    return labels.get(tier, tier)
