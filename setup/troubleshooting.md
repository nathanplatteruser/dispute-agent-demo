# Troubleshooting

Assumes a standard Windows machine with adequate specs to run the installed
dependencies. If a machine can't run them, that's a hardware issue to
resolve before demo day, not something these steps work around.

## Missing dependencies

Re-run `pip install -r requirements.txt` inside the activated virtual
environment. Confirm the venv is active, your terminal prompt should show
`(venv)`.

## Model / download failures

Confirm `ollama pull llama3.1:8b` completed successfully before going
air-gapped. Run `ollama list` to confirm the model is present locally.

## Windows permissions

If scripts are blocked, see the PowerShell execution-policy note in
`setup/windows.md`.

## Slow processing

The 20-document live run should complete well within the demo window on a
16 GB machine. If it's unexpectedly slow, confirm you're not accidentally
running on the cloud tier over a poor Wi-Fi connection, fall back to the
local model tier deliberately if needed.

## No internet / air-gapped setup

Everything after initial setup (dependency install, model pull) is designed
to run without internet access. If you're demoing air-gapped, complete all
setup steps and the preflight check while still connected, then disconnect.
