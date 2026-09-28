"""Send Markdown drafts to a human-approval inbox."""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import URLError

from .parse import build_payload
from .send import send_draft


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", help="One JSON object per file")
    parser.add_argument("--section", default="投稿文")
    parser.add_argument("--adapter", choices=["studio"], default="studio")
    args = parser.parse_args(argv)
    failures = 0
    for path in args.files:
        result = {"ok": True, "path": str(path), "dry_run": args.dry_run}
        try:
            data = build_payload(path, args.section)
            if not args.dry_run:
                url = os.environ.get("MD_DRAFT_INBOX_URL", "").strip()
                token = os.environ.get("MD_DRAFT_INBOX_TOKEN", "").strip()
                missing = [name for name, value in (
                    ("MD_DRAFT_INBOX_URL", url), ("MD_DRAFT_INBOX_TOKEN", token)
                ) if not value]
                if missing:
                    raise ValueError("Missing configuration: " + ", ".join(missing))
                try:
                    send_draft(data, url, token)
                except (OSError, URLError, ValueError) as exc:
                    # Avoid exposing credentials or server response text.
                    raise ValueError(f"Inbox request failed ({type(exc).__name__})") from None
            result.update(id=data["id"], title=data["title"], chars=len(data["body"]))
            if not args.json:
                if args.dry_run:
                    print(f"Draft: {path.name} title={data['title']!r} "
                          f"({len(data['body'])} chars, id={data['id']})")
                else:
                    print(f"Inbox draft saved: {path.name} id={data['id']}")
        except (OSError, ValueError) as exc:
            failures += 1
            result.update(ok=False, error=str(exc))
            print(f"Failed: {path.name}: {exc}", file=sys.stderr)
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
    return 1 if failures else 0
