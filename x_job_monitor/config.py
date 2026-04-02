from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml

from .query import DEFAULT_QUERIES


@dataclass
class QueryConfig:
    name: str
    query: str


@dataclass
class OutputConfig:
    raw_jsonl_path: str
    csv_path: str
    markdown_path: str


@dataclass
class StateConfig:
    path: str


@dataclass
class AppConfig:
    base_url: str = "https://api.x.com/2"
    request_timeout_seconds: int = 20
    connect_timeout_seconds: int = 5
    external_metadata_timeout_seconds: int = 10
    max_results_per_query: int = 50
    max_pages_per_query: int = 2
    fetch_external_metadata: bool = True
    user_agent: str = "x-ai-job-monitor/0.1"


@dataclass
class MonitorConfig:
    app: AppConfig
    queries: List[QueryConfig]
    output: OutputConfig
    state: StateConfig


def load_config(path: str) -> MonitorConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    app_raw = raw.get("app") or {}
    output_raw = raw.get("output") or {}
    state_raw = raw.get("state") or {}
    queries_raw = raw.get("queries") or []

    queries = [
        QueryConfig(name=item["name"], query=item["query"])
        for item in queries_raw
        if item and item.get("name") and item.get("query")
    ]
    if not queries:
        queries = [QueryConfig(name=item.name, query=item.query) for item in DEFAULT_QUERIES]

    return MonitorConfig(
        app=AppConfig(
            base_url=app_raw.get("base_url", "https://api.x.com/2"),
            request_timeout_seconds=int(app_raw.get("request_timeout_seconds", 20)),
            connect_timeout_seconds=int(app_raw.get("connect_timeout_seconds", 5)),
            external_metadata_timeout_seconds=int(
                app_raw.get("external_metadata_timeout_seconds", 10)
            ),
            max_results_per_query=int(app_raw.get("max_results_per_query", 50)),
            max_pages_per_query=int(app_raw.get("max_pages_per_query", 2)),
            fetch_external_metadata=bool(app_raw.get("fetch_external_metadata", True)),
            user_agent=app_raw.get("user_agent", "x-ai-job-monitor/0.1"),
        ),
        queries=queries,
        output=OutputConfig(
            raw_jsonl_path=output_raw.get("raw_jsonl_path", "data/raw_posts.jsonl"),
            csv_path=output_raw.get("csv_path", "data/latest_jobs.csv"),
            markdown_path=output_raw.get("markdown_path", "reports/latest_jobs.md"),
        ),
        state=StateConfig(path=state_raw.get("path", "data/state/state.json")),
    )

