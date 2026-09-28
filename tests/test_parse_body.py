import pytest

from md_draft_inbox.parse import MAX_BODY, build_payload, extract_body, extract_title


def test_heading_and_separator():
    assert extract_body('# Title\n## 投稿文\nhello\n---\n## Notes\nignored') == 'hello'
    assert extract_title('# Title\n## 投稿文\nhello', 'fallback') == 'Title'
    assert extract_title('## Section', 'fallback') == 'fallback'


def test_fenced_body():
    assert extract_body('## 投稿文\n```text\nhello\n## inside\n```\n---') == 'hello\n## inside'


def test_custom_section():
    assert extract_body('## Draft.*\nhello', 'Draft.*') == 'hello'


@pytest.mark.parametrize('content', [
    '# Missing', '## 投稿文\n', '## 投稿文\n---',
    '## 投稿文\n```\n\n```', '## 投稿文\n```\nhello',
    '## 投稿文\n' + 'x' * (MAX_BODY + 1),
])
def test_invalid_body(content):
    with pytest.raises(ValueError):
        extract_body(content)


def test_limit():
    assert len(extract_body('## 投稿文\n' + 'x' * MAX_BODY)) == MAX_BODY


def test_payload_fallback(tmp_path):
    path = tmp_path / 'draft.md'
    path.write_text('## 投稿文\n本文', encoding='utf-8')
    assert build_payload(path)['title'] == 'draft'
