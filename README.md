# HackSonTest

这个仓库演示了如何：

- 创建一个可以被外部调用的 GitHub Action（通过 `repository_dispatch` 事件）
- 使用本地 HTTP server 暴露一个简单 API，由外部 shell 脚本调用，再由 server 去触发 GitHub Action

## 目录结构

- `.github/workflows/external-trigger.yml`：可被外部触发的 GitHub Action 工作流
- `server/server.py`：本地 HTTP server，通过 GitHub REST API 触发 `repository_dispatch`
- `requirements.txt`：Python 依赖（Flask + requests）
- `trigger_via_local.sh`：示例 shell 脚本，调用本地 server 暴露的 API

## 1. 准备 GitHub Access Token

1. 在 GitHub 上创建一个 Personal Access Token：
	- 建议使用 Fine-grained PAT，至少勾选当前仓库的 `Actions`/`Contents` 权限（或 Classic PAT 勾选 `repo` 权限）
2. 在本机设置环境变量（把占位符替换成你的实际信息）：

```bash
export GITHUB_TOKEN="<your_pat_here>"
export GITHUB_OWNER="rock-57blocks"     # 仓库 Owner
export GITHUB_REPO="HackSonTest"       # 仓库名
```

## 2. 安装并启动本地 server

在项目根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 启动本地 HTTP server（默认端口 8000）
python server/server.py
```

启动后，你可以用浏览器或 curl 测试健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## 3. 使用 shell 脚本调用暴露的 API

在另外一个终端（保持 server 进程不关）：

```bash
chmod +x trigger_via_local.sh
./trigger_via_local.sh "Hello from external shell"
```

这个脚本会：

1. 向本地 `http://127.0.0.1:8000/trigger` 发送一个 POST 请求（带上 message）
2. 本地 server 使用 GitHub API 调用 `repository_dispatch`：
	- `event_type`: `run-external-job`
	- `client_payload.message`: 你传入的 message
3. GitHub 端的 `external-trigger.yml` 工作流会被触发，你可以在 Actions 页面里看到这次运行

## 4. 工作流说明（`.github/workflows/external-trigger.yml`）

该工作流支持两种触发方式：

- `repository_dispatch`：由本地 server 或其它系统通过 GitHub REST API 触发
- `workflow_dispatch`：你也可以在 GitHub UI 手动触发，并传入一个 message 输入

工作流会打印：

- 触发事件名（`github.event_name`）
- 来自 `repository_dispatch` 的 `client_payload.message`
- 或来自 `workflow_dispatch` 的 `inputs.message`

这样你就拥有了：

- 一个可以通过外部系统（本地 server / 将来任何服务）调用的 GitHub Action
- 一个简单的 HTTP API + shell 脚本示例，用于演示整个调用链路

