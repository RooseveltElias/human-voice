#!/usr/bin/env python3
"""
human-voice/scripts/update_patterns.py

Daily scraper that does two things:
1. Hunts new AI writing detection research and updates references/live_patterns.md
2. Learns from high-quality pre-2021 academic sources and updates
   references/academic_updates.md with any newly discovered scholarship

Usage:
    python scripts/update_patterns.py

Environment variables:
    ANTHROPIC_API_KEY  -- required for pattern extraction
    SERPER_API_KEY     -- optional, enables Google search (falls back to DuckDuckGo)

Cron example (daily at 6 AM):
    0 6 * * * cd /path/to/human-voice && python scripts/update_patterns.py

GitHub Actions: see scripts/github_action.yml
"""

import os
import json
import re
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
import anthropic

# ---- Configuration ----------------------------------------------------------

BASE_DIR = Path(__file__).parent.parent
REFERENCES_DIR = BASE_DIR / "references"
LIVE_PATTERNS_FILE = REFERENCES_DIR / "live_patterns.md"
ACADEMIC_UPDATES_FILE = REFERENCES_DIR / "academic_updates.md"
STATE_FILE = BASE_DIR / ".scraper_state.json"
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "scraper.log"),
    ],
)
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# ---- Anchor sources: AI detection -------------------------------------------
# These are checked every run for new patterns.

AI_DETECTION_SOURCES = [
    {
        "name": "Wikipedia: Signs of AI Writing",
        "url": "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing",
        "priority": "high",
    },
    {
        "name": "Beutler Ink: How to Spot AI Writing",
        "url": "https://www.beutlerink.com/blog/how-to-spot-ai-writing",
        "priority": "high",
    },
    {
        "name": "HumanizeThisAI: AI Writing Patterns",
        "url": "https://humanizethisai.com/blog/what-are-ai-writing-patterns",
        "priority": "high",
    },
    {
        "name": "Leap AI: Perplexity vs Burstiness",
        "url": "https://www.tryleap.ai/learn/perplexity-vs-burstiness",
        "priority": "medium",
    },
    {
        "name": "Augmented Educator: Ten Telltale Signs",
        "url": "https://www.theaugmentededucator.com/p/the-ten-telltale-signs-of-ai-generated",
        "priority": "medium",
    },
]

# ---- Anchor sources: Academic writing quality --------------------------------
# Legitimate pre-2021 sources on what makes prose clear and human.
# These are checked periodically for any new analysis or commentary.

ACADEMIC_SOURCES = [
    {
        "name": "Orwell 1946: Politics and the English Language (full text)",
        "url": "https://bioinfo.uib.es/~joemiro/RecEscr/PoliticsandEngLang.pdf",
        "type": "primary",
        "period": "pre-2021",
    },
    {
        "name": "Flesch Readability Research: Overview",
        "url": "https://legible.com/blog/flesch-reading-ease/",
        "type": "secondary",
        "period": "pre-2021",
    },
    {
        "name": "Purdue OWL: Active vs Passive Voice",
        "url": "https://owl.purdue.edu/owl/general_writing/academic_writing/active_and_passive_voice/active_versus_passive_voice.html",
        "type": "reference",
        "period": "pre-2021",
    },
    {
        "name": "Writing Center: Sentence Variety and Rhythm",
        "url": "https://www.sjsu.edu/writingcenter/docs/handouts/Sentence%20Variety%20and%20Rhythm.pdf",
        "type": "reference",
        "period": "pre-2021",
    },
]

# ---- Discovery search queries -----------------------------------------------

AI_DETECTION_QUERIES = [
    "AI writing detection new patterns 2026",
    "LLM text fingerprints linguistic markers research",
    "ChatGPT Claude Gemini writing style differences aidiolect",
    "AI generated text academic study vocabulary patterns",
    "how to spot AI writing new tells signs",
]

ACADEMIC_QUERIES = [
    "academic research writing clarity concision linguistics peer reviewed",
    "nominalization active voice readability research writing quality",
    "sentence length variation prose rhythm linguistics study",
    "plain language movement evidence readability English writing",
]

# ---- Core utilities ---------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "seen_ai_urls": [],
        "seen_academic_urls": [],
        "last_run": None,
        "run_history": [],
        "pattern_count": 0,
        "academic_count": 0,
    }


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def fetch_page(url: str, timeout: int = 20) -> Optional[str]:
    """Fetch and clean page text. Returns None on failure."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:15000]
    except Exception as e:
        log.warning(f"Fetch failed for {url}: {e}")
        return None


def search_duckduckgo(query: str, max_results: int = 5) -> list[dict]:
    try:
        r = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query, "b": ""},
            headers=HEADERS,
            timeout=15,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for a in soup.select(".result__a")[:max_results]:
            href = a.get("href", "")
            m = re.search(r"uddg=([^&]+)", href)
            if m:
                from urllib.parse import unquote
                href = unquote(m.group(1))
            if href.startswith("http"):
                results.append({"title": a.get_text(strip=True), "url": href})
        return results
    except Exception as e:
        log.warning(f"DuckDuckGo search failed: {e}")
        return []


def search(query: str, max_results: int = 5) -> list[dict]:
    key = os.getenv("SERPER_API_KEY")
    if not key:
        return search_duckduckgo(query, max_results)
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={"q": query, "num": max_results},
            timeout=15,
        )
        data = r.json()
        return [
            {"title": item.get("title", ""), "url": item.get("link", "")}
            for item in data.get("organic", [])
            if item.get("link", "").startswith("http")
        ]
    except Exception as e:
        log.warning(f"Serper search failed ({e}), falling back to DuckDuckGo")
        return search_duckduckgo(query, max_results)


# ---- Extraction via Anthropic -----------------------------------------------

def extract_ai_patterns(content: str, source_name: str, client: anthropic.Anthropic) -> Optional[str]:
    """Extract AI writing detection patterns from scraped content."""
    prompt = f"""You are an expert analyst extracting AI writing detection patterns.

SOURCE: {source_name}
CONTENT:
{content}

Extract ONLY specific, actionable patterns for detecting AI-generated writing.

For each new pattern found, provide:
- A short name
- What it looks like (with an example if available in the content)
- Why it is a tell
- How to avoid it

Ignore patterns already in this standard list:
em dash overuse, rule of threes, negative parallelism ("It's not X it's Y"),
compulsive summaries ("In conclusion", "Overall"), banned words (delve tapestry
pivotal underscore landscape foster testament enhance robust innovative transformative
realm adept bolster harness), participial phrase overuse, compulsive balance
("while there are benefits there are also drawbacks"), false ranges ("from X to Y"),
template architecture.

If genuinely new patterns exist in this source, format them clearly in markdown.
If no new patterns exist, respond with exactly: NO_NEW_PATTERNS

Keep response under 500 words."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        return None if text == "NO_NEW_PATTERNS" else text
    except Exception as e:
        log.warning(f"Pattern extraction failed for {source_name}: {e}")
        return None


def extract_academic_insights(
    content: str, source_name: str, client: anthropic.Anthropic
) -> Optional[str]:
    """Extract writing quality principles from academic or research sources."""
    prompt = f"""You are an expert analyst extracting principles of good human writing
from academic and research sources.

SOURCE: {source_name}
CONTENT:
{content}

Extract ONLY specific, concrete, actionable writing principles from this source.
Focus on principles that:
1. Come from research, scholarship, or evidence (not opinion)
2. Explain what makes prose clear, natural, and human
3. Are not already covered by these well-known principles:
   Orwell's six rules, Strunk's "omit needless words", Pinker's curse of knowledge,
   Williams's character-and-action formula, Flesch readability, active voice preference,
   nominalization avoidance, sentence length variation

If genuinely new or complementary research-backed principles exist, present them
clearly in markdown with the source/evidence basis.

If nothing new, respond with exactly: NO_NEW_INSIGHTS

Keep response under 500 words."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        return None if text == "NO_NEW_INSIGHTS" else text
    except Exception as e:
        log.warning(f"Academic extraction failed for {source_name}: {e}")
        return None


# ---- Discovery pipelines ----------------------------------------------------

def is_useful_url(url: str) -> bool:
    skip_domains = [
        "youtube.com", "twitter.com", "x.com", "reddit.com",
        "facebook.com", "instagram.com", "tiktok.com",
        "amazon.com", "pinterest.com", "linkedin.com",
    ]
    skip_terms = ["buy", "shop", "price", "coupon", "signup", "free-trial"]
    url_lower = url.lower()
    for d in skip_domains:
        if d in url_lower:
            return False
    for t in skip_terms:
        if t in url_lower:
            return False
    return True


def discover_urls(queries: list[str], seen_urls: set, n_queries: int = 3) -> list[dict]:
    discovered = []
    for query in queries[:n_queries]:
        time.sleep(2)
        for r in search(query, max_results=4):
            url = r.get("url", "")
            if url and url not in seen_urls and is_useful_url(url):
                discovered.append(r)
                seen_urls.add(url)
    return discovered


# ---- File writers -----------------------------------------------------------

def write_live_patterns(patterns: list[dict], state: dict) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Live Patterns: Auto-Updated by Daily Scraper",
        "",
        f"Last updated: {now}",
        f"Sources with new patterns this run: {len(patterns)}",
        "",
        "This file is regenerated daily. Do not edit manually.",
        "To add permanent patterns, edit SKILL.md or the static reference files.",
        "",
        "---",
        "",
    ]

    if not patterns:
        lines += [
            "## No New Patterns This Run",
            "",
            "All scraped sources matched patterns already in the static reference files.",
            "",
        ]
    else:
        for p in patterns:
            lines += [
                f"## {p['source']}",
                f"Source: {p['url']}",
                "",
                p["patterns"],
                "",
                "---",
                "",
            ]

    history = state.get("run_history", [])
    if state.get("last_run"):
        history.append(state["last_run"])
    history = history[-5:]
    state["run_history"] = history

    lines += ["## Run History (last 5)", ""] + [f"- {ts}" for ts in reversed(history)]

    LIVE_PATTERNS_FILE.parent.mkdir(exist_ok=True)
    LIVE_PATTERNS_FILE.write_text("\n".join(lines))
    log.info(f"Wrote live_patterns.md with {len(patterns)} source(s)")


def write_academic_updates(insights: list[dict]) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Academic Updates: New Research on Writing Quality",
        "",
        f"Last updated: {now}",
        "",
        "This file contains writing quality principles discovered by the scraper",
        "that complement but go beyond the foundational sources in academic_principles.md.",
        "",
        "---",
        "",
    ]

    if not insights:
        lines += [
            "## No New Academic Insights This Run",
            "",
            "All scraped academic content matched principles already in academic_principles.md.",
            "",
        ]
    else:
        for insight in insights:
            lines += [
                f"## {insight['source']}",
                f"Source: {insight['url']}",
                "",
                insight["insights"],
                "",
                "---",
                "",
            ]

    ACADEMIC_UPDATES_FILE.parent.mkdir(exist_ok=True)
    ACADEMIC_UPDATES_FILE.write_text("\n".join(lines))
    log.info(f"Wrote academic_updates.md with {len(insights)} source(s)")


# ---- Main -------------------------------------------------------------------

def run_scraper() -> None:
    log.info("=" * 60)
    log.info(f"Scraper run starting: {datetime.now(timezone.utc).isoformat()}")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("ANTHROPIC_API_KEY not set. Exiting.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    state = load_state()

    ai_seen = set(state.get("seen_ai_urls", []))
    academic_seen = set(state.get("seen_academic_urls", []))

    # ---- Phase 1: AI detection pattern scraping ----------------------------

    ai_patterns: list[dict] = []

    log.info(f"Phase 1: Scraping {len(AI_DETECTION_SOURCES)} AI detection sources...")
    for source in AI_DETECTION_SOURCES:
        log.info(f"  Checking: {source['name']}")
        text = fetch_page(source["url"])
        if text:
            patterns = extract_ai_patterns(text, source["name"], client)
            if patterns:
                ai_patterns.append({
                    "source": source["name"],
                    "url": source["url"],
                    "patterns": patterns,
                })
                log.info(f"    New patterns found")
            else:
                log.info(f"    No new patterns")
        time.sleep(3)

    log.info("Phase 1: Discovering new AI detection sources...")
    new_ai_sources = discover_urls(AI_DETECTION_QUERIES, ai_seen, n_queries=3)
    log.info(f"  Found {len(new_ai_sources)} new URLs to check")

    for source in new_ai_sources[:6]:
        url = source.get("url", "")
        title = source.get("title", url)[:70]
        log.info(f"  Checking: {title}")
        text = fetch_page(url)
        if text:
            patterns = extract_ai_patterns(text, title, client)
            if patterns:
                ai_patterns.append({
                    "source": title,
                    "url": url,
                    "patterns": patterns,
                })
                log.info(f"    New patterns found")
        time.sleep(3)

    # ---- Phase 2: Academic source learning ----------------------------------

    academic_insights: list[dict] = []

    log.info(f"Phase 2: Checking {len(ACADEMIC_SOURCES)} academic sources...")
    for source in ACADEMIC_SOURCES:
        log.info(f"  Checking: {source['name']}")
        text = fetch_page(source["url"])
        if text:
            insights = extract_academic_insights(text, source["name"], client)
            if insights:
                academic_insights.append({
                    "source": source["name"],
                    "url": source["url"],
                    "insights": insights,
                })
                log.info(f"    New insights found")
            else:
                log.info(f"    No new insights")
        time.sleep(3)

    log.info("Phase 2: Discovering new academic writing research...")
    new_academic_sources = discover_urls(ACADEMIC_QUERIES, academic_seen, n_queries=2)
    log.info(f"  Found {len(new_academic_sources)} new URLs to check")

    for source in new_academic_sources[:4]:
        url = source.get("url", "")
        title = source.get("title", url)[:70]
        log.info(f"  Checking: {title}")
        text = fetch_page(url)
        if text:
            insights = extract_academic_insights(text, title, client)
            if insights:
                academic_insights.append({
                    "source": title,
                    "url": url,
                    "insights": insights,
                })
                log.info(f"    New insights found")
        time.sleep(3)

    # ---- Write outputs -------------------------------------------------------

    write_live_patterns(ai_patterns, state)
    write_academic_updates(academic_insights)

    state["seen_ai_urls"] = list(ai_seen)
    state["seen_academic_urls"] = list(academic_seen)
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state["pattern_count"] = len(ai_patterns)
    state["academic_count"] = len(academic_insights)
    save_state(state)

    log.info(f"Run complete.")
    log.info(f"  AI patterns: {len(ai_patterns)} sources produced new content")
    log.info(f"  Academic insights: {len(academic_insights)} sources produced new content")


if __name__ == "__main__":
    run_scraper()
