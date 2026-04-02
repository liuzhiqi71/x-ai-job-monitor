from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class JobLead:
    tweet_id: str
    tweet_url: str
    author_username: str
    author_name: str
    created_at: str
    lang: Optional[str]
    text: str
    query_name: str
    matched_urls: List[str] = field(default_factory=list)
    external_url: Optional[str] = None
    external_final_url: Optional[str] = None
    external_title: Optional[str] = None
    external_description: Optional[str] = None
    public_metrics: Dict[str, Any] = field(default_factory=dict)
    raw_source: str = "x_recent_search"
    collected_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "JobLead":
        return cls(
            tweet_id=str(payload.get("tweet_id", "")),
            tweet_url=payload.get("tweet_url", ""),
            author_username=payload.get("author_username", ""),
            author_name=payload.get("author_name", ""),
            created_at=payload.get("created_at", ""),
            lang=payload.get("lang"),
            text=payload.get("text", ""),
            query_name=payload.get("query_name", ""),
            matched_urls=list(payload.get("matched_urls") or []),
            external_url=payload.get("external_url"),
            external_final_url=payload.get("external_final_url"),
            external_title=payload.get("external_title"),
            external_description=payload.get("external_description"),
            public_metrics=dict(payload.get("public_metrics") or {}),
            raw_source=payload.get("raw_source", "x_recent_search"),
            collected_at=payload.get("collected_at"),
        )

