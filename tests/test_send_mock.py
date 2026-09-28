import io
import json
from pathlib import Path
import re
from urllib.error import HTTPError

import pytest

from md_draft_inbox import cli, send


def test_post(monkeypatch):
    data = {'id': 'a', 'title': 'Title', 'body': '本文', 'source': 'draft.md'}
    url = 'https://example.test/inbox'

    def urlopen(request, timeout):
        assert request.full_url == url
        assert request.method == 'POST'
        assert request.get_header('Authorization') == 'Bearer test-token'
        assert request.get_header('Content-type') == 'application/json'
        assert json.loads(request.data) == data
        assert timeout == 30
        return io.BytesIO(b'{"accepted": true}')

    monkeypatch.setattr(send.urllib.request, 'urlopen', urlopen)
    assert send.send_draft(data, url, 'test-token') == {'accepted': True}


def test_http_error(monkeypatch):
    def urlopen(request, timeout):
        raise HTTPError(request.full_url, 403, 'Denied', {}, None)

    monkeypatch.setattr(send.urllib.request, 'urlopen', urlopen)
    with pytest.raises(HTTPError):
        send.send_draft({}, 'https://example.test/inbox', 'test-token')


def test_only_inbox_code():
    for module in (send, cli):
        assert not re.search(r'publish|schedule', Path(module.__file__).read_text(), re.I)
