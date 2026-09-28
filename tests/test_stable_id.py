import uuid

from md_draft_inbox.parse import ID_NAMESPACE_PREFIX, build_payload


def test_stable_id_and_namespace(tmp_path):
    path = tmp_path / 'draft.md'
    path.write_text('# Title\n## 投稿文\n本文', encoding='utf-8')
    first = build_payload(path)
    assert first == build_payload(path)
    assert ID_NAMESPACE_PREFIX == 'md-draft-inbox:'
    assert first['id'] == str(uuid.uuid5(uuid.NAMESPACE_URL, 'md-draft-inbox:draft.md\nTitle\n本文'))
    assert set(first) == {'id', 'title', 'body', 'source'}
    folder = tmp_path / 'moved'
    folder.mkdir()
    moved = path.rename(folder / path.name)
    assert build_payload(moved) == first
    moved.write_text('# Title\n## 投稿文\nChanged', encoding='utf-8')
    assert build_payload(moved)['id'] != first['id']


def test_truncated_title(tmp_path):
    path = tmp_path / 'draft.md'
    path.write_text('# ' + 'T' * 120 + '\n## 投稿文\nBody', encoding='utf-8')
    data = build_payload(path)
    assert data['title'] == 'T' * 100
    assert data['id'] == str(uuid.uuid5(uuid.NAMESPACE_URL, 'md-draft-inbox:draft.md\n' + 'T' * 100 + '\nBody'))
