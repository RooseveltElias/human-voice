#!/usr/bin/env python3
"""
human-voice/scripts/build_platforms.py

Reads the current state of all reference files and regenerates the platform-
specific exports: live_patterns summary injection into each platform file.

Run this after update_patterns.py, or call it from the GitHub Action.

Usage:
    python scripts/build_platforms.py
"""

from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
REFERENCES_DIR = BASE_DIR / "references"
PLATFORMS_DIR = BASE_DIR / "platforms"


def read_file(path: Path, fallback: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return fallback


def extract_new_patterns(live_patterns_text: str) -> str:
    """Pull only the newly discovered patterns from live_patterns.md."""
    lines = live_patterns_text.splitlines()
    in_content = False
    content_lines = []
    for line in lines:
        if line.startswith("## High-Priority Sources") or \
           line.startswith("## Secondary Sources") or \
           line.startswith("## Newly Discovered"):
            in_content = True
        elif line.startswith("## Run History"):
            in_content = False
        if in_content:
            content_lines.append(line)
    result = "\n".join(content_lines).strip()
    if not result or "No New Patterns" in result:
        return ""
    return result


def build_platform_readme() -> None:
    """Update platforms/README.md with current status."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    live = read_file(REFERENCES_DIR / "live_patterns.md")
    academic = read_file(REFERENCES_DIR / "academic_updates.md")

    live_last = "Not yet run"
    for line in live.splitlines():
        if line.startswith("Last updated:"):
            live_last = line.replace("Last updated:", "").strip()
            break

    academic_last = "Not yet run"
    for line in academic.splitlines():
        if line.startswith("Last updated:"):
            academic_last = line.replace("Last updated:", "").strip()
            break

    content = f"""# Platform Exports

Generated: {now}

This folder contains ready-to-paste instructions for each LLM platform.
All files derive from the same source knowledge in the `references/` folder.

## Files

| File | Platform | Method | Character limit |
|------|----------|--------|-----------------|
| `UNIVERSAL_SYSTEM_PROMPT.md` | Any | System prompt | Context window |
| `chatgpt-custom-gpt-instructions.md` | ChatGPT | Custom GPT Builder | ~8,000 chars |
| `chatgpt-custom-instructions.md` | ChatGPT | Custom Instructions | 1,500 per field |
| `gemini-gem-instructions.md` | Gemini | Gems | No known limit |
| `api-system-prompt.md` | Any API | system / system_instruction | Context window |

## Knowledge Files to Upload

For Custom GPT and Gemini Gems (both support file uploads), upload these
reference files from the `references/` folder alongside the instructions.
This gives the model access to the full depth of the skill.

- `academic_principles.md` -- Orwell, Pinker, Williams, Strunk source notes
- `banned_words_extended.md` -- full word list with frequency data
- `structural_patterns_deep.md` -- before/after examples for every pattern
- `live_patterns.md` -- latest AI detection research (scraper: {live_last})
- `academic_updates.md` -- latest writing research (scraper: {academic_last})

## Platform Comparison

**Claude (Skills)** -- most capable. The full SKILL.md plus all reference
files load automatically. Claude reads them before writing anything.
Install: upload `human-voice.skill` via Settings > Customize > Skills.

**ChatGPT Custom GPT** -- second most capable. The instruction field takes
~8,000 chars. Upload the reference files as knowledge files in the GPT
Builder. Requires ChatGPT Plus or higher.

**Gemini Gem** -- comparable to Custom GPT. No published instruction limit.
Supports uploaded Google Drive files as well as direct file upload.
Requires a Google AI plan (Gemini Advanced).

**ChatGPT Custom Instructions** -- most limited. Only 1,500 chars per field.
The compressed version covers the core rules but not the full reference library.
Available on all ChatGPT plans.

**API** -- most flexible. Include the full system prompt with no length
constraints beyond the model's context window. Works with OpenAI, Anthropic,
Google, Mistral, Groq, Ollama, and any OpenAI-compatible endpoint.
"""
    (PLATFORMS_DIR / "README.md").write_text(content)
    print(f"  Wrote platforms/README.md")


def build_all() -> None:
    print("Building platform exports...")
    PLATFORMS_DIR.mkdir(exist_ok=True)
    build_platform_readme()
    print("Done.")


if __name__ == "__main__":
    build_all()
