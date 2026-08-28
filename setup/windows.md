# Windows Setup Notes

Tested target: standard Windows 10/11 machine.

1. Install Python 3.10+ from python.org, check "Add Python to PATH" during
   install.
2. Install Git for Windows.
3. Open PowerShell, then follow `setup/install.md` from Step 2.
4. If PowerShell blocks the venv activation script, run PowerShell as
   Administrator once and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then retry `venv\Scripts\Activate.ps1`.

5. If pip install fails on a package needing a compiler, install
   "Desktop development with C++" via the Visual Studio Build Tools
   installer, then retry.
