# X AI Job Monitor

一个面向公开仓库的 X 招聘监控工具。它使用 X API v2 Recent Search 抓取中文 AI 与机器人公司招聘帖子，并生成可提交回仓库的 `JSONL`、`CSV` 和 `Markdown` 报告。

## Features

- 使用 `X_BEARER_TOKEN` 访问 X API，不在仓库内保存任何真实凭据
- 默认使用“中文 AI 与机器人招聘”紧查询，优先抓带链接的中文招聘帖
- 使用每个查询独立的 `since_id` 做增量抓取
- 外链网页抓取默认关闭，降低单次运行成本；需要时可在本地配置里打开
- 输出：
  - `data/raw_posts.jsonl`
  - `data/latest_jobs.csv`
  - `reports/latest_jobs.md`
- 本地 secret scan 命令：`make check-secrets`
- GitHub Actions:
  - `ci.yml` 在 `push` 和 `pull_request` 上跑测试与 secret scan
  - `monitor.yml` 每周一 UTC 00:00 运行，对应北京时间每周一 08:00

## Security

- 当前对话里暴露过的 X 凭据必须先轮换，再使用新 Bearer Token。
- 只把新的 `X_BEARER_TOKEN` 放进本地环境变量和 GitHub repository secrets。
- 不要把 `.env`、`config.local.yaml`、`*.save`、cookies、登录态文件放进仓库。

## Local Setup

```bash
cd /Users/weiliu/Code/x-ai-job-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp config.example.yaml config.local.yaml
export X_BEARER_TOKEN='your-rotated-token'
python -m x_job_monitor run --config config.example.yaml
```

如果你希望覆盖模板里的查询或输出路径，复制 `config.example.yaml` 到 `config.local.yaml` 并修改，再在命令里传这个本地文件。

## Make Targets

```bash
make test
make check-secrets
make run
```

`make run` 默认读取 `config.example.yaml`。真正的私有配置请使用你本地未提交的 `config.local.yaml`。

## Cost Control Defaults

默认配置已经收紧到低成本模式：

- 单次只跑 1 个中文招聘查询
- 每次最多抓 10 条
- 每个查询只抓 1 页
- 默认不抓外链页面元数据
- 本地会过滤明显不是招聘的噪音帖，例如论文讨论、新闻评论、币圈广告和工具宣传

如果只是验证 token 和查询效果，先保持这个默认值，不要扩大抓取范围。

## GitHub Actions Setup

1. 创建公开仓库并推送本目录。
2. 在 GitHub 仓库里新增 secret：`X_BEARER_TOKEN`
3. 手动运行一次 `monitor.yml`
4. 确认它能：
   - 通过测试
   - 通过 Gitleaks
   - 生成 `data/` 和 `reports/` 输出
   - 有变化时自动提交
