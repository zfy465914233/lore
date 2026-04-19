"""Shared configuration reader for Scholar Agent.

Looks for .scholar.json walking up from cwd. If not found, defaults to cwd.

Config file format (.scholar.json):
{
  "knowledge_dir": "./knowledge",       // path to knowledge cards
  "index_path": "./indexes/local/index.json",  // path to BM25 index
  "scholar_dir": "./scholar-agent"            // only needed when embedded as subdirectory
}
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Scholar Agent's own directory (where this file lives)
SCHOLAR_ROOT = Path(__file__).resolve().parents[1]

# Defaults: always resolve relative to cwd, not scholar-agent directory
_DEFAULTS = {
    "knowledge_dir": str(Path.cwd() / "knowledge"),
    "index_path": str(Path.cwd() / "indexes" / "local" / "index.json"),
    "scholar_dir": str(SCHOLAR_ROOT),
}

_config_cache: dict | None = None


def _find_config_file() -> Path | None:
    """Find .scholar.json — walk up from cwd, then check SCHOLAR_ROOT (embedded mode)."""
    current = Path.cwd()
    for _ in range(10):  # max 10 levels up
        candidate = current / ".scholar.json"
        if candidate.exists():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    # Fallback: scholar-agent's own directory (embedded mode where config lives inside scholar-agent/)
    scholar_config_file = SCHOLAR_ROOT / ".scholar.json"
    if scholar_config_file.exists():
        return scholar_config_file
    return None


def load_config() -> dict:
    """Load and return the merged configuration."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    config = dict(_DEFAULTS)

    config_file = _find_config_file()
    if config_file is not None:
        try:
            overrides = json.loads(config_file.read_text(encoding="utf-8"))
            config_base = config_file.parent
            # Resolve relative paths against the config file's directory
            for key in ("knowledge_dir", "index_path", "scholar_dir"):
                if key in overrides:
                    val = overrides[key]
                    if val is not None:
                        p = Path(val)
                        if not p.is_absolute():
                            p = config_base / p
                        config[key] = str(p.resolve())
            # Preserve all other config keys (e.g. academic settings)
            for key, val in overrides.items():
                if key not in ("knowledge_dir", "index_path", "scholar_dir"):
                    config[key] = val
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to parse %s: %s — using defaults", config_file, exc)

    _config_cache = config
    return config


def get_knowledge_dir() -> Path:
    return Path(load_config()["knowledge_dir"])


def get_index_path() -> Path:
    return Path(load_config()["index_path"])


def get_scholar_dir() -> Path:
    return Path(load_config()["scholar_dir"])


def clear_cache() -> None:
    """Clear cached config (useful after setup_mcp.py writes new config)."""
    global _config_cache
    _config_cache = None


def get_research_interests() -> dict:
    """Return research_interests from .scholar.json academic config.

    Returns a dict with 'research_domains' and 'excluded_keywords'.
    Falls back to empty domains if not configured.
    """
    config = load_config()
    academic = config.get("academic", {})
    interests = academic.get("research_interests", {})
    if isinstance(interests, list) and not interests:
        return {"research_domains": {}, "excluded_keywords": []}
    if not isinstance(interests, dict):
        return {"research_domains": {}, "excluded_keywords": []}
    return interests
