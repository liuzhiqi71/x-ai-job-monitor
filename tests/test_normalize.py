import json
from pathlib import Path

from x_job_monitor.models import JobLead
from x_job_monitor.normalize import dedupe_leads, filter_query_leads, normalize_search_pages


def test_normalize_search_pages_maps_author_and_url():
    fixture_path = Path(__file__).parent / "fixtures" / "search_recent_response.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    leads = normalize_search_pages([payload], query_name="english-ai-jobs", collected_at="2026-04-02T00:00:00Z")
    assert len(leads) == 1
    lead = leads[0]
    assert lead.author_username == "hiringteam"
    assert lead.tweet_url.endswith("/status/1900000000000000001")
    assert lead.external_url == "https://jobs.example.com/open-role"
    assert lead.collected_at == "2026-04-02T00:00:00Z"


def test_dedupe_leads_keeps_first_tweet_id():
    fixture_path = Path(__file__).parent / "fixtures" / "search_recent_response.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    leads = normalize_search_pages([payload], query_name="english-ai-jobs")
    duplicated = dedupe_leads(leads + leads)
    assert len(duplicated) == 1


def test_filter_query_leads_keeps_job_post_and_drops_noise():
    job_post = JobLead(
        tweet_id="1",
        tweet_url="https://x.com/a/status/1",
        author_username="jobposter",
        author_name="Job Poster",
        created_at="2026-04-02T00:00:00Z",
        lang="zh",
        text="AI工程师招聘中，欢迎投递简历，岗位详情见链接",
        query_name="chinese-ai-hiring",
        matched_urls=["https://jobs.example.com/1"],
        external_url="https://jobs.example.com/1",
    )
    noise_post = JobLead(
        tweet_id="2",
        tweet_url="https://x.com/b/status/2",
        author_username="noise",
        author_name="Noise",
        created_at="2026-04-02T00:00:00Z",
        lang="zh",
        text="Science 今天发论文：你的 AI 在拍马屁。",
        query_name="chinese-ai-hiring",
        matched_urls=["https://science.example.com/paper"],
        external_url="https://science.example.com/paper",
    )
    kept = filter_query_leads([job_post, noise_post])
    assert [item.tweet_id for item in kept] == ["1"]


def test_filter_query_leads_drops_course_and_news_posts():
    course_post = JobLead(
        tweet_id="3",
        tweet_url="https://x.com/c/status/3",
        author_username="course",
        author_name="Course",
        created_at="2026-04-02T00:00:00Z",
        lang="zh",
        text="人人都可以学的AI自动化招聘课，0基础可学，人工智能自动招聘解放HR",
        query_name="chinese-ai-hiring",
        matched_urls=["https://example.com/course"],
        external_url="https://example.com/course",
    )
    news_post = JobLead(
        tweet_id="4",
        tweet_url="https://x.com/d/status/4",
        author_username="news",
        author_name="News",
        created_at="2026-04-02T00:00:00Z",
        lang="zh",
        text="本周热读 企业将裁员归因于人工智能已成为一种风潮。",
        query_name="chinese-ai-hiring",
        matched_urls=["https://example.com/news"],
        external_url="https://example.com/news",
    )
    kept = filter_query_leads([course_post, news_post])
    assert kept == []


def test_filter_query_leads_keeps_robotics_hiring_post():
    robotics_post = JobLead(
        tweet_id="5",
        tweet_url="https://x.com/e/status/5",
        author_username="robotics",
        author_name="Robotics",
        created_at="2026-04-02T00:00:00Z",
        lang="zh",
        text="具身智能公司招聘机器人工程师和SLAM工程师，欢迎投递简历",
        query_name="chinese-ai-hiring",
        matched_urls=["https://robot.example.com/jobs"],
        external_url="https://robot.example.com/jobs",
    )
    kept = filter_query_leads([robotics_post])
    assert [item.tweet_id for item in kept] == ["5"]


def test_filter_query_leads_keeps_robotics_operations_post():
    operations_post = JobLead(
        tweet_id="6",
        tweet_url="https://x.com/f/status/6",
        author_username="robotops",
        author_name="Robot Ops",
        created_at="2026-04-02T00:00:00Z",
        lang="zh",
        text="机器人公司招聘机器人运营和机器人运维，欢迎投递简历",
        query_name="chinese-ai-hiring",
        matched_urls=["https://robot.example.com/ops"],
        external_url="https://robot.example.com/ops",
    )
    kept = filter_query_leads([operations_post])
    assert [item.tweet_id for item in kept] == ["6"]
