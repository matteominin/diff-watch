from enum import Enum
from dataclasses import dataclass
import httpx
from selectolax.lexbor import LexborHTMLParser
import hashlib

class CheckStatus(Enum):
    OK = "ok"
    BLOCKED = "blocked"
    SELECTOR_NOT_FOUND = "selector_not_found"
    HTTP_ERROR = "http_error"

@dataclass
class CheckResult():
    status: CheckStatus
    hash: str | None = None
    error: str | None = None

def check(url: str, selector: str) -> str:
    try: 
        res = httpx.get(url, follow_redirects=True, 
            timeout=10.0, headers={"User-Agent": "diffwatch/0.1"})
    except httpx.RequestError as e:
        return CheckResult(status=CheckStatus.HTTP_ERROR, error=str(e))

    if res.status_code in (401, 403, 429):
        return CheckResult(status=CheckStatus.BLOCKED, error=f"HTTP status: {res.status_code}")
    if 400 <= res.status_code <= 599:
        return CheckResult(status=CheckStatus.HTTP_ERROR, error=f"HTTP {res.status_code}")

    tree = LexborHTMLParser(res.text)
    tree.strip_tags(['head', 'style', 'script', 'xmp', 'iframe', 'noembed', 'noframes'])
    node = tree.css_first(selector) if selector else tree

    if node is None:
        return CheckResult(status=CheckStatus.SELECTOR_NOT_FOUND)

    text = node.text(strip=True)
    return CheckResult(status=CheckStatus.OK, hash=hashlib.sha256(text.encode()).hexdigest())