from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class DefaultQuery:
    name: str
    query: str


@dataclass
class QueryFetchResult:
    pages: List[Dict[str, object]]
    newest_id: Optional[str]


DEFAULT_QUERIES = [
    DefaultQuery(
        name="chinese-ai-hiring",
        query='("AI工程师" OR "人工智能工程师" OR "大模型工程师" OR '
        '"机器学习工程师" OR "算法工程师" OR "NLP工程师" OR "机器人工程师" OR '
        '"机器人算法工程师" OR "SLAM工程师" OR "运动控制工程师" OR "机器人数据采集" OR '
        '"机器人运营" OR "机器人会话逻辑" OR "机器人运维" OR "具身智能" OR '
        '"人形机器人" OR "机械臂" OR "AIGC" OR "大模型" OR "人工智能" OR "机器人") '
        '(招聘 OR 招人 OR 岗位 OR 内推 OR 社招 OR 诚聘 OR HC OR JD OR 投递) '
        "lang:zh has:links -is:retweet -is:reply",
    ),
]


def _max_snowflake(left: Optional[str], right: Optional[str]) -> Optional[str]:
    if not left:
        return right
    if not right:
        return left
    return left if int(left) >= int(right) else right


def fetch_query_pages(
    client,
    query_name: str,
    query: str,
    since_id: Optional[str],
    max_pages: int,
    max_results: int,
) -> QueryFetchResult:
    pages: List[Dict[str, object]] = []
    newest_id = since_id
    next_token: Optional[str] = None

    for _ in range(max(1, max_pages)):
        payload = client.search_recent(
            query=query,
            query_name=query_name,
            max_results=max_results,
            since_id=since_id,
            next_token=next_token,
        )
        pages.append(payload)
        meta = payload.get("meta") or {}
        newest_id = _max_snowflake(newest_id, meta.get("newest_id"))
        next_token = meta.get("next_token")
        if not next_token:
            break

    return QueryFetchResult(pages=pages, newest_id=newest_id)
