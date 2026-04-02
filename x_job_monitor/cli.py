from __future__ import annotations

import argparse
import os
from typing import Dict

from .client import XRecentSearchClient
from .config import load_config
from .logging_utils import get_logger
from .metadata import ExternalMetadata, fetch_external_metadata
from .normalize import dedupe_leads, filter_query_leads, normalize_search_pages
from .query import fetch_query_pages
from .render import append_raw_jsonl, read_jsonl, write_latest_csv, write_markdown
from .state import StateStore


def _enrich_metadata(leads, timeout_seconds: int, user_agent: str) -> None:
    cache: Dict[str, ExternalMetadata] = {}
    for lead in leads:
        if not lead.external_url:
            continue
        if lead.external_url not in cache:
            cache[lead.external_url] = fetch_external_metadata(
                url=lead.external_url,
                timeout_seconds=timeout_seconds,
                user_agent=user_agent,
            )
        metadata = cache[lead.external_url]
        lead.external_final_url = metadata.final_url
        lead.external_title = metadata.title
        lead.external_description = metadata.description


def run_monitor(config_path: str) -> int:
    logger = get_logger(__name__)
    token = os.getenv("X_BEARER_TOKEN")
    if not token:
        logger.error("Missing required environment variable: X_BEARER_TOKEN")
        return 2

    config = load_config(config_path)
    state = StateStore(config.state.path)
    all_new_leads = []

    with XRecentSearchClient(
        bearer_token=token,
        base_url=config.app.base_url,
        timeout_seconds=config.app.request_timeout_seconds,
        connect_timeout_seconds=config.app.connect_timeout_seconds,
        user_agent=config.app.user_agent,
    ) as client:
        for query_config in config.queries:
            result = fetch_query_pages(
                client=client,
                query_name=query_config.name,
                query=query_config.query,
                since_id=state.get_since_id(query_config.name),
                max_pages=config.app.max_pages_per_query,
                max_results=config.app.max_results_per_query,
            )
            leads = normalize_search_pages(result.pages, query_name=query_config.name)
            all_new_leads.extend(leads)
            state.set_since_id(query_config.name, result.newest_id)
            logger.info("Fetched %d leads for query=%s", len(leads), query_config.name)

    fetched_count = len(all_new_leads)
    all_new_leads = dedupe_leads(all_new_leads)
    deduped_count = len(all_new_leads)
    all_new_leads = filter_query_leads(all_new_leads)
    logger.info(
        "Lead filtering fetched=%d deduped=%d kept=%d",
        fetched_count,
        deduped_count,
        len(all_new_leads),
    )
    if config.app.fetch_external_metadata:
        _enrich_metadata(
            all_new_leads,
            timeout_seconds=config.app.external_metadata_timeout_seconds,
            user_agent=config.app.user_agent,
        )

    appended = append_raw_jsonl(config.output.raw_jsonl_path, all_new_leads)
    all_leads = read_jsonl(config.output.raw_jsonl_path)
    write_latest_csv(config.output.csv_path, all_leads)
    write_markdown(config.output.markdown_path, all_leads)
    state.save()

    logger.info(
        "Monitor run complete appended=%d total=%d",
        appended,
        len(all_leads),
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Monitor AI hiring posts on X.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the monitor once.")
    run_parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return run_monitor(args.config)
    parser.print_help()
    return 1
