# Privacy Policy

The Vidu S2 Dify plugin sends user-selected inputs to the regional Vidu API to create and inspect S2 Avatar and Editing real-time sessions.

## Data Processed

Depending on the Tool, the plugin may process and transmit:

- Avatar persona text, character image URI, display name, voice, call mode, and persona-enhancement selection.
- Editing reference image URI and editing type.
- Vidu live session identifiers and returned session metadata.
- Region selection and fixed Vidu endpoint metadata.
- Short-lived RTC application, channel, user, expiry, and `rtc.token` values returned by Vidu.
- Optional Editing `client_secret` and required `render_uid` returned by Vidu.
- Session status, timestamps, trace identifiers, billed seconds, and credit cost.

The reusable Vidu API key is stored through Dify's Provider credential mechanism. The plugin does not place the API key in Tool output or write it to plugin files.

## Third-Party Services

The plugin sends requests only to the selected fixed Vidu API host:

- China: `https://api.vidu.cn`
- Global: `https://api.vidu.com`

Vidu privacy information is available at https://www.vidu.cn/privacy-policy. Product and regional documentation is available through https://platform.vidu.cn/vidu-stream/doc and https://platform.vidu.com/vidu-stream/doc.

## Retention

The plugin does not intentionally persist user content. Dify Workflow execution history may retain structured inputs and outputs, including `rtc.token` and `client_secret`, according to workspace logging and retention settings. Vidu may retain API data according to its own policies. Workspace administrators should restrict access and choose an appropriate history retention period.

## Security Boundary

The plugin performs short-lived HTTP operations and does not maintain a Vidu control WebSocket or Aliyun RTC connection. A trusted application backend and RTC client must own those connections.

Do not send the reusable Vidu API key to a browser. Forward short-lived session credentials only to the client or backend serving that specific live session. The Tool implementations emit sensitive credentials only as structured variables and JSON, not as human-readable text or links.

## Contact

For privacy questions, open an issue at https://github.com/shengshu-ai/vidu-s-api/issues.
