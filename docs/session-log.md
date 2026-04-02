## 2026-04-02 12:22
- Did: Initialized the public-safe X AI job monitor repository, implemented the X recent search client, normalization, metadata fetch, state store, renderers, tests, Make targets, and GitHub Actions for CI plus daily execution.
- Commands: `mkdir -p /Users/weiliu/Code/x-ai-job-monitor/{x_job_monitor,tests,tests/fixtures,.github/workflows,docs,data,reports,scripts}`, `git init /Users/weiliu/Code/x-ai-job-monitor`
- Result: Repository scaffold created and ready for dependency install, local test execution, and secret-scan verification.
- Next: Install dependencies, run pytest and local secret scan, then review the resulting diff and any environment-specific gaps.

## 2026-04-02 12:29
- Did: Verified the repository with a Python 3.13 virtualenv, ran the test suite, ran the local secret scanner, and checked the CLI failure path for a missing `X_BEARER_TOKEN`.
- Commands: `/opt/homebrew/bin/python3.13 -m venv .venv`, `.venv/bin/python -m pip install -e '.[dev]'`, `.venv/bin/python -m pytest`, `.venv/bin/python scripts/check_secrets.py .`, `X_BEARER_TOKEN='' .venv/bin/python -m x_job_monitor run --config config.example.yaml`
- Result: `9 passed`; local secret scan reported no findings; missing-token path exits cleanly without exposing headers or token values.
- Next: Remove local build artifacts from status, review the diff, and push this new repository to GitHub after adding a rotated `X_BEARER_TOKEN` secret.

## 2026-04-02 12:30
- Did: Tightened the local secret scanner to avoid false negatives from placeholder text and updated the security tests so simulated leaks are generated at runtime instead of being stored in the repo.
- Commands: `.venv/bin/python -m pytest`, `.venv/bin/python scripts/check_secrets.py .`
- Result: `10 passed`; local secret scan reported no findings after the scanner fix and test cleanup.
- Next: Add the rotated `X_BEARER_TOKEN` secret in GitHub, push the repo, and run `monitor.yml` once with `workflow_dispatch`.

## 2026-04-02 12:38
- Did: Read the local X credential file, attempted one real monitor run with the extracted Bearer Token, then installed `gitleaks` locally and ran a repository scan.
- Commands: `X_BEARER_TOKEN=<from /Users/weiliu/x-api.txt> .venv/bin/python -m x_job_monitor run --config config.example.yaml`, `/opt/homebrew/bin/brew install gitleaks`, `/opt/homebrew/bin/gitleaks detect --source . --no-git --redact`
- Result: Real X API run reached `GET /2/tweets/search/recent` but failed with `401 Unauthorized`, so no data files were generated; local `gitleaks` 8.30.1 scan passed with `no leaks found`.
- Next: Replace the local Bearer Token with a valid rotated token or confirm the app has Recent Search access, then rerun the monitor and inspect generated outputs.

## 2026-04-02 12:45
- Did: Retested the real X API run with the updated local Bearer Token from `/Users/weiliu/x-api.txt` and inspected the direct API response body for billing status.
- Commands: `X_BEARER_TOKEN=<from /Users/weiliu/x-api.txt> .venv/bin/python -m x_job_monitor run --config config.example.yaml`, `curl -H "Authorization: Bearer <token>" 'https://api.x.com/2/tweets/search/recent?query=AI&max_results=10'`
- Result: Authentication succeeded far enough to return `402 Payment Required` with `CreditsDepleted`; response detail said the enrolled account had no credits, and no output files were generated.
- Next: Add credits to the enrolled X API account, then rerun the monitor to confirm data collection and report generation.

## 2026-04-02 13:05
- Did: Tightened the default monitor configuration to reduce spend by narrowing the search scope to Chinese AI hiring posts, limiting each run to one page of ten results, and disabling external metadata fetch by default.
- Commands: `apply_patch` to update `config.example.yaml`, `x_job_monitor/query.py`, `README.md`, and tests
- Result: The repository defaults now favor low-cost validation instead of wide discovery; the next real API run should issue materially fewer requests and avoid slow per-link fetches.
- Next: Run the test suite locally to confirm the narrower defaults did not break behavior, then only rerun X API after you explicitly approve another paid test.

## 2026-04-02 13:08
- Did: Ran one real X API request using the narrowed Chinese AI hiring query and wrote the resulting outputs to JSONL, CSV, Markdown, and state files.
- Commands: `X_BEARER_TOKEN=<from /Users/weiliu/x-api.txt> .venv/bin/python -m x_job_monitor run --config config.example.yaml`
- Result: The run completed successfully with `Fetched 10 leads for query=chinese-ai-hiring`; output files were created under `data/` and `reports/`; the saved `since_id` is `2039559209021563116`.
- Next: Review the ten captured posts, tighten the query further to reduce remaining non-job noise, and only rerun when the narrower query is ready.

## 2026-04-02 13:18
- Did: Narrowed the Chinese hiring query again and added a local hiring-intent filter so obvious noise posts are dropped before writing output.
- Commands: `apply_patch` to update `config.example.yaml`, `x_job_monitor/normalize.py`, `x_job_monitor/cli.py`, `README.md`, and normalization tests
- Result: Default matching is now stricter on both the remote query and local filtering path; local verification passed with `11 passed`, and the local secret scan still reported no findings.
- Next: Only make another paid API request if you explicitly want to validate the narrower matching against live X data.

## 2026-04-02 13:20
- Did: Cleared the previous generated outputs and state, then ran one real X API request with the narrower Chinese hiring query and reviewed the resulting CSV and Markdown outputs.
- Commands: `rm -f data/raw_posts.jsonl data/latest_jobs.csv reports/latest_jobs.md data/state/state.json`, `X_BEARER_TOKEN=<from /Users/weiliu/x-api.txt> .venv/bin/python -m x_job_monitor run --config config.example.yaml`
- Result: The live run fetched 6 posts, kept 5 after local filtering, and wrote fresh output files under `data/` and `reports/`; remaining noise still includes a training/course post and a news article.
- Next: Tighten local filtering again to drop course/training/news content before the next paid request.

## 2026-04-02 13:33
- Did: Strengthened local hiring filters by requiring role-like job signals and expanding the noise list to drop course, training, resource-share, and news-style posts.
- Commands: `apply_patch` to update `x_job_monitor/normalize.py`, normalization tests, and the session log
- Result: The filter now requires both AI hiring intent and role signals such as `工程师` or `实习生`, making false positives materially less likely.
- Next: Rebuild the current local outputs from the already-fetched JSONL file so the visible reports reflect the stricter filtering without another paid API call.

## 2026-04-02 13:34
- Did: Expanded the default hiring scope to include Chinese robotics-company hiring terms while keeping the local filter strict on recruitment intent and role signals.
- Commands: `apply_patch` to update `config.example.yaml`, `README.md`, `x_job_monitor/query.py`, `x_job_monitor/normalize.py`, and normalization tests
- Result: The monitor now targets both AI and robotics hiring posts such as `机器人工程师`, `SLAM工程师`, and `具身智能`, without reopening the broader generic AI-topic search.
- Next: Run the local test suite and secret scan, then decide whether to spend another paid request validating the expanded robotics scope on live X data.

## 2026-04-02 13:36
- Did: Expanded the robotics hiring scope further to include robot data collection, robot operations, robot dialogue logic, and robot operations/maintenance roles in both the query and local role filters.
- Commands: `apply_patch` to update `config.example.yaml`, `x_job_monitor/query.py`, `x_job_monitor/normalize.py`, normalization tests, and the session log
- Result: The matcher now covers non-engineering but still role-like robotics hiring posts such as `机器人运营`, `机器人数据采集`, `机器人会话逻辑`, and `机器人运维`.
- Next: Run the local test suite and secret scan, then decide whether to spend another paid request validating the expanded robotics scope on live X data.

## 2026-04-02 13:38
- Did: Cleared outputs and reran one live X API request with the expanded AI-plus-robotics hiring query, then reviewed the regenerated CSV and Markdown outputs.
- Commands: `rm -f data/raw_posts.jsonl data/latest_jobs.csv reports/latest_jobs.md data/state/state.json`, `X_BEARER_TOKEN=<from /Users/weiliu/x-api.txt> .venv/bin/python -m x_job_monitor run --config config.example.yaml`
- Result: The live run fetched 10 posts, kept 3 after filtering, and regenerated the outputs; this sample did not surface new robotics-specific hiring posts, but the output remained clean and low-noise.
- Next: Leave the broader AI+robotics query in place for future daily runs and only spend more live requests if you want a larger page size or more queries.

## 2026-04-02 13:39
- Did: Changed the automation cadence from daily to once per week on Monday while keeping the manual workflow trigger available.
- Commands: `apply_patch` to update `.github/workflows/monitor.yml`, `README.md`, and the session log
- Result: The scheduled workflow now uses `0 0 * * 1`, which runs at Monday 00:00 UTC and Monday 08:00 Beijing time; commit messages were updated to say `weekly`.
- Next: Run the local test suite and secret scan, then push the workflow change so GitHub picks up the new weekly schedule.

## 2026-04-02 13:46
- Did: Investigated the failed GitHub Actions runs, found the third-party Gitleaks wrapper was failing to parse its bundled config on GitHub-hosted runners, and switched both workflows to the official `gitleaks/gitleaks-action`.
- Commands: `gh run view 23885941411 --log -R liuzhiqi71/x-ai-job-monitor`, `gh run view 23885936388 --log -R liuzhiqi71/x-ai-job-monitor`, `apply_patch` to update `.github/workflows/ci.yml`, `.github/workflows/monitor.yml`, and the session log
- Result: The failure root cause is isolated to the GitHub-side Gitleaks action wrapper rather than any actual secret leak; local secret scans and local Gitleaks checks still pass cleanly.
- Next: Re-run local verification, push the workflow fix, and trigger the weekly monitor workflow again to confirm the public repo is green end to end.
