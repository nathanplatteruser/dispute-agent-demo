#!/usr/bin/env python3
"""
Preflight check for the dispute-review demo.

Checks that required Python packages, sample data, and local model
availability (Ollama) are in place before the demo starts. Assumes a
standard Windows machine with adequate RAM and disk space, this script
does not check hardware specs; if a machine can't run the installed
dependencies, that's resolved before demo day, not by this script.

Run with:
    python scripts/preflight_check.py
"""

import importlib
import os
import subprocess
import sys

REQUIRED_PACKAGES = ["pandas"]  # extend this list to match your actual requirements.txt
REQUIRED_DATA_DIRS = ["data/sample_disputes", "data/mock_reference_data"]
OLLAMA_MODEL = "llama3.1:8b"

CHECK = "[OK]"
WARN = "[WARN]"
FAIL = "[FAIL]"


def check_packages():
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if not missing:
        print(f"{CHECK} Required Python packages present: {', '.join(REQUIRED_PACKAGES)}")
    else:
        print(f"{FAIL} Missing packages: {', '.join(missing)}. "
              f"Run: pip install -r requirements.txt")


def check_data_files():
    for d in REQUIRED_DATA_DIRS:
        if os.path.isdir(d) and any(os.scandir(d)):
            print(f"{CHECK} Data present: {d}")
        else:
            print(f"{WARN} No files found in {d}. Add sample data before "
                  f"running the live demo.")


def check_ollama():
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print(f"{WARN} Ollama installed but 'ollama list' failed. "
                  f"Local-model fallback (Tier 2) may not work.")
            return
        if OLLAMA_MODEL in result.stdout:
            print(f"{CHECK} Local model available: {OLLAMA_MODEL}")
        else:
            print(f"{WARN} Model '{OLLAMA_MODEL}' not found locally. "
                  f"Run: ollama pull {OLLAMA_MODEL} while you still have "
                  f"internet access.")
    except FileNotFoundError:
        print(f"{WARN} Ollama not found on PATH. Tier 2 (local model) "
              f"fallback will not be available if the cloud tier fails.")
    except Exception as e:
        print(f"{WARN} Could not check Ollama: {e}")


def main():
    print("Running preflight check...\n")
    check_packages()
    check_data_files()
    check_ollama()
    print("\nPreflight check complete. Review any [WARN] or [FAIL] lines "
          "above before running the live demo.")


if __name__ == "__main__":
    sys.exit(main())
