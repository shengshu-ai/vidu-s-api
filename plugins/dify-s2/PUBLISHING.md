# Publishing the Vidu S2 Dify Plugin

## Release Identity

- Author: `shengshu-ai`
- Plugin: `vidu_s2`
- Version: `0.0.2`
- Source directory: `plugins/dify-s2`
- Package: `vidu_s2-0.0.2.difypkg`
- Shared repository: https://github.com/shengshu-ai/vidu-s-api
- Git tag: `v0.0.2`
- Marketplace path: `shengshu-ai/vidu_s2/vidu_s2-0.0.2.difypkg`

The existing Vidu S1 plugin remains under `plugins/dify` with identity `shengshu-ai/vidu_s1`. The two source directories and packages must remain isolated. The repository already uses tag `v0.0.1` for S1, so the first S2 GitHub Release uses `v0.0.2` even though S2 is a new Marketplace plugin.

## Pre-Release Checks

Run from the repository root with Python 3.12 and the Dify Plugin CLI:

```powershell
$env:PYTHONPATH = (Resolve-Path "plugins/dify-s2").Path
plugins/dify-s2/.venv/Scripts/python.exe -m pytest plugins/dify-s2/tests
git diff -- plugins/dify
dify plugin package ./plugins/dify-s2 -o vidu_s2-0.0.2.difypkg
tar -tf ./vidu_s2-0.0.2.difypkg
Get-FileHash ./vidu_s2-0.0.2.difypkg -Algorithm SHA256
```

The S1 diff must be empty. The package must not contain tests, virtual environments, caches, `.env`, private keys, Git metadata, S1 source files, or unexplained executables.

Before public release, install the package in a test Dify workspace and verify both regions as available, all declared Workflow variables, one real Avatar session, one real Editing session, session lookup, voice lookup, and sensitive structured output handling.

## GitHub Release

Create the release only after the S2 source has been merged into the repository's main line:

```powershell
git tag -a v0.0.2 -m "Vidu S2 Dify Plugin v0.0.2"
git push origin v0.0.2
gh release create v0.0.2 ./vidu_s2-0.0.2.difypkg `
  --repo shengshu-ai/vidu-s-api `
  --title "Vidu S2 Dify Plugin v0.0.2" `
  --notes "Initial Vidu S2 Dify plugin release with Avatar and Editing session tools."
```

The `v0.0.2` Release should contain only `vidu_s2-0.0.2.difypkg` for the S2 plugin. Do not replace or delete the S1 `v0.0.1` Release.

Users install from GitHub with https://github.com/shengshu-ai/vidu-s-api and select `v0.0.2`. Merely committing a `.difypkg` to the source tree is not a GitHub Release.

## Dify Marketplace

Submit S2 as a **New plugin**, not an update to S1. In a fork of `langgenius/dify-plugins`, add exactly:

```text
shengshu-ai/vidu_s2/vidu_s2-0.0.2.difypkg
```

The Marketplace PR should normally contain only that new package. Select Medium risk and disclose that the plugin:

- Creates potentially billable real-time sessions.
- Sends persona text, character images, Editing reference images, and session parameters to fixed Vidu HTTPS endpoints.
- Returns sensitive `rtc.token` values and an optional Editing `client_secret` as structured Workflow output.
- Does not execute arbitrary code, access the local filesystem, join RTC, or maintain the Vidu control WebSocket.

Include the source repository, privacy policy, support URL, automated test results, Cloud or Community Edition validation performed, and maintenance commitment.

## Future Versions

Every published package uses a new manifest version and a unique repository-level Git tag. Because S1 and S2 share one repository, maintainers must coordinate tag numbers between both plugins. Never reuse or overwrite a published package version or tag.
