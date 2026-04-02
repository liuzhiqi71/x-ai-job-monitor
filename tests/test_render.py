from x_job_monitor.models import JobLead
from x_job_monitor.render import append_raw_jsonl, read_jsonl, write_latest_csv, write_markdown


def _lead(tweet_id: str) -> JobLead:
    return JobLead(
        tweet_id=tweet_id,
        tweet_url=f"https://x.com/i/web/status/{tweet_id}",
        author_username="tester",
        author_name="Test User",
        created_at="2026-04-01T00:00:00Z",
        lang="en",
        text="Sample text",
        query_name="english-ai-jobs",
        matched_urls=["https://jobs.example.com/open-role"],
        external_url="https://jobs.example.com/open-role",
        external_final_url="https://jobs.example.com/open-role",
        external_title="Open Role",
        external_description="Join us",
        public_metrics={"like_count": 1},
        collected_at="2026-04-02T00:00:00Z",
    )


def test_render_outputs_files(tmp_path):
    raw_path = tmp_path / "data" / "raw_posts.jsonl"
    csv_path = tmp_path / "data" / "latest_jobs.csv"
    markdown_path = tmp_path / "reports" / "latest_jobs.md"

    appended = append_raw_jsonl(str(raw_path), [_lead("1"), _lead("1"), _lead("2")])
    assert appended == 2

    all_leads = read_jsonl(str(raw_path))
    write_latest_csv(str(csv_path), all_leads)
    write_markdown(str(markdown_path), all_leads)

    assert csv_path.exists()
    assert markdown_path.exists()
    assert len(all_leads) == 2
    assert "Open Role" in markdown_path.read_text(encoding="utf-8")

