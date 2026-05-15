# Complete Setup Guide

How to put the human-voice skill on GitHub and make the daily scraper run
automatically. Follow each section in order.

---

## What You Need Before Starting

- A GitHub account (free at github.com)
- An Anthropic API key (paid, from console.anthropic.com)
- Python 3.10 or higher on your computer
- Git installed on your computer
- About 30 minutes

That is the full list. You do not need to know how to code.

---

## Part 1: Set Up Your GitHub Repository

### Step 1: Create a new GitHub account (skip if you already have one)

Go to github.com. Click Sign Up. Use your email, pick a username, and verify
your account. The free plan is fine.

### Step 2: Create the repository

After signing in:

1. Click the green New button on the left side of your GitHub dashboard.
2. Name the repository: `human-voice`
3. Set it to Public (this lets other people find and use your skill).
4. Check the box that says "Add a README file".
5. Click Create repository.

You now have an empty repo at `github.com/YOUR_USERNAME/human-voice`.

### Step 3: Install Git on your computer (skip if already installed)

Mac: Open Terminal and type `git --version`. If it prompts you to install
developer tools, click Install.

Windows: Download from git-scm.com/download/win. Run the installer with all
default options.

Linux: Run `sudo apt install git` or `sudo dnf install git`.

### Step 4: Clone the repository to your computer

Open Terminal (Mac/Linux) or Command Prompt (Windows). Run:

```bash
git clone https://github.com/YOUR_USERNAME/human-voice.git
cd human-voice
```

Replace YOUR_USERNAME with your actual GitHub username. You now have a local
copy of the repo on your machine.

---

## Part 2: Put the Skill Files Into the Repository

### Step 5: Extract the skill ZIP

You should have `human-voice.skill` downloaded. That file is a ZIP archive.

Mac: Double-click it in Finder. It extracts a folder called `human-voice`.

Windows: Right-click it, choose Extract All, and extract to your Desktop.

Linux: Run `unzip human-voice.skill -d ~/Desktop/extracted`

Inside the extracted folder you will find:

```
human-voice/
  SKILL.md
  README.md
  references/
    academic_principles.md
    academic_updates.md
    banned_words_extended.md
    live_patterns.md
    structural_patterns_deep.md
  scripts/
    update_patterns.py
    build_platforms.py
    github_action.yml
    requirements.txt
  platforms/
    UNIVERSAL_SYSTEM_PROMPT.md
    api-system-prompt.md
    chatgpt-custom-gpt-instructions.md
    chatgpt-custom-instructions.md
    gemini-gem-instructions.md
```

### Step 6: Copy the files into your cloned repository

You need the contents of the extracted `human-voice/` folder to go into the
root of your cloned repo (not inside a subfolder).

Mac/Linux, in Terminal:

```bash
cp -r ~/Desktop/human-voice/* ~/path/to/your/cloned/human-voice/
```

Windows, in File Explorer: open both folders side by side, select all files
inside the extracted `human-voice/` folder, and paste them into your cloned
`human-voice/` folder.

After copying, your cloned repo should look like this from inside:

```
human-voice/  (the git repo folder)
  SKILL.md
  README.md
  references/
  scripts/
  platforms/
```

### Step 7: Create the GitHub Actions workflow folder

The GitHub Actions workflow file needs to live in `.github/workflows/`. Create
that folder and copy the file into it.

Mac/Linux:

```bash
cd ~/path/to/your/cloned/human-voice
mkdir -p .github/workflows
cp scripts/github_action.yml .github/workflows/update-patterns.yml
```

Windows (Command Prompt):

```cmd
cd C:\path\to\your\cloned\human-voice
mkdir .github\workflows
copy scripts\github_action.yml .github\workflows\update-patterns.yml
```

### Step 8: Push everything to GitHub

Still inside your cloned repo folder, run:

```bash
git add .
git commit -m "Initial commit: human-voice skill and scraper"
git push origin main
```

If Git asks for your GitHub credentials, enter your username and your Personal
Access Token (not your password). To create a token: go to github.com,
click your profile picture, then Settings, then Developer settings, then
Personal access tokens, then Tokens (classic), then Generate new token.
Give it repo scope and copy the token.

After the push, go to `github.com/YOUR_USERNAME/human-voice` in your browser.
You should see all the files there.

---

## Part 3: Get Your Anthropic API Key

The scraper uses Claude to extract patterns from scraped content. You need an
API key for this.

### Step 9: Create or retrieve your Anthropic API key

1. Go to console.anthropic.com.
2. Sign in or create an account.
3. Click API Keys in the left sidebar.
4. Click Create Key.
5. Name it: `human-voice-scraper`
6. Copy the key immediately. You will not see it again.

The key looks like: `sk-ant-api03-...`

Keep it somewhere safe. Do not put it in any file that goes into your GitHub
repo.

### How much will it cost?

Each scraper run calls Claude Sonnet to extract patterns from scraped pages.
A typical run processes 10 to 15 pages. At Sonnet pricing, each run costs
roughly $0.03 to $0.08. Running daily costs under $2 per month.

---

## Part 4: Add Secrets to GitHub Actions

GitHub Actions needs your API key to run the scraper. You give it the key
as an encrypted secret, not as plain text.

### Step 10: Add the Anthropic API key as a GitHub secret

1. Go to `github.com/YOUR_USERNAME/human-voice`.
2. Click the Settings tab (gear icon near the top right of the repo).
3. In the left sidebar, click Secrets and variables, then Actions.
4. Click New repository secret.
5. Name: `ANTHROPIC_API_KEY`
6. Value: paste your API key (`sk-ant-api03-...`)
7. Click Add secret.

### Step 11: Add the Serper API key (optional but recommended)

Without this, the scraper falls back to DuckDuckGo for search. DuckDuckGo
works but is less reliable for discovery. Serper gives Google results.

To get a Serper key:
1. Go to serper.dev.
2. Sign up for a free account (2,500 free searches per month, enough for
   roughly 3 months of daily runs before you need to add payment).
3. Copy your API key from the dashboard.

Add it as a GitHub secret following the same steps:
- Name: `SERPER_API_KEY`
- Value: your Serper key

If you skip this step, the scraper still runs. It just uses DuckDuckGo.

---

## Part 5: Run the Scraper for the First Time

### Step 12: Trigger the workflow manually

1. Go to `github.com/YOUR_USERNAME/human-voice`.
2. Click the Actions tab.
3. You should see "Update Patterns and Publish Skill" in the left sidebar.
4. Click it.
5. On the right side, click Run workflow, then click the green Run workflow
   button.

The workflow starts. Click into it to watch the live log.

It takes about 5 to 8 minutes to run. When it finishes:

- `references/live_patterns.md` is updated with new AI writing patterns.
- `references/academic_updates.md` is updated with new writing research.
- A GitHub Release is published with two downloadable files:
  - `human-voice.skill` for Claude
  - `human-voice-api-prompt.txt` for any API

You can see the release at `github.com/YOUR_USERNAME/human-voice/releases`.

### If the workflow fails

Click the failed step to see the error log. Common problems:

"ANTHROPIC_API_KEY not set" -- you did not add the secret in Step 10, or
you mistyped the secret name. Check that it is exactly `ANTHROPIC_API_KEY`.

"No module named anthropic" -- the requirements.txt was not found. Verify
the file is at `scripts/requirements.txt` in your repo (not inside a subfolder).

"Permission denied: push" -- your GitHub token does not have write access.
Go to your Personal Access Token settings and add the `repo` scope.

---

## Part 6: Verify Daily Automation

### Step 13: Confirm the schedule is active

The workflow runs automatically every day at 6 AM UTC. You do not need to
do anything after the first manual run.

To confirm it is scheduled:
1. Go to the Actions tab in your repo.
2. Click on "Update Patterns and Publish Skill".
3. You should see "Schedule" listed under "Triggers".

GitHub may disable scheduled workflows on repos that have had no activity for
60 days. If that happens, just push a small change (like adding a blank line
to README.md) to reactivate it.

---

## Part 7: Install the Skill in Claude

### Step 14: Download the latest skill file

Go to `github.com/YOUR_USERNAME/human-voice/releases`. Click the most recent
release. Download `human-voice.skill`.

Or use the file you already downloaded from this conversation.

### Step 15: Enable code execution in Claude

The skill requires this to work.

1. Go to claude.ai.
2. Click your profile icon in the top right corner.
3. Click Settings.
4. Click Capabilities.
5. Make sure Code Execution is turned on.

### Step 16: Upload the skill

1. In the left sidebar on claude.ai, click Customize.
2. Click Skills.
3. Click the + button.
4. Click Create skill (or Upload a skill if that option appears).
5. Upload `human-voice.skill`.
6. It appears in your skills list. Toggle it on.

The skill is now active. Claude reads it automatically before writing or
editing any text. You do not need to mention it in your prompts.

### Step 17: Test it

Start a new chat. Ask Claude to write something, anything. An email, a
paragraph, a pitch. The output should show no banned words, no em dashes used
as connectors, no compulsive summaries, and varied sentence lengths.

To explicitly test it, ask: "Write a paragraph about Payble's UK launch."
Compare the output to what Claude produced before the skill was installed.

---

## Part 8: Share the Skill With Others

### How other people install it

Point them to your GitHub releases page:
`github.com/YOUR_USERNAME/human-voice/releases`

They download `human-voice.skill` and follow Steps 15 and 16 above.

### For ChatGPT users

They go to `github.com/YOUR_USERNAME/human-voice/tree/main/platforms` and
copy the contents of `chatgpt-custom-gpt-instructions.md` into their Custom
GPT builder. They also download the four reference files from `references/`
and upload them as knowledge files inside the GPT builder.

### For Gemini users

Same approach. They copy from `gemini-gem-instructions.md` and upload the
reference files into their Gem.

### For developers using any API

They use `human-voice-api-prompt.txt` from the releases page as their system
prompt. The `api-system-prompt.md` in the `platforms/` folder has ready-to-run
code examples for OpenAI, Anthropic, Google, and Ollama.

---

## Part 9: Keeping the Skill Updated

### How updates flow

Every morning, the GitHub Action runs the scraper. It finds new AI writing
detection articles and new academic writing research. It extracts any genuinely
new patterns (not already in the skill) and writes them to the reference files.
It then packages a fresh `human-voice.skill` and publishes it as a release.

### To get the latest version into Claude

1. Go to your releases page and download the new `human-voice.skill`.
2. In Claude's Skills section, click the three dots next to the current skill.
3. Click Delete, then confirm.
4. Upload the new file and toggle it on.

This takes about 2 minutes. You only need to do it when you want the latest
scraped patterns. The skill works correctly without updates -- the core academic
principles do not change.

---

## Quick Reference

```
GitHub repo:     github.com/YOUR_USERNAME/human-voice
Releases page:   github.com/YOUR_USERNAME/human-voice/releases
Actions tab:     github.com/YOUR_USERNAME/human-voice/actions
Secrets:         github.com/YOUR_USERNAME/human-voice/settings/secrets/actions

Required secrets:
  ANTHROPIC_API_KEY   (from console.anthropic.com)
  SERPER_API_KEY      (optional, from serper.dev)

Scraper schedule:   Daily at 6 AM UTC (automatic after first run)
Approx cost:        Under $2/month at current Anthropic API pricing

Claude install:     Settings > Capabilities > Code Execution ON
                    Customize > Skills > Upload human-voice.skill
```
