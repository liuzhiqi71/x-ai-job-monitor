from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

from .models import JobLead

CSV_COLUMNS = [
    "tweet_id",
    "tweet_url",
    "author_username",
    "author_name",
    "created_at",
    "lang",
    "text",
    "query_name",
    "matched_urls",
    "external_url",
    "external_final_url",
    "external_title",
    "external_description",
    "public_metrics",
    "raw_source",
    "collected_at",
]


def _sort_leads(leads: Iterable[JobLead]) -> List[JobLead]:
    return sorted(
        leads,
        key=lambda item: (item.created_at or "", item.tweet_id),
        reverse=True,
    )


def read_jsonl(path: str) -> List[JobLead]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    items: List[JobLead] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            items.append(JobLead.from_dict(json.loads(line)))
    return items


def append_raw_jsonl(path: str, new_leads: Iterable[JobLead]) -> int:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    existing_ids = {lead.tweet_id for lead in read_jsonl(path)}
    appended = 0
    with file_path.open("a", encoding="utf-8") as handle:
        for lead in new_leads:
            if lead.tweet_id in existing_ids:
                continue
            handle.write(json.dumps(lead.to_dict(), ensure_ascii=False) + "\n")
            existing_ids.add(lead.tweet_id)
            appended += 1
    return appended


def write_latest_csv(path: str, leads: Iterable[JobLead]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for lead in _sort_leads(leads):
            row = lead.to_dict()
            row["matched_urls"] = json.dumps(lead.matched_urls, ensure_ascii=False)
            row["public_metrics"] = json.dumps(lead.public_metrics, ensure_ascii=False)
            writer.writerow(row)


def write_markdown(path: str, leads: Iterable[JobLead]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    items = _sort_leads(leads)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Latest AI Job Leads From X",
        "",
        f"*Generated at: {generated_at}*",
        "",
        f"*Total leads: {len(items)}*",
        "",
    ]

    if not items:
        lines.append("No leads collected yet.")
    else:
        for lead in items:
            lines.extend(
                [
                    f"## {lead.author_name or lead.author_username or 'Unknown author'}",
                    "",
                    f"- Query: `{lead.query_name}`",
                    f"- Posted at: `{lead.created_at or 'unknown'}`",
                    f"- Tweet: [{lead.tweet_id}]({lead.tweet_url})",
                    f"- External URL: {lead.external_final_url or lead.external_url or 'N/A'}",
                    f"- External title: {lead.external_title or 'N/A'}",
                    f"- Text: {lead.text}",
                    "",
                ]
            )

    file_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

