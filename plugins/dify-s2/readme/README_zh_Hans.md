# Vidu S2 Dify 插件

这是一个独立的 Dify Tool Plugin，用于创建和查询 Vidu S2 Avatar 与 Editing 实时会话。插件身份为 `shengshu-ai/vidu_s2`，与同一源码仓库中的 Vidu S1 插件并行存在、互不覆盖。

## 工具

| 工具 | 用途 |
| --- | --- |
| `create_avatar_session` | 根据人设和角色图片创建 S2 Avatar 实时会话。 |
| `create_editing_session` | 创建风格迁移、虚拟试穿、主体替换或背景替换的 S2 Editing 会话。 |
| `get_live_session` | 查询两类会话的状态、时间、追踪与计费字段。 |
| `list_voices` | 查询当前 Vidu 账号可用的自定义克隆音色。 |

## 产品边界

插件在 Dify Workflow 或 Agent 中执行短时 HTTPS 请求，返回会话元数据以及可信应用所需的结构化 RTC 数据。

插件不会在 Dify 内承载实时通话，也不会长期维护 Vidu 控制 WebSocket。完整接入还需要：

- 可信后端负责建立带鉴权的 Vidu 控制 WebSocket、完成 `conn_init`、维持心跳、发送运行中控制并结束会话。
- 阿里云 RTC 客户端使用返回的凭证加入频道、发布麦克风或摄像头媒体并渲染生成结果。
- Editing 客户端只渲染返回的 `render_uid` 对应的 camera stream。

Avatar 文本、参考图操作、Editing prompt 切换、中断与挂断均依赖持续连接状态，因此不作为普通 Dify Tool 暴露。

## Provider 配置

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `vidu_api_key` | 是 | 支持 `vda_xxx` 或 `Token vda_xxx`。 |
| `region` | 是 | `cn` 使用 `https://api.vidu.cn`；`global` 使用 `https://api.vidu.com`。 |

保存凭证时调用只读的 `GET /live/v1/voices`，不会创建实时会话。

## 敏感 Workflow 输出

创建工具会返回 `rtc.token`、其他 RTC 身份信息，以及 Editing 可能返回的 `client_secret`。它们都是短期会话凭证，只作为结构化变量与 JSON 返回，不会写入面向用户的 Tool 文本或链接。

Dify Workflow 历史可能保留结构化输出。请限制历史记录的访问权限和保留时间，并仅将凭证交给当前会话使用的可信后端或 RTC 客户端。可重复使用的 Vidu API Key 始终保存在 Dify Provider 凭证中，不会作为 Tool 输出返回。

## 集成链路

```text
Dify Workflow
  -> create_avatar_session 或 create_editing_session
  -> 将 live_id 与结构化会话凭证交给可信后端
  -> 后端维护 Vidu 控制 WebSocket
  -> 浏览器或移动端维护阿里云 RTC 媒体
  -> get_live_session 查询状态和计费
```

## 源码与支持

- 源码：https://github.com/shengshu-ai/vidu-s-api
- 问题反馈：https://github.com/shengshu-ai/vidu-s-api/issues
- 产品文档：https://platform.vidu.cn/vidu-stream/doc 和 https://platform.vidu.com/vidu-stream/doc

S2 首个包名为 `vidu_s2-0.0.2.difypkg`，Git tag 为 `v0.0.2`。这是因为同一仓库的 `v0.0.1` 已用于独立的 S1 插件。
