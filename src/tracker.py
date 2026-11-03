"""Daily arXiv metadata collector and research digest.

Standard-library only. Optional OpenAI summaries require OPENAI_API_KEY.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "papers.json"
REPORT_DIR = ROOT / "reports"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_API = "https://export.arxiv.org/api/query"
SEARCH = '(cat:cs.CL OR cat:cs.AI OR cat:cs.IR)'
TOPICS = {
    "RAG": ("retrieval augmented", "retrieval-augmented", "rag", "retriever", "retrieval"),
    "LLM": ("large language model", "language models", "llm", "instruction tuning", "reasoning"),
    "Agent": ("agentic", "ai agent", "multi-agent", "tool use", "tool calling", "autonomous agent"),
}
# Generic terms are given less weight; a paper must match at least one distinctive term.
STRONG_TERMS = (
    "retrieval augmented", "retrieval-augmented", "large language model",
    "llm", "agentic", "ai agent", "multi-agent", "tool calling",
    "autonomous agent", "rag", "retriever",
)


def clean(value: str) -> str:
    return " ".join((value or "").split())


def arxiv_id(url: str) -> str:
    identifier = url.rstrip("/").rsplit("/", 1)[-1]
    return re.sub(r"v\d+$", "", identifier)


def parse_feed(xml_text: bytes) -> list[dict]:
    root = ET.fromstring(xml_text)
    if root.tag != ATOM + "feed":
        raise ValueError("Unexpected arXiv response: Atom feed missing")
    results = []
    for entry in root.findall(ATOM + "entry"):
        link = clean(entry.findtext(ATOM + "id", default=""))
        title = clean(entry.findtext(ATOM + "title", default=""))
        abstract = clean(entry.findtext(ATOM + "summary", default=""))
        published = clean(entry.findtext(ATOM + "published", default=""))
        if not (link and title and abstract and published):
            continue
        if "/api/errors#" in link:
            raise ValueError("arXiv returned an API error entry")
        authors = [
            clean(author.findtext(ATOM + "name", default=""))
            for author in entry.findall(ATOM + "author")
        ]
        results.append({
            "id": arxiv_id(link),
            "title": title,
            "abstract": abstract,
            "authors": [a for a in authors if a],
            "published": published,
            "updated": clean(entry.findtext(ATOM + "updated", default="")),
            "url": f"https://arxiv.org/abs/{arxiv_id(link)}",
            "categories": [
                c.attrib["term"] for c in entry.findall(ATOM + "category")
                if "term" in c.attrib
            ],
        })
    return results


def fetch_papers(max_results: int) -> list[dict]:
    params = urllib.parse.urlencode({
        "search_query": SEARCH,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    url = ARXIV_API + "?" + params
    headers = {
        "User-Agent": os.getenv("ARXIV_USER_AGENT", "AIPaperTracker/1.0 (research metadata collection)"),
        "Accept": "application/atom+xml",
    }
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=40) as response:
                return parse_feed(response.read())
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == 2:
                raise RuntimeError(f"arXiv request failed: {exc}") from exc
            time.sleep(3 * (attempt + 1))
    return []


def classify(paper: dict) -> tuple[list[str], int]:
    title = paper["title"].lower()
    body = (paper["title"] + " " + paper["abstract"]).lower()
    labels = [name for name, terms in TOPICS.items() if any(t in body for t in terms)]
    strong = sum(1 for term in STRONG_TERMS if term in body)
    score = min(100, strong * 15 + sum(10 for term in STRONG_TERMS if term in title))
    return labels, score


def is_recent(paper: dict, now: datetime, days: int) -> bool:
    try:
        published = datetime.fromisoformat(paper["published"].replace("Z", "+00:00"))
    except ValueError:
        return False
    return now - timedelta(days=days) <= published <= now + timedelta(minutes=5)


def fallback_summary(abstract: str) -> str:
    """Excerpt only: never invent an abstract-based paraphrase."""
    text = clean(abstract)
    return text[:350].rstrip() + ("…" if len(text) > 350 else "")


def llm_summary(paper: dict, key: str, model: str) -> str:
    """Optional summary based only on title and abstract, not the full paper."""
    payload = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": 220,
        "messages": [
            {"role": "system", "content":
             "Summarize the following paper title and abstract in 2 concise Korean sentences. "
             "Only use the provided abstract; avoid invented claims or experimental numbers."},
            {"role": "user", "content":
             f"Title: {paper['title']}\nAbstract: {paper['abstract']}"},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "User-Agent": "AIPaperTracker/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        obj = json.load(response)
    return clean(obj["choices"][0]["message"]["content"])


def read_existing(path: Path) -> list[dict]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("data/papers.json must be a JSON list")
    return raw


def md_safe(value: str) -> str:
    return clean(value).replace("|", "\\|").replace("\n", " ")


def make_report(papers: list[dict], date: str, source_count: int) -> str:
    lines = [
        f"# AI Paper Digest — {date}",
        "",
        f"- Newly archived papers: **{len(papers)}**",
        f"- arXiv candidates retrieved: **{source_count}**",
        "- Scores represent **keyword relevance only**, not research quality.",
        "- Summaries reflect abstracts, not full-text verification.",
        "",
    ]
    for i, paper in enumerate(papers, start=1):
        lines.extend([
            f"## {i}. {md_safe(paper['title'])}",
            "",
            f"- arXiv: {paper['url']}",
            f"- Published (UTC): {paper['published']}",
            f"- Topics: {', '.join(paper['topics'])}",
            f"- Keyword relevance: {paper['relevance_score']}/100",
            f"- Authors: {md_safe(', '.join(paper['authors'][:8]))}",
            f"- Summary ({paper['summary_type']}): {md_safe(paper['summary'])}",
            "",
        ])
    return "\n".join(lines)


def run(now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    days = max(1, min(int(os.getenv("LOOKBACK_DAYS", "7")), 30))
    size = max(10, min(int(os.getenv("MAX_RESULTS", "150")), 500))
    max_new = max(1, min(int(os.getenv("MAX_NEW_PER_RUN", "15")), 50))
    current = read_existing(DATA_PATH)
    seen = {p["id"] for p in current}
    candidates = fetch_papers(size)
    eligible = []
    for paper in candidates:
        if paper["id"] in seen or not is_recent(paper, now, days):
            continue
        topics, score = classify(paper)
        if not topics or score < 15:
            continue
        paper["topics"] = topics
        paper["relevance_score"] = score
        eligible.append(paper)
        seen.add(paper["id"])
        if len(eligible) >= max_new:
            break
    if not eligible:
        print(f"No new relevant papers among {len(candidates)} candidates; no changes.")
        return 0

    key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    for paper in eligible:
        paper["summary"] = fallback_summary(paper["abstract"])
        paper["summary_type"] = "abstract excerpt"
        if key:
            try:
                paper["summary"] = llm_summary(paper, key, model)
                paper["summary_type"] = f"LLM ({model})"
            except (urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError) as exc:
                print(f"LLM summary unavailable for {paper['id']}: {type(exc).__name__}")
        paper["collected_at"] = now.isoformat()

    # Write only after collecting/summarizing, to avoid inconsistent partial state.
    updated = current + eligible
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    date = now.astimezone(timezone(timedelta(hours=9))).date().isoformat()
    report = make_report(eligible, date, len(candidates))
    (REPORT_DIR / f"{date}.md").write_text(report, encoding="utf-8")
    (REPORT_DIR / "LATEST.md").write_text(report, encoding="utf-8")
    DATA_PATH.write_text(
        json.dumps(updated, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Archived {len(eligible)} new papers on {date}.")
    return len(eligible)


if __name__ == "__main__":
    run()
