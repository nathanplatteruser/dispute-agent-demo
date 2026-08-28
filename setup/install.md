# Setup: All Platforms

Assumes a standard Windows machine. This guide walks through installing
everything needed; it doesn't check hardware specs along the way.

## 1. Prerequisites

- Python 3.10 or later
- Git

## 2. Clone the repository

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/dispute-agent-demo.git
cd dispute-agent-demo
```

## 3. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

- Mac/Linux: `source venv/bin/activate`
- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- Windows (cmd): `venv\Scripts\activate.bat`

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Local model setup (air-gapped fallback path)

The demo is designed to run on a tiered failover:

1. Cloud model (primary)
2. Local model via Ollama, llama3.1:8b (fallback if no internet)
3. Cached responses (fallback if the local model also fails)

Install Ollama and pull the model ahead of time so it's cached locally:

```bash
ollama pull llama3.1:8b
```

## 6. Confirm sample data is present

```bash
ls data/sample_disputes
ls data/mock_reference_data
```

## 7. Run the preflight check

```bash
python scripts/preflight_check.py
```

This checks required dependencies, presence of the sample data files, and
whether the local model is available, before you're standing in front of a
room.

## 8. Run the demo

See `docs/participant-handout.md` for the run sequence.
