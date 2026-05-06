#!/usr/bin/env bash
# scholar-agent setup script
#
# Usage:
#   Standalone (global install):  bash setup.sh            (run from repo root)
#   Embedded (project-local):     cd my-project && bash path/to/scholar-agent/setup.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(pwd)"

# Detect mode: standalone (git checkout) vs embedded (subdirectory of another project)
if [ -d "$SCRIPT_DIR/.git" ] && [ "$SCRIPT_DIR" = "$VAULT_DIR" ]; then
  MODE="standalone"
else
  MODE="embedded"
fi

echo "=== Scholar Agent Setup ==="
echo "Mode: $MODE"
echo ""

# 0. Check system dependencies
echo "[0/4] Checking system dependencies..."

if command -v pdftotext &>/dev/null; then
  echo "  poppler: OK"
else
  echo "  poppler: NOT FOUND (optional, for PDF text extraction)"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "    Installing via Homebrew..."
    brew install poppler 2>/dev/null || echo "    (brew install poppler failed — install manually if needed)"
  elif command -v apt-get &>/dev/null; then
    echo "    Installing via apt..."
    sudo apt-get update -qq && sudo apt-get install -y -qq poppler-utils
  elif command -v dnf &>/dev/null; then
    echo "    Installing via dnf..."
    sudo dnf install -y poppler-utils
  else
    echo "    Install manually: brew install poppler | apt install poppler-utils"
  fi
fi

# 1. Install / update package
echo "[1/4] Installing scholar-agent..."
if [ "$MODE" = "standalone" ]; then
  # Standalone: install from source in editable mode
  pip install -e "$SCRIPT_DIR" 2>/dev/null || pip3 install -e "$SCRIPT_DIR"
  echo "  Installed in editable mode from source."
else
  # Embedded: install Python dependencies
  pip install "fastmcp>=2.0" "PyMuPDF>=1.24.0" "PyYAML>=6.0" "jsonschema>=4.23" 2>/dev/null \
    || pip3 install "fastmcp>=2.0" "PyMuPDF>=1.24.0" "PyYAML>=6.0" "jsonschema>=4.23"
  echo "  Installed Python dependencies."
fi

if [ "$MODE" = "standalone" ]; then
  # Standalone mode: use 'scholar-agent init'
  echo "[2/4] Running 'scholar-agent init'..."
  echo ""

  if command -v scholar-agent &>/dev/null; then
    scholar-agent init --format text
  else
    python -m scholar_agent.cli init --format text 2>/dev/null \
      || python3 -m scholar_agent.cli init --format text
  fi

  echo ""
  echo "[3/4] Setup complete!"

else
  # Embedded mode: traditional project-local setup
  echo "[2/4] Creating directories..."
  mkdir -p "$VAULT_DIR/knowledge"
  mkdir -p "$VAULT_DIR/paper-notes"
  mkdir -p "$VAULT_DIR/indexes/local"
  mkdir -p "$VAULT_DIR/.claude/skills"

  echo "[3/4] Setting up config files..."
  if [ ! -f "$VAULT_DIR/.scholar.json" ]; then
    cp "$SCRIPT_DIR/templates/scholar.json.template" "$VAULT_DIR/.scholar.json"
    echo "  Created .scholar.json"
  else
    echo "  .scholar.json already exists, skipping"
  fi

  if [ ! -f "$VAULT_DIR/.mcp.json" ]; then
    cp "$SCRIPT_DIR/templates/mcp.json.template" "$VAULT_DIR/.mcp.json"
    echo "  Created .mcp.json"
  else
    echo "  .mcp.json already exists, skipping"
  fi

  if [ ! -f "$VAULT_DIR/.claude/settings.local.json" ]; then
    cp "$SCRIPT_DIR/templates/settings.local.json.template" "$VAULT_DIR/.claude/settings.local.json"
    echo "  Created .claude/settings.local.json"
  else
    echo "  .claude/settings.local.json already exists, skipping"
  fi

  # Install Claude Code skills (project-local)
  echo "[4/4] Installing Claude Code skills (project-local)..."
  SKILLS_DIR="$VAULT_DIR/.claude/skills"
  for skill in conf-papers extract-paper-images paper-analyze paper-search start-my-day; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
      echo "  Updating $skill..."
    else
      echo "  Installing $skill..."
    fi
    cp -r "$SCRIPT_DIR/skills/$skill" "$SKILLS_DIR/$skill"
  done

  echo ""
  echo "=== Setup complete! ==="
  echo ""
  echo "Directory structure:"
  echo "  $VAULT_DIR/"
  echo "  ├── .claude/"
  echo "  │   ├── settings.local.json  # MCP + skill permissions"
  echo "  │   └── skills/              # Project-local skills"
  echo "  ├── .scholar.json            # Scholar-agent config"
  echo "  ├── .mcp.json                # MCP server config"
  echo "  ├── knowledge/               # Knowledge cards"
  echo "  ├── paper-notes/             # Paper analysis notes"
  echo "  └── indexes/                 # BM25 search index"
  echo ""
  echo "Skills installed:"
  echo "  /paper-analyze        - Analyze a paper in depth"
  echo "  /conf-papers          - Search conference papers"
  echo "  /extract-paper-images - Extract figures from papers"
  echo "  /paper-search         - Search existing paper notes"
  echo "  /start-my-day         - Daily paper recommendations"
fi

echo ""
echo "Restart Claude Code to activate."
