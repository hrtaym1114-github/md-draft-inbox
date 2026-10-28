日本語: [README.md](README.md)
# md-draft-inbox

After the quality gate comes the human inbox. This small CLI places Markdown drafts created by agents or daily jobs **only in an inbox for human review and approval**.

Send Markdown drafts to a human-approval inbox after your quality gate.  
**Never publish to X.** Never auto-approve or schedule. Inbox POST only.

[![dry-run → inbox](docs/media/md-draft-inbox-strip.png)](docs/media/md-draft-inbox-howto.gif)

- 🎞️ [GIF](docs/media/md-draft-inbox-howto.gif)
- Release: [v0.1.0](https://github.com/hrtaym1114-github/md-draft-inbox/releases/tag/v0.1.0)

## Getting started (4 steps)

1. **Install** — `pip install git+https://github.com/hrtaym1114-github/md-draft-inbox.git`
2. **Dry-run** — `md-draft-inbox examples/pass.md --dry-run` (no network access or keys required)
3. **Env (live sending only)** — `MD_DRAFT_INBOX_URL` / `MD_DRAFT_INBOX_TOKEN` (draft creation only)
4. **Result** — All files succeed: **exit 0** / Any file fails: **exit 1**

```sh
md-draft-inbox examples/pass.md --dry-run
# Draft: pass.md title='A draft for review' (65 chars, id=…)
```

## Install

Python ≥ 3.10. No runtime dependencies (standard library only).

```sh
# For first-time users (recommended)
pip install git+https://github.com/hrtaym1114-github/md-draft-inbox.git

# Development (this repository)
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/md-draft-inbox examples/pass.md --dry-run
.venv/bin/pytest -q
```

`python -m md_draft_inbox` works the same way.

## Configuration

| Variable | Live | Dry-run |
| --- | --- | --- |
| `MD_DRAFT_INBOX_URL` | Required: inbox draft-create URL | Not used |
| `MD_DRAFT_INBOX_TOKEN` | Required: Bearer token (draft creation only) | Not used |

No configuration files are read. The URL and token come only from environment variables. Do not supply tokens with broad permissions for publishing or scheduling.

## Usage

```sh
# No network access
md-draft-inbox examples/pass.md --dry-run
md-draft-inbox examples/pass.md --dry-run --json

# Live sending (your own inbox)
export MD_DRAFT_INBOX_URL='https://example.com/api/drafts'
export MD_DRAFT_INBOX_TOKEN='…'   # draft-create only
md-draft-inbox examples/pass.md

# Multiple files and a custom body heading
md-draft-inbox first.md second.md --section Draft --adapter studio
```

### Extraction rules

- **Title**: The first `#` heading, or the filename without its extension if absent. Truncated to 100 characters
- **Body**: Defaults to `## 投稿文` (change with `--section`). Runs up to the next h2 heading, outside code fences
- Enclosing triple-backtick fences are stripped. A trailing `---` is removed
- Missing body heading, empty body, unclosed fence, or body over 20,000 characters → that file fails

### Adapter `studio` (only option and default)

Sends UTF-8 JSON via HTTP POST with Bearer authentication. The payload is `{id, title, body, source}`. `source` contains only the filename.

Stable ID:

```python
uuid.uuid5(uuid.NAMESPACE_URL,
           'md-draft-inbox:' + filename + '\n' + title[:100] + '\n' + body)
```

The ID stays the same when a file is moved, as long as its name and extracted content remain unchanged. Draft files are not modified. The inbox handles duplicates. An HTTP error or invalid JSON causes that file to fail. No specific response fields are required.

`--json` outputs `ok` / `path` / `dry_run` for each file (`id` / `title` / `chars` on success, `error` on failure). Errors also go to stderr. Processing continues with the next file after a failure.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | All files succeeded |
| 1 | At least one file failed |
| 2 | Argument error |

## Non-goals

- **Publishing or scheduling APIs** for X / Typefully or similar services
- Automatic publishing or scheduling
- LLM editing or generation
- Enforcing a fixed folder layout

## Related

Upstream quality gate: [x-jev-gate](https://github.com/hrtaym1114-github/x-jev-gate)  
Collection gate: [news-collect-validate](https://github.com/hrtaym1114-github/news-collect-validate)

MIT © 2026 hrtaym1114
