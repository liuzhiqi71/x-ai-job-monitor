from x_job_monitor.state import StateStore


def test_state_store_round_trip(tmp_path):
    path = tmp_path / "state" / "state.json"
    store = StateStore(str(path))
    assert store.get_since_id("chinese-ai-hiring") is None
    store.set_since_id("chinese-ai-hiring", "123")
    store.save()

    reloaded = StateStore(str(path))
    assert reloaded.get_since_id("chinese-ai-hiring") == "123"
