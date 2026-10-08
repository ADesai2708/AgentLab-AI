import ipaddress
import socket
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from researchops.cache import SQLiteCache
from researchops.models import FetchParams, FetchResult


MAX_REDIRECTS = 3

BLOCKED_CONTENT_TYPES = {
    "application/x-executable",
    "application/octet-stream",
}


def validate_url(url: str):

    parsed = urlparse(url)

    if parsed.scheme not in {
        "http",
        "https"
    }:
        raise ValueError(
            "Only HTTP and HTTPS URLs are allowed."
        )

    if parsed.username or parsed.password:
        raise ValueError(
            "URLs containing credentials are not allowed."
        )

    hostname = parsed.hostname

    if not hostname:
        raise ValueError(
            "URL does not contain a hostname."
        )

    if hostname.lower() in {
        "localhost",
        "localhost.localdomain"
    }:
        raise ValueError(
            "Localhost URLs are blocked."
        )

    try:

        addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM
        )

    except socket.gaierror as exc:

        raise ValueError(
            "Hostname could not be resolved."
        ) from exc

    for address in addresses:

        ip = ipaddress.ip_address(
            address[4][0]
        )

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):

            raise ValueError(
                f"Blocked destination IP: {ip}"
            )


class SecureFetchTool:

    def __init__(
        self,
        cache: SQLiteCache
    ):

        self.cache = cache

        self.timeout = 15

        self.max_bytes = 2_000_000
    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(
        multiplier=0.5,
        min=0.5,
        max=4
    ),
    retry=retry_if_exception_type(
        (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RemoteProtocolError
        )
    )
)

    def fetch(
        self,
        params: FetchParams
    ) -> FetchResult:

        cache_key = self.cache.create_key(
            "fetch",
            params.model_dump(mode="json")
        )

        cached = self.cache.get(
            cache_key
        )

        if cached is not None:

            print("FETCH CACHE HIT")

            return FetchResult.model_validate(
                cached
            )

        print("FETCH CACHE MISS")

        result = self._fetch(
            str(params.url),
            params.max_chars
        )

        self.cache.set(
            cache_key,
            result.model_dump(mode="json")
        )

        return result

    def _fetch(
        self,
        url: str,
        max_chars: int
    ) -> FetchResult:

        current_url = url

        headers = {
            "User-Agent": (
                "ResearchOps/0.1 "
                "(research-fetcher)"
            ),
            "Accept": (
                "text/html,"
                "application/xhtml+xml,"
                "text/plain"
            )
        }

        with httpx.Client(
            timeout=self.timeout,
            follow_redirects=False,
            headers=headers
        ) as client:

            for _ in range(
                MAX_REDIRECTS + 1
            ):

                validate_url(
                    current_url
                )

                response = client.get(
                    current_url
                )

                if response.status_code in {
                    301,
                    302,
                    303,
                    307,
                    308
                }:

                    location = response.headers.get(
                        "location"
                    )

                    if not location:

                        raise ValueError(
                            "Redirect without Location."
                        )

                    from urllib.parse import urljoin

                    current_url = urljoin(
                        current_url,
                        location
                    )

                    continue

                response.raise_for_status()

                break

            else:

                raise ValueError(
                    "Too many redirects."
                )

        content_type = (
            response
            .headers
            .get(
                "content-type",
                ""
            )
            .split(";")[0]
            .lower()
        )

        if content_type in BLOCKED_CONTENT_TYPES:

            raise ValueError(
                f"Blocked content type: "
                f"{content_type}"
            )

        body = response.content[
            :self.max_bytes
        ]

        truncated_bytes = (
            len(response.content)
            > self.max_bytes
        )

        if (
            "text/html" in content_type
            or
            "application/xhtml+xml"
            in content_type
        ):

            soup = BeautifulSoup(
                body,
                "html.parser"
            )

            for tag in soup(
                [
                    "script",
                    "style",
                    "noscript",
                    "svg",
                    "canvas",
                    "iframe"
                ]
            ):

                tag.decompose()

            title = ""

            if soup.title:

                title = soup.title.get_text(
                    " ",
                    strip=True
                )

            text = soup.get_text(
                " ",
                strip=True
            )

        else:

            title = ""

            text = body.decode(
                "utf-8",
                errors="replace"
            )

        text = text[:max_chars]

        return FetchResult(
            url=current_url,
            title=title,
            text=text,
            content_type=(
                content_type
                or "application/octet-stream"
            ),
            truncated=(
                truncated_bytes
                or len(text) >= max_chars
            )
        )