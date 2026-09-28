# md-draft-inbox

判定の次は人の受信箱。エージェントや日次ジョブが生成した Markdown 下書きを、人が読んで承認する inbox に送る小さな CLI です。投稿・予約は行いません。

Send Markdown drafts to a human-approval inbox after your quality gate. Generated drafts need a place for people to review them. This CLI creates inbox drafts only: **never publish to X**, and never automatically approve or schedule anything. The receiving inbox is responsible for the human review workflow.

## Install / インストール

Python 3.10+; no runtime dependencies. From the source checkout:

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/md-draft-inbox examples/pass.md --dry-run
```

After installation, use `md-draft-inbox` from the active environment, or `python -m md_draft_inbox`.

## Configuration / 環境変数

| Variable | Live / 実送信 | Dry run |
| --- | --- | --- |
| `MD_DRAFT_INBOX_URL` | Required: your inbox draft-create endpoint | Unused |
| `MD_DRAFT_INBOX_TOKEN` | Required: Bearer token for draft creation | Unused |

URL やトークンは環境変数で指定します。設定ファイルは読みません。下書き作成用の権限を持つトークンを利用してください。
Use a token scoped to draft creation. No configuration files are read.

## Usage / 使い方

```sh
# Parse only: no network or credentials required / 通信なし
md-draft-inbox examples/pass.md --dry-run
md-draft-inbox examples/pass.md --dry-run --json

# Set your own endpoint and token / 自分の inbox を設定
export MD_DRAFT_INBOX_URL='<your inbox draft-create URL>'
export MD_DRAFT_INBOX_TOKEN='<your draft-create token>'
md-draft-inbox examples/pass.md

# Multiple files and a custom section / 複数ファイル・本文見出し変更
md-draft-inbox first.md second.md --section Draft --adapter studio
```

The first `#` heading supplies the title; otherwise the filename stem is used. Titles are truncated to 100 characters. The body comes from `## 投稿文` (or the exact `--section` heading), ending at the next level-two heading outside a fence. An enclosing triple-backtick fence is unwrapped; a trailing `---` separator is removed. Missing sections, empty bodies, unclosed fences, and bodies over 20,000 characters fail that file.

タイトルは `#` 見出し（無ければ拡張子を除くファイル名）、本文は `## 投稿文` から抽出します。`--section` で変更できます。コードフェンスと末尾の区切り線を除去し、本文が空・見出しなし・フェンス未閉鎖・20,000文字超の場合は失敗します。

The sole adapter, `studio`, sends `{id, title, body, source}` as UTF-8 JSON via HTTP POST with Bearer authentication. `source` is the filename only. The stable ID is:

```python
uuid.uuid5(uuid.NAMESPACE_URL,
           'md-draft-inbox:' + source + '\n' + title[:100] + '\n' + body)
```

Moving a file without renaming or changing its extracted content preserves its ID. Retrying preserves the ID; duplicate handling depends on the inbox. Files are never modified. The response must be valid JSON; HTTP errors fail the file. No particular receipt fields are required.

原稿は変更しません。同じファイル名と抽出内容で再実行すると同じ ID になります。重複処理は inbox 側の実装によります。

`--json` writes one object per file to stdout with `ok`, `path`, and `dry_run`; successes add `id`, `title`, and `chars`, while failures add `error`. Errors also go to stderr. Processing continues after a failed file, including missing live configuration.

## Exit codes / 終了コード

| Code | Meaning / 意味 |
| --- | --- |
| 0 | All files succeeded / 全ファイル成功 |
| 1 | At least one file failed / いずれか失敗 |
| 2 | Invalid CLI arguments / 引数エラー |

## Development / 開発

```sh
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest -q
```

Related quality gate: [x-jev-gate](https://github.com/hrtaym1114-github/x-jev-gate).

MIT © 2026 hrtaym1114
