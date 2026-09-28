"""Create drafts in the configured inbox using the standard library."""

import json
import urllib.request


def send_draft(data: dict, url: str, token: str, timeout: float = 30) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)
