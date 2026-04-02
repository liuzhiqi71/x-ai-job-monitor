from pathlib import Path

from scripts.check_secrets import scan_repo


def test_config_example_contains_no_real_secret():
    text = Path("config.example.yaml").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "aaaaaaaa" not in lowered
    assert "access token secret" not in lowered
    assert "password:" not in lowered


def test_gitignore_covers_local_secret_files():
    text = Path(".gitignore").read_text(encoding="utf-8")
    assert ".env" in text
    assert "config.local.yaml" in text
    assert "*.save" in text
    assert "data/state/" in text


def test_secret_scanner_detects_simulated_secret(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    marker = "pass" + "word"
    (repo / "bad.txt").write_text(f'{marker} = "supersecret123!"\n', encoding="utf-8")
    findings = scan_repo(repo)
    assert findings


def test_secret_scanner_does_not_skip_real_secret_in_example_text(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    marker = "pass" + "word"
    (repo / "bad.txt").write_text(
        f'link = "https://example.com"\n{marker} = "supersecret123!"\n',
        encoding="utf-8",
    )
    findings = scan_repo(repo)
    assert findings
