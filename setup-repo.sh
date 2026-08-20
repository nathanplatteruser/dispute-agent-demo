#!/usr/bin/env bash
# setup-repo.sh — one-time setup for the collections demo repo.
# Run from the root of the repo: bash setup-repo.sh

set -euo pipefail

echo "==> Creating directory structure"
mkdir -p pipeline ui break offline handout talk data/raw data/synth

echo "==> Writing .gitignore"
cat > .gitignore <<'EOF'
# Raw data NEVER gets committed. This is constraint #1.
data/raw/
*.csv.zip
complaints.csv

# Secrets
.env
.env.*
*.key
*.pem
credentials.json

# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/

# Node
node_modules/

# OS
.DS_Store

# Model caches
offline/cache/*.bin
EOF

echo "==> Installing pre-commit hook"
mkdir -p .git/hooks
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
# Blocks the two things that would end this project:
# real consumer data, and secrets.

set -uo pipefail
FAIL=0
FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$FILES" ]; then exit 0; fi

# 1. Block raw data files
for f in $FILES; do
  case "$f" in
    data/raw/*|*complaints.csv|*.csv.zip)
      echo "BLOCKED: $f looks like raw source data. Keep it in data/raw/ (ignored)."
      FAIL=1 ;;
  esac
done

# 2. Block oversized files (raw dumps sneaking in under another name)
for f in $FILES; do
  if [ -f "$f" ]; then
    SIZE=$(wc -c < "$f" | tr -d ' ')
    if [ "$SIZE" -gt 5242880 ]; then
      echo "BLOCKED: $f is over 5MB. If it's data, it belongs in data/raw/."
      FAIL=1
    fi
  fi
done

# 3. Scan for PII/PCI shapes and secrets
PATTERNS='[0-9]{3}-[0-9]{2}-[0-9]{4}|4[0-9]{15}|5[1-5][0-9]{14}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
for f in $FILES; do
  if [ -f "$f" ] && git diff --cached -- "$f" | grep -nEq "$PATTERNS"; then
    echo "BLOCKED: $f matches an SSN, card number, or credential pattern."
    FAIL=1
  fi
done

if [ "$FAIL" -ne 0 ]; then
  echo ""
  echo "Commit blocked. Constraint #1 of this project is no real consumer data."
  echo "If this is a false positive: git commit --no-verify"
  exit 1
fi
exit 0
EOF
chmod +x .git/hooks/pre-commit

echo "==> Seeding DECISIONS.md"
[ -f DECISIONS.md ] || cat > DECISIONS.md <<'EOF'
# Decisions

Judgment calls made during the build, with the alternative rejected.

| Date | Decision | Why | Rejected |
|------|----------|-----|----------|
EOF

echo ""
echo "Done. Structure created, .gitignore written, pre-commit hook armed."
echo ""
echo "Verify the hook works:"
echo "  echo '123-45-6789' > /tmp/t.txt && cp /tmp/t.txt ./test.txt"
echo "  git add test.txt && git commit -m 'test'   # should BLOCK"
echo "  rm test.txt"
