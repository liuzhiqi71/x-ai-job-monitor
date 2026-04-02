from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import urlparse

import httpx

from .logging_utils import get_logger


@dataclass
class ExternalMetadata:
    requested_url: str
    final_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class _HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts = []
        self.description = None
        self.og_title = None
        self.og_description = None

    def handle_starttag(self, tag, attrs) -> None:
        if tag.lower() == "title":
            self.in_title = True
            return
        if tag.lower() != "meta":
            return

        attrs_map = {key.lower(): value for key, value in attrs if key}
        name = (attrs_map.get("name") or "").lower()
        prop = (attrs_map.get("property") or "").lower()
        content = attrs_map.get("content")
        if not content:
            return
        if name == "description":
            self.description = content
        if prop == "og:title":
            self.og_title = content
        if prop == "og:description":
            self.og_description = content

    def handle_endtag(self, tag) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> Optional[str]:
        joined = unescape(" ".join(self.title_parts)).strip()
        return joined or None


def _host_only(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or "unknown-host"


def fetch_external_metadata(
    url: str,
    timeout_seconds: int,
    user_agent: str,
) -> ExternalMetadata:
    logger = get_logger(__name__)
    result = ExternalMetadata(requested_url=url, final_url=url)
    if not url:
        return result

    headers = {"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"}
    timeout = httpx.Timeout(timeout_seconds, connect=min(timeout_seconds, 5))

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
            response = client.get(url)
            response.raise_for_status()
            result.final_url = str(response.url)
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type.lower():
                return result
            parser = _HeadParser()
            parser.feed(response.text[:200_000])
            result.title = parser.og_title or parser.title
            result.description = parser.og_description or parser.description
            return result
    except httpx.HTTPError as exc:
        logger.warning(
            "External metadata fetch failed host=%s error=%s",
            _host_only(url),
            exc.__class__.__name__,
        )
        return result

