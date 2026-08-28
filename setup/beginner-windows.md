# Beginner Setup Guide: Windows

**Do this BEFORE the demo session.** Every download in here can take a while
depending on your internet, do it the night before, not while everyone's
waiting on you live.

No prior coding experience needed. Just copy each command exactly as shown
and press Enter. Assumes a standard Windows machine, if you install
everything below and it runs, you're set.

---

## Checklist (check these off as you go)

- [ ] Step 1: Install Python
- [ ] Step 2: Install Git
- [ ] Step 3: Install Ollama
- [ ] Step 4: Download the AI model (this is the big download, do it early)
- [ ] Step 5: Download this project
- [ ] Step 6: Set up the project
- [ ] Step 7: Run the readiness check
- [ ] Step 8: You're done

---

## Step 1: Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow "Download Python" button
3. Open the downloaded file to start installing
4. **Important:** on the very first install screen, check the box at the
   bottom that says **"Add python.exe to PATH"** before clicking Install.
   This step is easy to miss and everything else breaks without it.
5. Click "Install Now" and wait for it to finish
6. Confirm it worked, press the **Windows key**, type `cmd`, press Enter to
   open Command Prompt, then paste:

```
python --version
```

You should see something like `Python 3.12.x`. If you instead see an error,
close Command Prompt completely, reopen it, and try again. Windows
sometimes needs a fresh window to pick up the PATH change.

---

## Step 2: Install Git

1. Go to [git-scm.com/downloads](https://git-scm.com/downloads)
2. Download the Windows version
3. Open the installer and click "Next" through every screen, the defaults
   are all fine, you don't need to change anything
4. Confirm it worked:

```
git --version
```

You should see something like `git version 2.4x.x`.

---

## Step 3: Install Ollama

Ollama is the program that runs the AI model on your own machine, without
needing the internet once it's set up.

1. Go to [ollama.com/download](https://ollama.com/download)
2. Download the Windows version and run the installer
3. Click through the install screens with defaults
4. Confirm it worked:

```
ollama --version
```

---

## Step 4: Download the AI model (the big one, start this early)

This step downloads several gigabytes. Start it, then go do something else
for a while.

```
ollama pull llama3.1:8b
```

You'll see a progress bar. When it says "success," you're done. Confirm it's
there:

```
ollama list
```

You should see `llama3.1:8b` in the list.

---

## Step 5: Download this project

1. Pick a simple location, like your Desktop. In Command Prompt:

```
cd Desktop
git clone https://github.com/YOUR-GITHUB-USERNAME/dispute-agent-demo.git
cd dispute-agent-demo
```

This creates a folder called `dispute-agent-demo` on your Desktop with
everything in it.

---

## Step 6: Set up the project

1. Create an isolated workspace for this project (this keeps it from messing
   with anything else on your computer):

```
python -m venv venv
```

2. Turn it on:

```
venv\Scripts\activate.bat
```

Your Command Prompt line should now start with `(venv)`, that means it
worked.

3. Install what the project needs:

```
pip install -r requirements.txt
```

This will take a minute or two.

---

## Step 7: Run the readiness check

This confirms everything above actually worked before demo day:

```
python scripts\preflight_check.py
```

You'll see a list of checks. Look for:

- `[OK]`, good, nothing to do
- `[WARN]`, worth a look, but not necessarily broken
- `[FAIL]`, needs fixing before the demo; see `setup/troubleshooting.md`

---

## Step 8: You're done

Close Command Prompt if you want, everything is saved. On demo day, all you
need to do is:

1. Open Command Prompt
2. `cd Desktop\dispute-agent-demo`
3. `venv\Scripts\activate.bat`
4. Follow `docs/participant-handout.md` from Step 6 onward, no more
   downloading or installing needed.

---

## If something goes wrong

Check `setup/troubleshooting.md` first. If it's not covered there, note
exactly what command you ran and exactly what error message you got ,
that's the fastest way for someone to help you fix it.
