---
title: 火山引擎 OpenAPI 与语音配置
tags:
  - 数字人项目
  - 火山引擎
  - OpenAPI
  - 豆包语音
  - API配置
created: 2026-07-04
---

# 火山引擎 OpenAPI 与语音配置

这篇笔记专门记录“不是火山方舟 Ark 模型 API”的接口，避免和 `ark_config.json` 混用。

## 三套 API 边界

### 火山方舟 Ark API

用途：语言模型、向量模型、图片生成、视频生成，例如 `ark-code-latest`、Seedream、Seedance。

鉴权：Agent/Coding Plan 页面里的“专属 API Key”，本地字段是 `ARK_API_KEY`，请求头一般是 Bearer。

配置文件：

```text
ark_config.json
scripts/ark_api.py
scripts/ark_chat_smoke_test.py
scripts/ark_video_task.py
```

常见域名：

```text
https://ark.cn-beijing.volces.com/api/plan/v3
```

### 火山引擎 OpenAPI

用途：智能视觉、数字人、TOS 对象存储、IAM 等云服务接口。

鉴权：`VOLCENGINE_ACCESS_KEY_ID` / `VOLCENGINE_SECRET_ACCESS_KEY` 或 TOS 专用 AK/SK，走火山引擎 OpenAPI 签名，不是 Ark Bearer。

配置文件：

```text
digital_human_config.json
scripts/digital_human_video_task.py
scripts/tos_audio_upload.py
```

数字人口播常见接口：

```text
Endpoint: https://visual.volcengineapi.com
Service: cv
Region: cn-beijing
Version: 2024-06-06
Submit Action: RealmanAvatarCreationTaskSubmitTask
Query Action: RealmanAvatarCreationTaskGetResult
```

TOS 用途：

```text
把本地旁白音频上传到对象存储，生成可访问的 audio_url，再交给数字人口播接口。
```

### 豆包语音 openspeech API

用途：复刻声音、TTS、ASR。

鉴权：优先使用语音控制台“API Key 管理”里的语音模型 API Key，本地字段是 `DOUBAO_SPEECH_API_KEY`；也可以继续使用豆包语音服务的 `APP_ID` + `Access Token`。这不是方舟 Agent Plan 的 `ARK_API_KEY`。

配置文件：

```text
doubao_speech_config.json
scripts/doubao_tts_synthesize.py
```

`.env.local` 中对应字段：

```env
DOUBAO_SPEECH_API_KEY=截图里的语音模型API Key
DOUBAO_SPEECH_APP_ID=你的语音服务APP_ID
DOUBAO_SPEECH_ACCESS_TOKEN=你的语音服务AccessToken
DOUBAO_TTS_RESOURCE_ID=seed-icl-2.0
```

常见地址：

```text
https://openspeech.bytedance.com/api/v3/tts/unidirectional
https://openspeech.bytedance.com/api/v3/plan/tts/unidirectional
```

## 当前项目调用关系

```text
写文案
-> doubao_speech_config.json 生成复刻声音旁白
-> scripts/tos_audio_upload.py 上传旁白，得到 audio_url
-> digital_human_config.json 调火山引擎数字人口播 OpenAPI
-> ark_config.json 只在需要方舟模型生成文案、图片或视频时使用
```

## 不要混用

- 不要把数字人 `visual.volcengineapi.com` 接口放进 `ark_config.json`。
- 不要用 `ARK_API_KEY` 直接调用火山引擎 OpenAPI 数字人接口。
- 不要把语音模型 API Key 写进 `ARK_API_KEY`，它应该写进 `DOUBAO_SPEECH_API_KEY`。
- 不要把豆包语音 openspeech 当成普通方舟 Chat/Responses 接口。
- `.env.local` 可以集中保存本机密钥，但文档里不记录真实密钥。
