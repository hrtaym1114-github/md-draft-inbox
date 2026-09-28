"""Extract a plain Markdown draft and its stable identifier."""

import re
import uuid
from pathlib import Path

MAX_BODY = 20000
ID_NAMESPACE_PREFIX = "md-draft-inbox:"


def extract_title(content: str, fallback: str) -> str:
    match = re.search(r"^#[ \t]+(.+)", content, re.M)
    return match[1].strip() if match else fallback


def extract_body(content: str, section: str = "投稿文") -> str:
    lines = content.splitlines()
    found = False
    fence = None
    body_lines = []
    for line in lines:
        marker = re.match(r"^\s*(`{3,})(.*)$", line)
        if fence is not None:
            if marker and len(marker[1]) >= fence and not marker[2].strip():
                fence = None
            if found:
                body_lines.append(line)
            continue
        if marker:
            fence = len(marker[1])
        heading = re.match(r"^##[ \t]+(.*)$", line)
        if heading:
            if found:
                break
            if heading[1].strip() == section:
                found = True
            continue
        if found:
            body_lines.append(line)
    if not found:
        raise ValueError(f"Missing section: {section}")
    if fence is not None:
        raise ValueError("Unclosed body fence")
    body = "\n".join(body_lines).strip()
    if body.startswith("```"):
        fenced = re.match(r"^(`{3,})[^\n]*\n(.*?)\n\1`*[ \t]*(?:\n|$)", body, re.S)
        if not fenced:
            raise ValueError("Unclosed body fence")
        body = fenced[2].strip()
    body = re.sub(r"(?:^|\n)---\s*$", "", body).strip()
    if not body or len(body) > MAX_BODY:
        raise ValueError(f"Body must contain 1–{MAX_BODY} characters")
    return body


def build_payload(path: Path, section: str = "投稿文") -> dict:
    content = path.read_text(encoding="utf-8")
    title = extract_title(content, path.stem)[:100]
    body = extract_body(content, section)
    source = path.name
    draft_id = str(uuid.uuid5(
        uuid.NAMESPACE_URL,
        ID_NAMESPACE_PREFIX + source + "\n" + title + "\n" + body,
    ))
    return {"id": draft_id, "title": title, "body": body, "source": source}
