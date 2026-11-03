import unittest
from datetime import datetime, timezone

from src.tracker import arxiv_id, classify, is_recent, make_report, parse_feed


SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2601.12345v2</id>
    <title>Retrieval-Augmented Generation for Scientific Search</title>
    <summary>We study retrieval-augmented generation and retriever design.</summary>
    <published>2026-11-02T12:00:00Z</published>
    <updated>2026-11-02T12:00:00Z</updated>
    <author><name>Alice Researcher</name></author>
    <category term="cs.CL"/>
  </entry>
</feed>"""


class TrackerTests(unittest.TestCase):
    def test_id_removes_version(self):
        self.assertEqual(arxiv_id("https://arxiv.org/abs/2601.12345v3"), "2601.12345")

    def test_feed_parsing(self):
        paper = parse_feed(SAMPLE)[0]
        self.assertEqual(paper["id"], "2601.12345")
        self.assertEqual(paper["categories"], ["cs.CL"])
        self.assertEqual(paper["authors"], ["Alice Researcher"])

    def test_classification(self):
        paper = parse_feed(SAMPLE)[0]
        topics, score = classify(paper)
        self.assertIn("RAG", topics)
        self.assertGreater(score, 0)

    def test_freshness(self):
        paper = parse_feed(SAMPLE)[0]
        self.assertTrue(is_recent(paper, datetime(2026, 11, 3, tzinfo=timezone.utc), 7))
        self.assertFalse(is_recent(paper, datetime(2026, 12, 3, tzinfo=timezone.utc), 7))

    def test_report(self):
        paper = parse_feed(SAMPLE)[0]
        paper.update(topics=["RAG"], relevance_score=45, summary="Abstract excerpt", summary_type="abstract excerpt")
        report = make_report([paper], "2026-11-03", 10)
        self.assertIn("arxiv.org/abs/2601.12345", report)
        self.assertIn("keyword relevance", report)


if __name__ == "__main__":
    unittest.main()
