# Participant Handout: Dispute Response Demo

## 1. What you will build

A prototype dispute-review workflow: classify a batch of fictional disputes,
check factual claims against mock reference data, flag what's factually
incorrect, draft a response, and route it through human sign-off.

## 2. What this is not

- Not production automation
- Not legal advice
- Not approved for real consumer data
- Not a substitute for security, compliance, or legal review

## 3. Before you start (machine)

- Standard Windows machine
- Internet connection for initial setup only, the demo itself is designed to
  run air-gapped once dependencies are installed

**First time setting up a machine like this?** Skip straight to
`setup/beginner-windows.md`. It walks through every install step (Python,
Git, Ollama, the model download) with no assumed experience. Do this the
night before, not on demo day.

## 4. Before you start

1. Clone the repository (see command below)
2. Confirm required software is installed, run `setup/install.md` checklist
3. Download any local model / dependencies (see `setup/install.md`)
4. Confirm sample data is present in `data/sample_disputes/`
5. Run the preflight check: `python scripts/preflight_check.py`

## 5. Clone the repository

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/dispute-agent-demo.git
cd dispute-agent-demo
```

## 6. Run the demo

1. Start the application (see `setup/install.md` for the exact run command
   once your app entry point is in place)
2. Load the mock dataset from `data/sample_disputes/`
3. Run the review
4. Open the output report in `outputs/`
5. Review a drafted response
6. Apply human approval / redline / sign-off

## 7. Troubleshooting

See `setup/troubleshooting.md` for dependency, model-download, Windows
permission, slow-processing, and no-internet/air-gapped issues.
