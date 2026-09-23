# Vidu S2 Dify Plugin

This independent Dify Tool Plugin creates and inspects Vidu S2 Avatar and Editing real-time sessions. It is distributed as `shengshu-ai/vidu_s2` and coexists with the separate Vidu S1 plugin in the same source repository.

## Tools

| Tool | Purpose |
| --- | --- |
| `create_avatar_session` | Create an S2 Avatar real-time session from a persona and character image. |
| `create_editing_session` | Create an S2 Editing session for style transfer, virtual try-on, subject replacement, or background replacement. |
| `get_live_session` | Query status, timing, trace, and billing fields for either session type. |
| `list_voices` | List custom cloned voices available to the Vidu account. |

## Product Boundary

The plugin performs short-lived HTTPS calls inside Dify Workflow or Agent runs. It returns session metadata and the structured RTC values required by a trusted application.

It does not host a real-time call or maintain the Vidu control WebSocket. A complete integration also requires:

- A trusted backend that opens the authenticated Vidu control WebSocket, completes `conn_init`, maintains heartbeats, sends runtime controls, and terminates the session.
- An Aliyun RTC client that joins with the returned credentials, publishes microphone or camera media, and renders the generated remote stream.
- Editing clients must render the camera stream published by the returned `render_uid`.

Runtime Avatar text, reference-image operations, Editing prompt switches, interruption, and hangup remain stateful backend responsibilities rather than stateless Dify Tools.

## Provider Configuration

| Field | Required | Notes |
| --- | --- | --- |
| `vidu_api_key` | Yes | Accepts `vda_xxx` or `Token vda_xxx`. |
| `region` | Yes | `cn` uses `https://api.vidu.cn`; `global` uses `https://api.vidu.com`. |

Credential validation makes a read-only `GET /live/v1/voices` request. It does not create a live session.

## Sensitive Workflow Output

Creation tools return `rtc.token`, other RTC identities, and—when supplied by Editing—`client_secret`. These are short-lived session credentials. They are returned only as structured variables and JSON, never as human-readable Tool text or links.

Dify Workflow history may retain structured output. Restrict history access and retention, and forward credentials only to the trusted backend or RTC client that owns that session. The reusable Vidu API key remains in Dify Provider credentials and is never returned by a Tool.

## Data Flow

```text
Dify Workflow
  -> create_avatar_session or create_editing_session
  -> pass live_id and structured session credentials to a trusted backend
  -> backend owns the Vidu control WebSocket
  -> browser/mobile client owns Aliyun RTC media
  -> get_live_session reads status and billing data
```

## Local Development

Use Python 3.12:

```bash
python -m venv plugins/dify-s2/.venv
plugins/dify-s2/.venv/Scripts/python -m pip install -r plugins/dify-s2/requirements.txt pytest pyyaml
PYTHONPATH=plugins/dify-s2 plugins/dify-s2/.venv/Scripts/python -m pytest plugins/dify-s2/tests
```

Package from the repository root:

```bash
dify plugin package ./plugins/dify-s2 -o vidu_s2-0.0.2.difypkg
```

## Source and Support

- Source: https://github.com/shengshu-ai/vidu-s-api
- Issues: https://github.com/shengshu-ai/vidu-s-api/issues
- Product documentation: https://platform.vidu.com/vidu-stream/doc and https://platform.vidu.cn/vidu-stream/doc

Release details are documented in `PUBLISHING.md`. The first S2 release uses Git tag `v0.0.2` because this shared repository already uses `v0.0.1` for the independent S1 plugin.
