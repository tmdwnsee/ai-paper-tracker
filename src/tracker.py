"""Daily arXiv metadata collector and research digest.

Standard-library only for metadata; optional Gemini PDF summaries require GEMINI_API_KEY.
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

from .fulltext import summarize_fulltext

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
    def matches(text: str, term: str) -> bool:
        return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", text) is not None

    labels = [name for name, terms in TOPICS.items() if any(matches(body, t) for t in terms)]
    strong = sum(1 for term in STRONG_TERMS if matches(body, term))
    score = min(100, strong * 15 + sum(10 for term in STRONG_TERMS if matches(title, term)))
    return labels, score


def is_recent(paper: dict, now: datetime, days: int) -> bool:
    try:
        published = datetime.fromisoformat(paper["published"].replace("Z", "+00:00"))
    except ValueError:
        return False
    return now - timedelta(days=days) <= published <= now + timedelta(minutes=5)


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
        f"- 한국어 PDF 본문 요약 완료: **{len(papers)}편**",
        f"- arXiv candidates retrieved: **{source_count}**",
        "- Scores represent **keyword relevance only**, not research quality.",
        "- 완료된 한국어 PDF 본문 요약만 표시합니다. 실패·미완료 결과는 저장하지 않습니다.",
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
            f"- Summary source: {paper.get('summary_type', 'pending')}",
            f"- PDF pages: {paper.get('pdf_pages', 'not processed')}",
            "",
            paper.get("summary", "한국어 본문 요약 대기 중"),
            "",
        ])
    return "\n".join(lines)


def run(now: datetime | None = None) -> int:
    """Persist and publish ONLY successfully summarized Korean full-text papers."""
    now = now or datetime.now(timezone.utc)
    days = max(1, min(int(os.getenv("LOOKBACK_DAYS", "7")), 30))
    size = max(10, min(int(os.getenv("MAX_RESULTS", "150")), 500))
    max_fulltext = max(0, min(int(os.getenv("MAX_FULLTEXT_PER_RUN", "1")), 10))
    current = [p for p in read_existing(DATA_PATH)
               if p.get("summary_type") == "fulltext_llm_ko" and p.get("summary", "").strip()]
    seen = {p["id"] for p in current}
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or max_fulltext == 0:
        print("No Gemini API key or summarization disabled. Nothing to publish.")
        return 0

    candidates = fetch_papers(size)
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    summarized = []
    attempts = 0
    for paper in candidates:
        if paper["id"] in seen or not is_recent(paper, now, days):
            continue
        topics, score = classify(paper)
        if not topics or score < 30:
            continue
        paper["topics"] = topics
        paper["relevance_score"] = score
        attempts += 1
        try:
            summary, pages, chunks = summarize_fulltext(paper, key, model)
            paper["summary"] = summary
            paper["summary_type"] = "fulltext_llm_ko"
            paper["pdf_pages"] = pages
            paper["text_chunks"] = chunks
            paper["collected_at"] = now.isoformat()
            summarized.append(paper)
            seen.add(paper["id"])
            print(f"Full-text Korean summary: {paper['id']} ({pages} pages, {chunks} chunks)")
        except Exception as exc:
            print(f"Full-text summary failed for {paper['id']}: {type(exc).__name__}: {str(exc)[:160]}")
            # Do not save incomplete/abstract-only records; retry in a future run.
            if "quota exceeded" in str(exc):
                print("Gemini quota reached; stopping this run.")
                break
        if attempts >= max_fulltext:
            break

    if not summarized:
        print(f"No completed Korean full-text summaries among {len(candidates)} candidates.")
        return 0

    updated = current + summarized
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    date = now.astimezone(timezone(timedelta(hours=9))).date().isoformat()
    # Keep the day's successfully processed papers in the daily report.
    daily = [p for p in updated if p.get("collected_at", "")[:10] == now.date().isoformat()]
    report = make_report(daily, date, len(candidates))
    (REPORT_DIR / f"{date}.md").write_text(report, encoding="utf-8")
    (REPORT_DIR / "LATEST.md").write_text(report, encoding="utf-8")
    DATA_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(summarized)} fully summarized Korean papers; no unfinished results committed.")
    return len(summarized)


if __name__ == "__main__":
    run()
