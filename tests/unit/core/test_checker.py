from pathlib import Path
import respx
import httpx
from diffwatch.core.checker import CheckStatus, parse_and_hash, compute_hash, check

FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "html_samples"
def _load_fixture(filename: str) -> str:
    return (FIXTURE_DIR / filename).read_text()

def test_parse_and_hash_success():
    html = _load_fixture("sample_page.html")
    res = parse_and_hash(html, "#product-price")

    assert res.status == CheckStatus.OK
    assert res.hash == compute_hash("€ 49.99".encode())
    assert res.error is None

def test_selector_not_found():
    html = _load_fixture("sample_page.html")
    res = parse_and_hash(html, ".non-existing-selector")

    assert res.status == CheckStatus.SELECTOR_NOT_FOUND
    assert res.hash is None

@respx.mock
def test_check_success_includes_http_status_code():
    URL = "http://test.com"
    mocked_fetch = respx.get(URL).mock(
        return_value=httpx.Response(200, text="<body>content</body>")
    )
    res = check(URL)

    assert mocked_fetch.called
    assert res.status == CheckStatus.OK
    assert res.http_status_code == 200

@respx.mock
def test_check_http_error():
    URL = "http://test.com"
    mocked_fetch = respx.get(URL).mock(return_value=httpx.Response(500))
    res = check(URL)

    assert mocked_fetch.called
    assert res.status == CheckStatus.HTTP_ERROR
    assert res.error is not None
    assert res.http_status_code == 500

@respx.mock
def test_check_blocked_error():
    URL = "http://test.com"
    mocked_fetch = respx.get(URL).mock(return_value=httpx.Response(401))
    res = check(URL)

    assert mocked_fetch.called
    assert res.status == CheckStatus.BLOCKED
    assert res.error is not None
    assert res.http_status_code == 401
