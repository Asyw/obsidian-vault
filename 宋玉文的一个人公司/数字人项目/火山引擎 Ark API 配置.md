---
title: 火山引擎 Ark API 配置
tags:
  - 数字人项目
  - 火山引擎
  - Ark
  - API配置
created: 2026-07-03
---

# 火山方舟 Ark API 配置

这篇笔记只记录数字人项目中“火山方舟 Ark 模型 API”的本地配置方式，方便 Codex 后续读取配置并调用方舟模型接口。

## API 边界说明

火山引擎和火山方舟不是同一套 API，后续按下面三类分开：

- 火山方舟 Ark API：模型调用接口，使用 Agent/Coding Plan 页面里的“专属 API Key”，本地字段是 `ARK_API_KEY`，主要域名是 `ark.cn-beijing.volces.com`，配置文件是 `ark_config.json`。
- 火山引擎 OpenAPI：数字人、智能视觉、TOS、IAM 等云服务接口，使用 AK/SK 签名，配置见 `digital_human_config.json` 和 `火山引擎 OpenAPI 与语音配置.md`。
- 豆包语音 openspeech API：复刻声音、TTS、ASR，使用豆包语音 App ID / Access Token 或语音专用鉴权，配置见 `doubao_speech_config.json`。

不要把数字人口播 `visual.volcengineapi.com`、TOS、openspeech 语音接口混进 `ark_config.json`。

## 当前状态

- API 配置文件已创建。
- 本地 API Key 已配置在 `.env.local`，但密钥不写入 Obsidian 笔记。
- 已完成一次真实连通测试，返回成功。
- 默认使用 Agent/Coding Plan 的 OpenAI 兼容地址和专属 API Key，避免误用标准 Ark 地址产生额外费用。
- `ark_config.json` 现在只保存方舟模型 API；语音和数字人 OpenAPI 已拆到单独配置。

## 文件位置

项目目录：

```text
/Users/xiaosong/Documents/Obsidian Vault/宋玉文的一个人公司/数字人项目
```

关键文件：

```text
.env.local
.env.local.example
ark_config.json
doubao_speech_config.json
short_video_config.json
digital_human_config.json
scripts/ark_chat_smoke_test.py
scripts/ark_api.py
```

用途说明：

- `.env.local`：本机私有密钥文件，保存 `ARK_API_KEY`、`ARK_MODEL`、`ARK_BASE_URL` 等配置。
- `.env.local.example`：示例模板，不包含真实密钥。
- `ark_config.json`：非敏感配置，只记录火山方舟模型 API 的 Base URL、模型列表、接口路径。
- `doubao_speech_config.json`：非敏感配置，记录豆包语音 openspeech 复刻声音/TTS 接口。
- `short_video_config.json`：短视频生成总配置，支持复刻声音、文生/图生视频、字幕、封面、导出。
- `digital_human_config.json`：火山引擎 OpenAPI 的数字人出镜口播配置，只在需要数字人形象出镜时使用。
- `scripts/ark_chat_smoke_test.py`：读取配置并调用火山 Ark 的测试脚本。
- `scripts/ark_api.py`：统一的火山方舟 API 入口，支持检查配置、Chat、Responses、Embeddings、图片生成、视频任务提交/查询。

## 私有配置

`.env.local` 应保持这种结构：

```env
ARK_API_KEY=你的火山方舟Agent/Coding Plan专属API Key
ARK_MODEL=你的Endpoint或模型ID
ARK_RESPONSES_MODEL=ark-code-latest
ARK_EMBEDDING_MODEL=doubao-embedding-vision
ARK_IMAGE_MODEL=doubao-seedream-5.0-lite
ARK_VIDEO_MODEL=doubao-seedance-1.5-pro
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/plan/v3
ARK_TIMEOUT_SECONDS=60
```

注意：

- 不要把真实 `ARK_API_KEY` 写入 Obsidian 笔记。
- 不要把真实 `ARK_API_KEY` 发到聊天窗口。
- 截图里的“专属 API Key”就是这里的 `ARK_API_KEY`，它不是火山引擎 IAM 的 AccessKey/SecretAccessKey。
- 这个专属 Key 只给 Agent/Coding Plan 的 `/api/plan/v3` 地址用。
- `.env.local` 已被 `.gitignore` 排除。
- `.env.local` 文件权限已收紧为仅本机用户可读写。
- 声音复刻、数字人口播、TOS 的密钥也放在 `.env.local`，但不属于 Ark API；配置说明见 `火山引擎 OpenAPI 与语音配置.md`。

## 接口总表

以后新增方舟模型接口、模型名，统一补到这里和 `ark_config.json` 的 `interface_catalog`。

### 语言模型

```text
模型: ark-code-latest
OpenAI Base URL: https://ark.cn-beijing.volces.com/api/plan/v3
OpenAI Responses: https://ark.cn-beijing.volces.com/api/plan/v3/responses
OpenAI Chat Completions: https://ark.cn-beijing.volces.com/api/plan/v3/chat/completions
Anthropic Base URL: https://ark.cn-beijing.volces.com/api/plan
```

### 向量模型

```text
模型: doubao-embedding-vision
Base URL: https://ark.cn-beijing.volces.com/api/plan/v3
Embeddings: https://ark.cn-beijing.volces.com/api/plan/v3/embeddings
说明: 当前向量模型不支持 Auto 路由。
```

### 文件接口

```text
创建或列出文件:
https://ark.cn-beijing.volces.com/api/plan/v3/files

获取或删除文件:
https://ark.cn-beijing.volces.com/api/plan/v3/files/{file_id}

下载文件内容:
https://ark.cn-beijing.volces.com/api/plan/v3/files/{file_id}/content
```

### 视觉模型

```text
视频模型:
- doubao-seedance-1.5-pro
- doubao-seedream-5.0-lite

创建视频生成任务:
https://ark.cn-beijing.volces.com/api/plan/v3/contents/generations/tasks

查询视频生成任务:
https://ark.cn-beijing.volces.com/api/plan/v3/contents/generations/tasks/{id}

查询视频生成任务列表:
https://ark.cn-beijing.volces.com/api/plan/v3/contents/generations/tasks?page_num={page_num}&page_size={page_size}&filter.status={filter.status}&filter.task_ids={filter.task_ids}&filter.model={filter.model}

取消或删除视频生成任务:
https://ark.cn-beijing.volces.com/api/plan/v3/contents/generations/tasks/{id}

图片生成:
https://ark.cn-beijing.volces.com/api/plan/v3/images/generations
```

### 语音模型

语音复刻、TTS、ASR 使用豆包语音 openspeech API，不属于方舟 Ark 模型 API。语音控制台“API Key 管理”里的 Key 应写到 `.env.local` 的 `DOUBAO_SPEECH_API_KEY`，不要写到 `ARK_API_KEY`。配置见：

```text
doubao_speech_config.json
火山引擎 OpenAPI 与语音配置.md
```

注意：

```text
Agent/Coding Plan 下优先使用 /api/plan/v3 和 /api/v3/plan/tts/... 这些专属地址。
不要误用 https://ark.cn-beijing.volces.com/api/v3 或普通 /api/v3/contents/generations/tasks，否则可能产生额外费用。
```

## Agent Plan 地址

根据火山方舟 Agent/Coding Plan 控制台截图，语言模型应使用：

```text
https://ark.cn-beijing.volces.com/api/plan/v3
```

控制台第三步“配置专属 API Key”里的 Key 对应本项目：

```text
ARK_API_KEY=截图里的专属 API Key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/plan/v3
```

Anthropic 兼容工具使用：

```text
https://ark.cn-beijing.volces.com/api/plan
```

不要用下面这个标准 Ark 地址接入 Agent Plan 额度：

```text
https://ark.cn-beijing.volces.com/api/v3
```

控制台提示：误用标准 Ark 地址可能产生额外费用。

## 统一调用脚本

新增脚本：

```text
scripts/ark_api.py
```

常用命令：

```bash
python3 scripts/ark_api.py check
python3 scripts/ark_api.py chat "你好，用一句话回复"
python3 scripts/ark_api.py responses "写一个短视频标题"
python3 scripts/ark_api.py embeddings "少年强则中国强"
python3 scripts/ark_api.py image "国风少年海报，竖屏"
python3 scripts/ark_api.py video-submit "9:16 竖屏，少年奔跑，晨光，5秒 --ratio 9:16 --fps 24 --dur 5"
python3 scripts/ark_api.py video-query <task_id>
```

脚本读取 `.env.local` 和 `ark_config.json`，不会在终端输出真实 API Key。

## 语言模型

推荐优先使用路由模型：

```text
ark-code-latest
```

控制台截图中可选的模型名包括：

```text
doubao-seed-2.0-code
doubao-seed-2.0-pro
doubao-seed-2.0-lite
doubao-seed-2.0-mini
glm-5.2
kimi-k2.7-code
deepseek-v4-pro
deepseek-v4-flash
minimax-m3
minimax-m2.7
kimi-k2.6
```

如果某个工具不支持 Auto/路由模型，就从上面的模型名中选择一个填到 `ARK_MODEL`。

## 其他模型与接口

向量模型：

```text
doubao-embedding-vision
```

视觉模型：

```text
doubao-seedance-1.5-pro
doubao-seedream-5.0-lite
```

语音资源和接口已移到 `doubao_speech_config.json`，避免和方舟 Ark API 混用。

## 数字人口播视频

注意：当前项目目标已经扩展为“短视频生成”，不只做口播视频。

短视频模式：

```text
hybrid: 复刻声音配音 + 方舟图片/视频生成 + 字幕/封面/剪辑合成
talking_head: 数字人形象出镜口播
visual_story: 无真人出镜的剧情/知识/历史类短视频
image_to_video: 使用图片素材生成动态视频
```

默认使用：

```text
SHORT_VIDEO_MODE=hybrid
SHORT_VIDEO_ASPECT_RATIO=9:16
SHORT_VIDEO_RESOLUTION=1080x1920
```

比例规则：

```text
用户每次可以在剧本或提示词里指定 9:16 或 16:9。
9:16 对应 1080x1920，适合抖音/视频号/小红书竖屏短视频。
16:9 对应 1920x1080，适合 B站/YouTube/横屏课程或纪录片感视频。
如果用户没有指定比例，则默认使用 SHORT_VIDEO_ASPECT_RATIO。
```

完整短视频生成流程：

```text
输入文案
-> 拆成短视频脚本和分镜
-> 用复刻声音生成旁白
-> 用 Seedream/Seedance 生成封面、镜头图、视频片段
-> 生成字幕
-> 按请求比例合成 mp4
-> 保存到 outputs/videos
```

只有在 `SHORT_VIDEO_MODE=talking_head` 时，才必须配置 `DIGITAL_HUMAN_AVATAR_ID`。

当前视频目标：

```text
类型: 数字人口播视频
画幅: 9:16 竖屏
默认分辨率: 1080x1920
```

数字人口播视频相关文件：

```text
digital_human_config.json
```

`.env.local` 中需要补齐这些字段：

```env
VOLCENGINE_ACCESS_KEY_ID=你的火山引擎AccessKeyId
VOLCENGINE_SECRET_ACCESS_KEY=你的火山引擎SecretAccessKey
DIGITAL_HUMAN_AVATAR_ID=你的数字人形象ID
DIGITAL_HUMAN_AUDIO_URL=可公网访问的旁白音频URL
DIGITAL_HUMAN_REQ_KEY=realman_avatar_creation_task
DIGITAL_HUMAN_API_ENDPOINT=https://visual.volcengineapi.com
DIGITAL_HUMAN_API_REGION=cn-beijing
DIGITAL_HUMAN_API_SERVICE=cv
DIGITAL_HUMAN_API_VERSION=2024-06-06
DIGITAL_HUMAN_ASPECT_RATIO=9:16
DIGITAL_HUMAN_RESOLUTION=1080x1920
DIGITAL_HUMAN_VIDEO_FORMAT=mp4
DIGITAL_HUMAN_VIDEO_CODEC=H264
```

说明：

- `ARK_TTS_VOICE_ID` 负责声音。
- `DIGITAL_HUMAN_AVATAR_ID` 负责人物形象。
- `DIGITAL_HUMAN_AUDIO_URL` 是数字人口播接口真正提交任务时需要的音频 URL。
- `DIGITAL_HUMAN_ASPECT_RATIO=9:16` 负责竖屏比例。
- 火山数字人视频接口属于智能视觉服务/图像生成大模型相关能力，可能需要火山 IAM 的 AccessKey/SecretAccessKey，不一定能只用 Ark API Key。
- 真实密钥和真实形象 ID 只放在 `.env.local`，不要写入 Obsidian 笔记。

数字人视频接口要点：

```text
接口地址: https://visual.volcengineapi.com
提交任务: Action=RealmanAvatarCreationTaskSubmitTask&Version=2024-06-06
查询任务: Action=RealmanAvatarCreationTaskGetResult&Version=2024-06-06
Region: cn-beijing
Service: cv
Body 必填: req_key, resource_id, audio_url
```

其中 `resource_id` 对应 `.env.local` 里的 `DIGITAL_HUMAN_AVATAR_ID`。

## 检查命令

检查本地配置是否能读取：

```bash
python3 scripts/ark_chat_smoke_test.py --check
```

检查数字人口播视频配置是否补齐：

```bash
python3 scripts/digital_human_config_check.py
```

预览数字人口播提交参数：

```bash
python3 scripts/digital_human_video_task.py submit --dry-run --audio-url "https://example.com/narration.wav"
```

提交数字人口播视频任务：

```bash
python3 scripts/digital_human_video_task.py submit --audio-url "https://example.com/narration.wav"
```

查询任务结果：

```bash
python3 scripts/digital_human_video_task.py query <task_id>
```

检查完整短视频生成配置是否补齐：

```bash
python3 scripts/short_video_config_check.py
```

检查豆包声音复刻语音合成配置：

```bash
python3 scripts/doubao_tts_synthesize.py --check
```

用你的复刻音色把文本合成旁白音频：

```bash
python3 scripts/doubao_tts_synthesize.py "你好，这是我的复刻声音测试。" --output outputs/audio/test.mp3
```

真实调用测试：

```bash
python3 scripts/ark_chat_smoke_test.py "请只回复：火山API连通成功"
```

已验证返回：

```text
火山API连通成功
```

## 后续给 Codex 使用

以后需要 Codex 调用火山引擎时，直接说明：

```text
请读取数字人项目里的 .env.local 和 ark_config.json，使用火山方舟 Ark API。
如果要做声音复刻/TTS，请读取 doubao_speech_config.json。
如果要做数字人口播/TOS 上传，请读取 digital_human_config.json 和火山引擎 OpenAPI 与语音配置.md。
```

Codex 会从本地文件读取配置，不需要在聊天里暴露密钥。
