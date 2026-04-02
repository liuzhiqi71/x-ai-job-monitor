from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from typing import Dict, Iterable, List

from .models import JobLead

HIRING_TERMS = (
    "招聘",
    "招人",
    "岗位",
    "内推",
    "社招",
    "诚聘",
    "hc",
    "jd",
    "投递",
    "简历",
    "求职",
    "岗位招聘中",
    "远程工作",
)

AI_ROLE_TERMS = (
    "ai",
    "人工智能",
    "大模型",
    "llm",
    "机器学习",
    "算法",
    "算法工程师",
    "ai工程师",
    "人工智能工程师",
    "机器学习工程师",
    "大模型工程师",
    "nlp",
    "aigc",
    "多模态",
    "机器人",
    "具身智能",
    "人形机器人",
    "机器人工程师",
    "机器人算法工程师",
    "机器人数据采集",
    "机器人运营",
    "机器人会话逻辑",
    "机器人运维",
    "slam",
    "运动控制",
    "控制工程师",
    "机械臂",
    "感知算法",
    "ros",
)

ROLE_SIGNAL_TERMS = (
    "工程师",
    "实习生",
    "研究员",
    "科学家",
    "产品经理",
    "开发",
    "specialist",
    "运营",
    "运维",
    "数据采集",
    "会话逻辑",
    "岗位招聘中",
    "岗位详情",
    "职位",
    "远程工作",
)

NOISE_TERMS = (
    "论文",
    "science 今天发论文",
    "新闻",
    "前总统",
    "提醒",
    "偏见",
    "webinar",
    "交流群",
    "程序自动统计",
    "不可作为任何投资参考",
    "市值",
    "预测市场",
    "推文预测",
    "gmgn",
    "币价",
    "代币",
    "天气预测",
    "课程",
    "训练营",
    "资源分享",
    "0基础可学",
    "入门到大师",
    "本周热读",
    "热读",
    "裁员",
    "华尔街日报",
    "wsj",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_urls(tweet: Dict[str, object]) -> List[str]:
    entities = tweet.get("entities") or {}
    urls = entities.get("urls") or []
    ordered = OrderedDict()
    for item in urls:
        url = item.get("unwound_url") or item.get("expanded_url") or item.get("url")
        if url:
            ordered[url] = None
    return list(ordered.keys())


def normalize_search_pages(
    pages: Iterable[Dict[str, object]],
    query_name: str,
    collected_at: str | None = None,
) -> List[JobLead]:
    collected_at = collected_at or _now_iso()
    users: Dict[str, Dict[str, object]] = {}
    rows: List[Dict[str, object]] = []

    for payload in pages:
        includes = payload.get("includes") or {}
        for user in includes.get("users") or []:
            users[str(user.get("id"))] = user
        rows.extend(payload.get("data") or [])

    leads: List[JobLead] = []
    for tweet in rows:
        author = users.get(str(tweet.get("author_id")), {})
        author_username = author.get("username", "")
        matched_urls = _extract_urls(tweet)
        tweet_id = str(tweet.get("id"))
        if author_username:
            tweet_url = f"https://x.com/{author_username}/status/{tweet_id}"
        else:
            tweet_url = f"https://x.com/i/web/status/{tweet_id}"

        leads.append(
            JobLead(
                tweet_id=tweet_id,
                tweet_url=tweet_url,
                author_username=author_username,
                author_name=author.get("name", ""),
                created_at=tweet.get("created_at", ""),
                lang=tweet.get("lang"),
                text=(tweet.get("text") or "").strip(),
                query_name=query_name,
                matched_urls=matched_urls,
                external_url=matched_urls[0] if matched_urls else None,
                public_metrics=dict(tweet.get("public_metrics") or {}),
                collected_at=collected_at,
            )
        )
    return leads


def dedupe_leads(leads: Iterable[JobLead]) -> List[JobLead]:
    by_id: Dict[str, JobLead] = {}
    for lead in leads:
        if lead.tweet_id not in by_id:
            by_id[lead.tweet_id] = lead
    return list(by_id.values())


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    low = (text or "").lower()
    return any(term.lower() in low for term in terms)


def filter_query_leads(leads: Iterable[JobLead]) -> List[JobLead]:
    filtered: List[JobLead] = []
    for lead in leads:
        if lead.query_name != "chinese-ai-hiring":
            filtered.append(lead)
            continue

        body = " ".join(
            part
            for part in [lead.text, lead.external_url or "", " ".join(lead.matched_urls)]
            if part
        )

        if not _contains_any(body, HIRING_TERMS):
            continue
        if not _contains_any(body, AI_ROLE_TERMS):
            continue
        if not _contains_any(body, ROLE_SIGNAL_TERMS):
            continue
        if _contains_any(body, NOISE_TERMS):
            continue

        filtered.append(lead)

    return filtered
