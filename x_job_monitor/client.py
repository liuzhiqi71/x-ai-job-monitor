from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from .logging_utils import get_logger

TWEET_FIELDS = ",".join(
    [
        "author_id",
        "created_at",
        "entities",
        "lang",
        "public_metrics",
    ]
)
USER_FIELDS = "id,name,username"


class XRecentSearchClient:
    def __init__(
        self,
        bearer_token: str,
        base_url: str,
        timeout_seconds: int,
        connect_timeout_seconds: int,
        user_agent: str,
    ) -> None:
        self.bearer_token = bearer_token
        self.base_url = base_url.rstrip("/")
        self.logger = get_logger(__name__)
        timeout = httpx.Timeout(timeout_seconds, connect=connect_timeout_seconds)
        self._client = httpx.Client(timeout=timeout, follow_redirects=True)
        self.user_agent = user_agent

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "XRecentSearchClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": self.user_agent,
        }

    def search_recent(
        self,
        query: str,
        query_name: str,
        max_results: int,
        since_id: Optional[str] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        endpoint = "/tweets/search/recent"
        params: Dict[str, Any] = {
            "query": query,
            "max_results": max(10, min(max_results, 100)),
            "expansions": "author_id",
            "tweet.fields": TWEET_FIELDS,
            "user.fields": USER_FIELDS,
        }
        if since_id:
            params["since_id"] = since_id
        if next_token:
            params["next_token"] = next_token

        try:
            response = self._client.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            self.logger.error(
                "X API request failed endpoint=%s query=%s status_code=%s",
                endpoint,
                query_name,
                exc.response.status_code,
            )
            raise
        except httpx.HTTPError as exc:
            self.logger.error(
                "X API request failed endpoint=%s query=%s error=%s",
                endpoint,
                query_name,
                exc.__class__.__name__,
            )
            raise

