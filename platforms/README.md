# Platform Exports

Generated: 2026-08-10 07:26 UTC

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
- `live_patterns.md` -- latest AI detection research (scraper: 2026-08-10 07:26 UTC)
- `academic_updates.md` -- latest writing research (scraper: 2026-08-10 07:26 UTC)

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
