# human-voice

A Claude skill that teaches Claude to write like a human, not a language model.

Built from two sources: pre-2021 peer-reviewed scholarship on what makes prose
clear and credible, and a continuously updated catalogue of AI writing patterns
drawn from Wikipedia's Signs of AI Writing field guide, academic linguistics
research, and practitioner journalism.

The scraper runs daily and updates the pattern library automatically.

---

## What This Skill Does

Once installed, Claude reads this skill before writing or editing any text. It
applies:

**Academic writing principles from foundational scholarship**
- George Orwell's six rules from "Politics and the English Language" (1946)
- Strunk and White's "omit needless words" principle (1959)
- Joseph Williams's character-and-action formula from Style: Lessons in
  Clarity and Grace (1981)
- Steven Pinker's Curse of Knowledge analysis from The Sense of Style (2014)
- Flesch and Gunning readability research (1948-1952)

**AI writing detection and avoidance**
- Banned vocabulary (delve, tapestry, underscore, pivotal, and ~50 others)
- Structural patterns to break (rule of threes, negative parallelism,
  false ranges, compulsive balance, template architecture)
- Punctuation rules (no em dash overuse, correct en dash usage)
- The physics of human writing: perplexity and burstiness

**Daily learning**
The scraper checks anchor sources including Wikipedia's Signs of AI Writing
every day, discovers new articles on AI detection, and extracts only patterns
not already in the skill. It also monitors academic writing research for new
findings. Everything goes into `references/live_patterns.md` and
`references/academic_updates.md`, which Claude reads alongside the core skill.

---

## Installation

### Claude.ai (web and desktop app)

**Requirements:** Pro, Max, Team, or Enterprise plan. Code execution must be
enabled in Settings, then Capabilities.

1. Download `human-voice.skill` from the [Releases page](../../releases)
2. Open Claude.ai
3. Go to the left sidebar and click **Customize**, then **Skills**
4. Click the **+** button, then **Create skill** (or **Upload a skill**)
5. Upload the `human-voice.skill` file (it is a ZIP file)
6. The skill appears in your list. Toggle it on.
7. Claude will now apply the skill automatically whenever you ask it to write
   or edit anything.

### Claude Code (command line)

```bash
# Download and install to your personal skills directory (works in all projects)
mkdir -p ~/.claude/skills
curl -sL https://github.com/YOUR_USERNAME/human-voice/releases/latest/download/human-voice.skill \
  -o human-voice.skill
unzip human-voice.skill -d ~/.claude/skills/

# Verify it is there
ls ~/.claude/skills/human-voice/
```

Start a new Claude Code session. The skill loads automatically.

To install for a single project only (shared with your team via git):

```bash
mkdir -p .claude/skills
unzip human-voice.skill -d .claude/skills/
git add .claude/skills/human-voice/
git commit -m "Add human-voice writing skill"
```

### Claude Desktop app

Same steps as Claude.ai. Go to Settings, then Capabilities, then Skills.
Upload the ZIP file.

---

## Using the Skill

Once installed, the skill fires automatically when you ask Claude to write,
edit, draft, or review text. You do not need to invoke it manually.

You can also call it directly by mentioning what you want:

"Write a cold email to a potential investor in my voice"
"Edit this paragraph so it does not sound like AI"
"Rewrite this copy applying everything you know about human writing"

Claude will apply the banned word list, the structural pattern checks, the
academic principles, and the latest scraped intelligence from live_patterns.md.

---

## Keeping It Current

### Run the scraper once

```bash
cd human-voice
pip install -r scripts/requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python scripts/update_patterns.py
```

This updates `references/live_patterns.md` and `references/academic_updates.md`
with the latest intelligence.

### Automate it daily

**Via cron (Mac or Linux):**

Open your crontab with `crontab -e` and add:

```
0 6 * * * cd /path/to/human-voice && python scripts/update_patterns.py >> logs/scraper.log 2>&1
```

**Via GitHub Actions (recommended):**

Fork this repository, then add two secrets in your repo settings
(Settings, then Secrets, then Actions):

- `ANTHROPIC_API_KEY` -- your Anthropic API key
- `SERPER_API_KEY` -- optional, for Google search (falls back to DuckDuckGo)

Copy `scripts/github_action.yml` to `.github/workflows/update-patterns.yml`
in your fork. The workflow will run every morning at 6 AM UTC, update the
pattern files, and commit the changes back to the repo automatically.

When the patterns update, re-download the ZIP and re-upload to Claude.ai, or
pull the latest in Claude Code. The skill learns as the files update.

---

## File Structure

```
human-voice/
├── SKILL.md                          Core skill file Claude reads
├── references/
│   ├── academic_principles.md        Full notes from pre-2021 scholarship
│   ├── banned_words_extended.md      Full word list with frequency data
│   ├── structural_patterns_deep.md   Before/after examples for each pattern
│   ├── live_patterns.md              Updated daily by scraper (AI detection)
│   └── academic_updates.md           Updated by scraper (writing research)
├── scripts/
│   ├── update_patterns.py            The daily scraper
│   ├── requirements.txt              Python dependencies
│   └── github_action.yml             GitHub Actions workflow for automation
└── logs/                             Created on first scraper run
```

---

## Academic Sources

The foundational principles come from these pre-2021 works:

Orwell, G. (1946). Politics and the English Language. Horizon.

Strunk, W., and White, E.B. (1959). The Elements of Style. Macmillan.

Williams, J.M. (1981). Style: Lessons in Clarity and Grace. Scott Foresman.
(Multiple subsequent editions through Pearson.)

Flesch, R. (1948). A new readability yardstick. Journal of Applied Psychology,
32(3), 221-233.

Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.

Pinker, S. (2014). The Sense of Style: The Thinking Person's Guide to Writing
in the 21st Century. Penguin.

---

## Contributing

Pull requests for new patterns, better before/after examples, or improved
scraper sources are welcome. Please do not add patterns that are not
documented in a credible source. The standard is: every pattern needs evidence,
not observation.

---

## License

MIT. Use freely. Attribution appreciated but not required.
