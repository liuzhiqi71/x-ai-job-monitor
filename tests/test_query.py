from x_job_monitor.query import fetch_query_pages


class StubClient:
    def __init__(self) -> None:
        self.calls = []

    def search_recent(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "data": [],
            "meta": {
                "newest_id": "20",
                "next_token": None,
            },
        }


def test_fetch_query_pages_uses_since_id_and_stops_without_next_token():
    client = StubClient()
    result = fetch_query_pages(
        client=client,
        query_name="english-ai-jobs",
        query="test query",
        since_id="10",
        max_pages=3,
        max_results=50,
    )
    assert result.newest_id == "20"
    assert len(result.pages) == 1
    assert client.calls[0]["since_id"] == "10"
    assert client.calls[0]["query_name"] == "english-ai-jobs"

