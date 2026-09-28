import json
from pathlib import Path
import subprocess
import sys

import pytest

from md_draft_inbox import cli

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'examples' / 'pass.md'


@pytest.fixture(autouse=True)
def no_network_or_env(monkeypatch):
    monkeypatch.delenv('MD_DRAFT_INBOX_URL', raising=False)
    monkeypatch.delenv('MD_DRAFT_INBOX_TOKEN', raising=False)

    def unexpected(*args, **kwargs):
        pytest.fail('Unexpected network attempt')

    monkeypatch.setattr(cli, 'send_draft', unexpected)


def test_dry_run(capsys):
    assert cli.main([str(EXAMPLE), '--dry-run']) == 0
    output = capsys.readouterr()
    assert output.out.startswith("Draft: pass.md title='A draft for review'")
    assert 'chars, id=' in output.out
    assert not output.err


def test_json_and_continue(tmp_path, capsys):
    assert cli.main([str(tmp_path / 'missing.md'), str(EXAMPLE), '--dry-run', '--json']) == 1
    output = capsys.readouterr()
    failed, success = map(json.loads, output.out.splitlines())
    assert failed['ok'] is False and failed['error']
    assert success['ok'] is True and success['id'] and success['chars'] > 0
    assert output.err


@pytest.mark.parametrize('configured', [None, 'MD_DRAFT_INBOX_URL', 'MD_DRAFT_INBOX_TOKEN'])
def test_live_missing_configuration(monkeypatch, capsys, configured):
    if configured:
        monkeypatch.setenv(configured, 'test-value')
    assert cli.main([str(EXAMPLE), '--json']) == 1
    output = capsys.readouterr()
    assert 'Missing configuration' in json.loads(output.out)['error']


def test_live_success(monkeypatch, capsys):
    monkeypatch.setenv('MD_DRAFT_INBOX_URL', 'https://example.test/inbox')
    monkeypatch.setenv('MD_DRAFT_INBOX_TOKEN', 'test-token')
    calls = []
    monkeypatch.setattr(cli, 'send_draft', lambda *args: calls.append(args) or {})
    assert cli.main([str(EXAMPLE)]) == 0
    assert len(calls) == 1
    assert calls[0][1:] == ('https://example.test/inbox', 'test-token')
    assert capsys.readouterr().out.startswith('Inbox draft saved: pass.md id=')


def test_module():
    result = subprocess.run([sys.executable, '-m', 'md_draft_inbox', str(EXAMPLE), '--dry-run', '--json'], capture_output=True, text=True)
    assert result.returncode == 0
    assert json.loads(result.stdout)['ok'] is True
