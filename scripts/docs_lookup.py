#!/usr/bin/env python3
"""Simple docs lookup and JSONL evidence generator.

Usage (basic):
  python3 scripts/docs_lookup.py --query "dependency injection" --stack python --out /tmp/docs.jsonl

The script accepts a registry file (JSON) mapping stacks to lists of doc URLs.
If not provided, a small curated default registry is used.

This is intentionally small: it fetches pages, extracts text, chunks it, and
writes JSONL records for later agent consumption.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from typing import Dict, List, Any, cast
from urllib.request import Request, urlopen
# urllib errors are not explicitly handled; imports removed to avoid unused warnings


DEFAULT_REGISTRY: Dict[str, List[str]] = {
    "python": ["https://docs.python.org/3/"],
    "fastapi": ["https://fastapi.tiangolo.com/en/latest/"],
    "django": ["https://docs.djangoproject.com/en/stable/"],
    "typescript": ["https://www.typescriptlang.org/docs/"],
    "react": ["https://reactjs.org/docs/"],
    "nextjs": ["https://nextjs.org/docs/"],
}


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._texts: List[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: List[Any]) -> None:
        if tag in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = data.strip()
            if text:
                self._texts.append(text)

    def get_text(self) -> str:
        return " ".join(self._texts)


def fetch_url(url: str, timeout: int = 10) -> str:
    """Fetch a URL and return its text content.

    Errors are allowed to propagate naturally; no explicit handling is required.
    """
    req = Request(url, headers={"User-Agent": "JACK-DocsLookup/0.1"})
    with urlopen(req, timeout=timeout) as resp:
        b = resp.read()
        try:
            return b.decode("utf-8")
        except Exception:
            return b.decode("latin-1", errors="ignore")


def extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    if m:
        return unescape(re.sub(r"\s+", " ", m.group(1).strip()))
    return ""


def extract_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    try:
        parser.feed(html)
        text = parser.get_text()
        # normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return unescape(text)
    except Exception:
        # last-resort fallback: strip tags
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        return unescape(text)


def chunk_text(text: str, chunk_size: int = 800) -> List[str]:  # noqa: C901
    """Split *text* into word chunks of roughly *chunk_size* characters.

    Very short chunks (<30 chars) are dropped and duplicate chunks are removed.
    This straightforward implementation keeps cognitive complexity low.
    """
    words = text.split()
    if not words:
        return []
    chunks: List[str] = []
    # Process words in fixed-size steps to avoid nested loops.
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk) >= 30 and chunk not in chunks:
            chunks.append(chunk)
    return chunks


def load_registry(path: str | None) -> Dict[str, List[str]]:
    if path:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                # normalize to stack->list
                out: Dict[str, List[str]] = {}
                for k, v in data.items():
                    if isinstance(v, str):
                        out[k] = [v]
                    elif isinstance(v, list):
                            # Convert entries to strings; ignore type checker warnings about unknown element types.
                            out[k] = [str(x) for x in v]  # type: ignore[arg-type]
                return out
        except Exception:
            print("Warning: failed to load registry file, using default registry", file=sys.stderr)
    return DEFAULT_REGISTRY.copy()


def make_record(query: str, stack: str, source_url: str, title: str, chunk_text: str, idx: int) -> Dict[str, Any]:
    return {
        "query": query,
        "stack": stack,
        "source_url": source_url,
        "title": title,
        "chunk_text": chunk_text,
        "chunk_index": idx,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source_type": "official-docs",
        "trust_level": "high",
    }


def _process_stack(stack: str, urls: List[str], query: str, chunk_size: int) -> List[Dict[str, Any]]:
    """Fetch each URL for a stack, extract text, chunk it and return records."""
    records_by_url: List[List[Dict[str, Any]]] = []
    for url in urls:
        try:
            html = fetch_url(url)
        except Exception as e:
            print(f"Warning: failed to fetch {url}: {e}", file=sys.stderr)
            continue
        title = extract_title(html)
        text = extract_text(html)
        chunks = chunk_text(text, chunk_size=chunk_size)
        url_records: List[Dict[str, Any]] = []
        for idx, ch in enumerate(chunks):
            rec = make_record(query, stack, url, title, ch, idx)
            url_records.append(rec)
        records_by_url.append(url_records)

    stack_records: List[Dict[str, Any]] = []
    max_len = max((len(records) for records in records_by_url), default=0)
    for idx in range(max_len):
        for records in records_by_url:
            if idx < len(records):
                stack_records.append(records[idx])
    return stack_records

def _find_matches(records: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Return top matching records for the query, sorted by score descending."""
    q = query.strip().lower()
    if not q:
        return []
    matches: List[Dict[str, Any]] = []
    for rec in records:
        chunk = cast(str, rec.get("chunk_text", ""))
        score = chunk.lower().count(q)
        if score:
            matches.append({
                "score": score,
                "stack": rec.get("stack"),
                "source_url": rec.get("source_url"),
                "chunk_index": rec.get("chunk_index"),
                "excerpt": chunk[:200],
            })
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

def main(argv: List[str] | None = None) -> int:  # noqa: C901
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--stack", help="Optional stack name to limit search")
    ap.add_argument("--registry-file", help="Optional JSON file mapping stacks to doc URLs")
    ap.add_argument("--out", help="Output JSONL file", default="docs_lookup.jsonl")
    ap.add_argument("--chunk-size", type=int, default=800)
    ap.add_argument("--overlap", type=int, default=100)
    args = ap.parse_args(argv)

    registry = load_registry(args.registry_file)
    targets = [args.stack] if args.stack else list(registry.keys())

    # Gather records across all stacks
    records: List[Dict[str, Any]] = []
    for stack in targets:
        urls = registry.get(stack) or []
        records.extend(_process_stack(stack, urls, args.query, args.chunk_size))

    # Write JSONL output
    try:
        with open(args.out, "w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error: failed to write output {args.out}: {e}", file=sys.stderr)
        return 2

    matches = _find_matches(records, args.query)

    print(f"Wrote {len(records)} chunk records to {args.out}")
    if matches:
        print("Top matches:")
        for m in matches[:5]:
            print(f"- [{m['stack']}] {m['source_url']} (chunk {m['chunk_index']}) score={m['score']}")
            print(f"  excerpt: {m['excerpt']}")
    else:
        print("No matches found for query in fetched docs.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

