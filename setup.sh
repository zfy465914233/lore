#!/usr/bin/env bash
# scholar-agent setup script
# Usage: cd your-project && bash path/to/scholar-agent/setup.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(pwd)"

echo "=== Scholar Agent Setup ==="
echo "Project root: $VAULT_DIR"
echo ""

# 1. Create directory structure
echo "[1/4] Creating directories..."
mkdir -p "$VAULT_DIR/knowledge"
mkdir -p "$VAULT_DIR/paper-notes"
mkdir -p "$VAULT_DIR/indexes/local"
mkdir -p "$VAULT_DIR/.claude/skills"

# 2. Copy config templates (don't overwrite existing)
echo "[2/4] Setting up config files..."
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

# 3. Install Claude Code skills (project-local, not global)
echo "[3/4] Installing Claude Code skills (project-local)..."
SKILLS_DIR="$VAULT_DIR/.claude/skills"

for skill in conf-papers extract-paper-images paper-analyze paper-search start-my-day; do
  if [ -d "$SKILLS_DIR/$skill" ]; then
    echo "  Updating $skill..."
  else
    echo "  Installing $skill..."
  fi
  cp -r "$SCRIPT_DIR/skills/$skill" "$SKILLS_DIR/$skill"
done

# 4. Build knowledge index
echo "[4/4] Building knowledge index..."
cd "$VAULT_DIR"
if command -v python &>/dev/null; then
  python "$SCRIPT_DIR/scripts/local_index.py" 2>/dev/null || echo "  (Index will be built on first query)"
else
  echo "  Python not found, index will be built on first query"
fi

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Directory structure:"
echo "  $VAULT_DIR/"
echo "  ├── .claude/"
echo "  │   ├── settings.local.json  # MCP + skill permissions"
echo "  │   └── skills/              # Project-local skills"
echo "  ├── .scholar.json              # Scholar-agent config"
echo "  ├── .mcp.json                # MCP server config"
echo "  ├── knowledge/               # Knowledge cards"
echo "  ├── paper-notes/             # Paper analysis notes"
echo  └── indexes/                 # BM25 search index"
echo ""
echo "Skills installed:"
echo "  /paper-analyze        - Analyze a paper in depth"
echo "  /conf-papers          - Search conference papers"
echo "  /extract-paper-images - Extract figures from papers"
echo "  /paper-search         - Search existing paper notes"
echo "  /start-my-day         - Daily paper recommendations"
echo ""
echo "Restart Claude Code to activate."
