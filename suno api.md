# suno api

---

<div align="center">
  <h1 align="center"">
      Suno AI API
  </h1>
  <p>Use API to call the music generation AI of Suno.ai and easily integrate it into agents like GPTs.</p>
  <p>👉 We update quickly, please star.</p>
</div>
<p align="center">
  <a target="_blank" href="./README.md">English</a>
  | <a target="_blank" href="./README_CN.md">简体中文</a>
  | <a target="_blank" href="https://suno.gcui.ai">Demo</a>
  | <a target="_blank" href="https://suno.gcui.ai/docs">Docs</a>
  | <a target="_blank" href="https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fgcui-art%2Fsuno-api&env=SUNO_COOKIE&project-name=suno-api&repository-name=suno-api">Deploy with Vercel</a>
</p>
<p align="center">
  <a href="https://www.producthunt.com/products/gcui-art-suno-api-open-source-sunoai-api/reviews?utm_source=badge-product_review&utm_medium=badge&utm_souce=badge-gcui&#0045;art&#0045;suno&#0045;api&#0045;open&#0045;source&#0045;sunoai&#0045;api" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/product_review.svg?product_id=577408&theme=light" alt="gcui&#0045;art&#0047;suno&#0045;api&#0058;Open&#0045;source&#0032;SunoAI&#0032;API - Use&#0032;API&#0032;to&#0032;call&#0032;the&#0032;music&#0032;generation&#0032;AI&#0032;of&#0032;suno&#0046;ai&#0046; | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>
</p>

> 🔥 Check out our new open-source project: [Album AI - Chat with your gallery using plain language!](https://github.com/gcui-art/album-ai)

![suno-api banner](https://github.com/gcui-art/suno-api/blob/main/public/suno-banner.png)

## Introduction

Suno.ai v3 is an amazing AI music service. Although the official API is not yet available, we couldn't wait to integrate its capabilities somewhere.

We discovered that some users have similar needs, so we decided to open-source this project, hoping you'll like it.

## Demo

We have deployed an example bound to a free Suno account, so it has daily usage limits, but you can see how it runs:
[suno.gcui.ai](https://suno.gcui.ai)

## Features

- Perfectly implements the creation API from app.suno.ai
- Automatically keep the account active.
- Compatible with the format of OpenAI’s `/v1/chat/completions` API.
- Supports Custom Mode
- One-click deployment to Vercel
- In addition to the standard API, it also adapts to the API Schema of Agent platforms like GPTs and Coze, so you can use it as a tool/plugin/Action for LLMs and integrate it into any AI Agent.
- Permissive open-source license, allowing you to freely integrate and modify.

## Getting Started

### 1. Obtain the cookie of your app.suno.ai account

1. Head over to [app.suno.ai](https://app.suno.ai) using your browser.
2. Open up the browser console: hit `F12` or access the `Developer Tools`.
3. Navigate to the `Network tab`.
4. Give the page a quick refresh.
5. Identify the request that includes the keyword `client?_clerk_js_version`.
6. Click on it and switch over to the `Header` tab.
7. Locate the `Cookie` section, hover your mouse over it, and copy the value of the Cookie.

![get cookie](https://github.com/gcui-art/suno-api/blob/main/public/get-cookie-demo.gif)

### 2. Clone and deploy this project

You can choose your preferred deployment method:

#### Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fgcui-art%2Fsuno-api&env=SUNO_COOKIE&project-name=suno-api&repository-name=suno-api)

#### Run locally

```bash
git clone https://github.com/gcui-art/suno-api.git
cd suno-api
npm install
```

Alternatively, you can use [Docker Compose](https://docs.docker.com/compose/)

```bash
docker compose build && docker compose up
```

### 3. Configure suno-api

- If deployed to Vercel, please add an environment variable `SUNO_COOKIE` in the Vercel dashboard, with the value of the cookie obtained in the first step.

- If you’re running this locally, be sure to add the following to your `.env` file:

```bash
SUNO_COOKIE=<your-cookie>
```

### 4. Run suno api

- If you’ve deployed to Vercel:
  - Please click on Deploy in the Vercel dashboard and wait for the deployment to be successful.
  - Visit the `https://<vercel-assigned-domain>/api/get_limit` API for testing.
- If running locally:
  - Run `npm run dev`.
  - Visit the `http://localhost:3000/api/get_limit` API for testing.
- If the following result is returned:

```json
{
  "credits_left": 50,
  "period": "day",
  "monthly_limit": 50,
  "monthly_usage": 50
}
```

it means the program is running normally.

### 5. Use Suno API

You can check out the detailed API documentation at :
[suno.gcui.ai/docs](https://suno.gcui.ai/docs)

## API Reference

Suno API currently mainly implements the following APIs:

```bash
- `/api/generate`: Generate music
- `/v1/chat/completions`: Generate music - Call the generate API in a format that works with OpenAI’s API.
- `/api/custom_generate`: Generate music (Custom Mode, support setting lyrics, music style, title, etc.)
- `/api/generate_lyrics`: Generate lyrics based on prompt
- `/api/get`: Get music information based on the id. Use “,” to separate multiple ids.
    If no IDs are provided, all music will be returned.
- `/api/get_limit`: Get quota Info
- `/api/extend_audio`: Extend audio length
- `/api/clip`: Get clip information based on ID passed as query parameter `id`
- `/api/concat`: Generate the whole song from extensions
```

For more detailed documentation, please check out the demo site:
[suno.gcui.ai/docs](https://suno.gcui.ai/docs)

## API Integration Code Example

### Python

```python
import time
import requests

# replace your vercel domain
base_url = 'http://localhost:3000'


def custom_generate_audio(payload):
    url = f"{base_url}/api/custom_generate"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()


def extend_audio(payload):
    url = f"{base_url}/api/extend_audio"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()

def generate_audio_by_prompt(payload):
    url = f"{base_url}/api/generate"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()


def get_audio_information(audio_ids):
    url = f"{base_url}/api/get?ids={audio_ids}"
    response = requests.get(url)
    return response.json()


def get_quota_information():
    url = f"{base_url}/api/get_limit"
    response = requests.get(url)
    return response.json()

def get_clip(clip_id):
    url = f"{base_url}/api/clip?id={clip_id}"
    response = requests.get(url)
    return response.json()

def generate_whole_song(clip_id):
    payloyd = {"clip_id": clip_id}
    url = f"{base_url}/api/concat"
    response = requests.post(url, json=payload)
    return response.json()


if __name__ == '__main__':
    data = generate_audio_by_prompt({
        "prompt": "A popular heavy metal song about war, sung by a deep-voiced male singer, slowly and melodiously. The lyrics depict the sorrow of people after the war.",
        "make_instrumental": False,
        "wait_audio": False
    })

    ids = f"{data[0]['id']},{data[1]['id']}"
    print(f"ids: {ids}")

    for _ in range(60):
        data = get_audio_information(ids)
        if data[0]["status"] == 'streaming':
            print(f"{data[0]['id']} ==> {data[0]['audio_url']}")
            print(f"{data[1]['id']} ==> {data[1]['audio_url']}")
            break
        # sleep 5s
        time.sleep(5)

```

### Js

```js
const axios = require("axios");

// replace your vercel domain
const baseUrl = "http://localhost:3000";

async function customGenerateAudio(payload) {
  const url = `${baseUrl}/api/custom_generate`;
  const response = await axios.post(url, payload, {
    headers: { "Content-Type": "application/json" },
  });
  return response.data;
}

async function generateAudioByPrompt(payload) {
  const url = `${baseUrl}/api/generate`;
  const response = await axios.post(url, payload, {
    headers: { "Content-Type": "application/json" },
  });
  return response.data;
}

async function extendAudio(payload) {
  const url = `${baseUrl}/api/extend_audio`;
  const response = await axios.post(url, payload, {
    headers: { "Content-Type": "application/json" },
  });
  return response.data;
}

async function getAudioInformation(audioIds) {
  const url = `${baseUrl}/api/get?ids=${audioIds}`;
  const response = await axios.get(url);
  return response.data;
}

async function getQuotaInformation() {
  const url = `${baseUrl}/api/get_limit`;
  const response = await axios.get(url);
  return response.data;
}

async function getClipInformation(clipId) {
  const url = `${baseUrl}/api/clip?id=${clipId}`;
  const response = await axios.get(url);
  return response.data;
}

async function main() {
  const data = await generateAudioByPrompt({
    prompt:
      "A popular heavy metal song about war, sung by a deep-voiced male singer, slowly and melodiously. The lyrics depict the sorrow of people after the war.",
    make_instrumental: false,
    wait_audio: false,
  });

  const ids = `${data[0].id},${data[1].id}`;
  console.log(`ids: ${ids}`);

  for (let i = 0; i < 60; i++) {
    const data = await getAudioInformation(ids);
    if (data[0].status === "streaming") {
      console.log(`${data[0].id} ==> ${data[0].audio_url}`);
      console.log(`${data[1].id} ==> ${data[1].audio_url}`);
      break;
    }
    // sleep 5s
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }
}

main();
```

## Integration with Custom Agents

You can integrate Suno AI as a tool/plugin/action into your AI agent.

### Integration with GPTs

[coming soon...]

### Integration with Coze

[coming soon...]

### Integration with LangChain

[coming soon...]

## Contributing

There are four ways you can support this project:

1. Fork and Submit Pull Requests: We welcome any PRs that enhance the component or editor.
2. Open Issues: We appreciate reasonable suggestions and bug reports.
3. Donate: If this project has helped you, consider buying us a coffee using the Sponsor button at the top of the project. Cheers! ☕
4. Spread the Word: Recommend this project to others, star the repo, or add a backlink after using the project.

## Questions, Suggestions, Issues, or Bugs?

We use GitHub Issues to manage feedback. Feel free to open an issue, and we'll address it promptly.

## License

LGPL-3.0 or later

## Related Links

- Project repository: [github.com/gcui-art/suno-api](https://github.com/gcui-art/suno-api)
- Suno.ai official website: [suno.ai](https://suno.ai)
- Demo: [suno.gcui.ai](https://suno.gcui.ai)
- Album AI: [Auto generate image metadata and chat with the album. RAG + Album.](https://github.com/gcui-art/album-ai)

## Statement

suno-api is an unofficial open source project, intended for learning and research purposes only.

## 👋 Introduction

Suno.ai v3 is an amazing AI music service. Although the official API is not yet available, we couldn't wait to integrate its capabilities somewhere.

We discovered that some users have similar needs, so we decided to open-source this project, hoping you'll like it.

We update quickly, please star us on Github: [github.com/gcui-art/suno-api](https://github.com/gcui-art/suno-api) ⭐

## 🌟 Features

- Perfectly implements the creation API from `app.suno.ai`
- Compatible with the format of OpenAI’s `/v1/chat/completions` API.
- Automatically keep the account active.
- Supports `Custom Mode`
- One-click deployment to Vercel
- In addition to the standard API, it also adapts to the API Schema of Agent platforms like GPTs and Coze, so you can use it as a tool/plugin/Action for LLMs and integrate it into any AI Agent.
- Permissive open-source license, allowing you to freely integrate and modify.

## 🚀 Getting Started

### 1\. Obtain the cookie of your app.suno.ai account

1. Head over to [app.suno.ai](https://app.suno.ai/) using your browser.
2. Open up the browser console: hit `F12` or access the `Developer Tools`.
3. Navigate to the `Network tab`.
4. Give the page a quick refresh.
5. Identify the request that includes the keyword `client?_clerk_js_version`.
6. Click on it and switch over to the `Header` tab.
7. Locate the `Cookie` section, hover your mouse over it, and copy the value of the Cookie.

Your browser does not support frames.

### 2\. Clone and deploy this project

You can choose your preferred deployment method:

#### Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fgcui-art%2Fsuno-api&env=SUNO_COOKIE&project-name=suno-api&repository-name=suno-api)

#### Run locally

```bash
git clone https://github.com/gcui-art/suno-api.git cd suno-api npm install
```

### 3\. Configure suno-api

- If deployed to Vercel, please add an environment variable `SUNO_COOKIE` in the Vercel dashboard, with the value of the cookie obtained in the first step.

- If you’re running this locally, be sure to add the following to your `.env` file:

    ```bash
    SUNO_COOKIE=<your-cookie>
    ```

### 4\. Run suno-api

- If you’ve deployed to Vercel:

  - Please click on Deploy in the Vercel dashboard and wait for the deployment to be successful.
  - Visit the `https://<vercel-assigned-domain>/api/get_limit` API for testing.
- If running locally:

  - Run `npm run dev`.
  - Visit the `http://localhost:3000/api/get_limit` API for testing.
- If the following result is returned:

    ```json
    { "credits_left": 50, "period": "day", "monthly_limit": 50, "monthly_usage": 50 }
    ```

it means the program is running normally.

### 5\. Use Suno API

You can check out the detailed API documentation at [suno.gcui.art/docs](https://suno.gcui.art/docs).

## 📚 API Reference

Suno API currently mainly implements the following APIs:

```bash
- `/api/generate`: Generate music - `/v1/chat/completions`: Generate music - Call the generate API in a format that works with OpenAI’s API. - `/api/custom_generate`: Generate music (Custom Mode, support setting lyrics, music style, title, etc.) - `/api/generate_lyrics`: Generate lyrics based on prompt - `/api/get`: Get music list - `/api/get?ids=`: Get music Info by id, separate multiple id with ",". - `/api/get_limit`: Get quota Info - `/api/extend_audio`: Extend audio length
```

For more detailed documentation, please check out the demo site:

👉 [suno.gcui.art/docs](https://suno.gcui.art/docs)

---

### default

It will automatically fill in the lyrics.

2 audio files will be generated for each request, consuming a total of 10 credits.

`wait_audio` can be set to API mode:

• By default, it is set to `false`, which indicates the background mode. It will only return audio task information, and you will need to call the get API to retrieve detailed audio information.

• If set to `true`, it simulates synchronous mode. The API will wait for a maximum of 100s until the audio is generated, and will directly return the audio link and other information. Recommend using in GPTs and other agents.

```json
{ "prompt": "A popular heavy metal song about war, sung by a deep-voiced male singer, slowly and melodiously. The lyrics depict the sorrow of people after the war.", "make_instrumental": false, "wait_audio": false }
```

| Code | Description | Links |
| --- | --- | --- |
| 200 |
success

<small>Media type</small>

<small>Controls <code>Accept</code> header.</small>

```json
[ { "0": { "id": "string", "title": "string", "image_url": "string", "lyric": "string", "audio_url": "string", "video_url": "string", "created_at": "string", "model_name": "string", "status": "string", "gpt_description_prompt": "string", "prompt": "string", "type": "string", "tags": "string" }, "1": { "id": "string", "title": "string", "image_url": "string", "lyric": "string", "audio_url": "string", "video_url": "string", "created_at": "string", "model_name": "string", "status": "string", "gpt_description_prompt": "string", "prompt": "string", "type": "string", "tags": "string" } } ]
```

 | *No links* |

Convert the `/api/generate` API to be compatible with the OpenAI `/v1/chat/completions` API format.

Generally used in OpenAI compatible clients.

```json
{ "prompt": "A popular heavy metal song about war, sung by a deep-voiced male singer, slowly and melodiously. The lyrics depict the sorrow of people after the war." }
```

| Code | Description | Links |
| --- | --- | --- |
| 200 |
success

<small>Media type</small>

<small>Controls <code>Accept</code> header.</small>

```json
{ "data": "string" }
```

 | *No links* |

The custom mode enables users to provide additional details about the music, such as music genre, lyrics, and more.

2 audio files will be generated for each request, consuming a total of 10 credits.

`wait_audio` can be set to API mode:

• By default, it is set to false, which indicates the background mode. It will only return audio task information, and you will need to call the get API to retrieve detailed audio information.

• If set to true, it simulates synchronous mode. The API will wait for a maximum of 100s until the audio is generated, and will directly return the audio link and other information. Recommend using in GPTs and other agents.

```json
{ "prompt": "[Verse 1]\nCruel flames of war engulf this land\nBattlefields filled with death and dread\nInnocent souls in darkness, they rest\nMy heart trembles in this silent test\n\n[Verse 2]\nPeople weep for loved ones lost\nBattered bodies bear the cost\nSeeking peace and hope once known\nOur grief transforms to hearts of stone\n\n[Chorus]\nSilent battlegrounds, no birds' song\nShadows of war, where we don't belong\nMay flowers of peace bloom in this place\nLet's guard this precious dream with grace\n\n[Bridge]\nThrough the ashes, we will rise\nHand in hand, towards peaceful skies\nNo more sorrow, no more pain\nTogether, we'll break these chains\n\n[Chorus]\nSilent battlegrounds, no birds' song\nShadows of war, where we don't belong\nMay flowers of peace bloom in this place\nLet's guard this precious dream with grace\n\n[Outro]\nIn unity, our strength will grow\nA brighter future, we'll soon know\nFrom the ruins, hope will spring\nA new dawn, we'll together bring", "tags": "pop metal male melancholic", "title": "Silent Battlefield", "make_instrumental": false, "wait_audio": false }
```

| Code | Description | Links |
| --- | --- | --- |
| 200 |
success

<small>Media type</small>

<small>Controls <code>Accept</code> header.</small>

```json
[ { "0": { "id": "string", "title": "string", "image_url": "string", "lyric": "string", "audio_url": "string", "video_url": "string", "created_at": "string", "model_name": "string", "status": "string", "gpt_description_prompt": "string", "prompt": "string", "type": "string", "tags": "string" }, "1": { "id": "string", "title": "string", "image_url": "string", "lyric": "string", "audio_url": "string", "video_url": "string", "created_at": "string", "model_name": "string", "status": "string", "gpt_description_prompt": "string", "prompt": "string", "type": "string", "tags": "string" } } ]
```

 | *No links* |

```json
{ "audio_id": "e76498dc-6ab4-4a10-a19f-8a095790e28d", "prompt": "", "continue_at": "109.96", "title": "", "tags": "" }
```

Generate lyrics based on Prompt.

```json
{ "prompt": "A soothing lullaby" }
```

| Code | Description | Links |
| --- | --- | --- |
| 200 |
success

<small>Media type</small>

<small>Controls <code>Accept</code> header.</small>

```json
{ "text": "string", "title": "string", "status": "string" }
```

 | *No links* |

| Name | Description |
| --- | --- |
|
ids

string

(query)

 |

Audio IDs, separated by commas. Leave blank to return a list of all music.

 |

| Code | Description | Links |
| --- | --- | --- |
| 200 |
success

<small>Media type</small>

<small>Controls <code>Accept</code> header.</small>

```json
[ { "0": { "id": "string", "title": "string", "image_url": "string", "lyric": "string", "audio_url": "string", "video_url": "string", "created_at": "string", "model_name": "string", "status": "string", "gpt_description_prompt": "string", "prompt": "string", "type": "string", "tags": "string" }, "1": { "id": "string", "title": "string", "image_url": "string", "lyric": "string", "audio_url": "string", "video_url": "string", "created_at": "string", "model_name": "string", "status": "string", "gpt_description_prompt": "string", "prompt": "string", "type": "string", "tags": "string" } } ]
```

 | *No links* |

| Code | Description | Links |
| --- | --- | --- |
| 200 |
success

<small>Media type</small>

<small>Controls <code>Accept</code> header.</small>

```json
{ "credits_left": 0, "period": "string", "monthly_limit": 0, "monthly_usage": 0 }
```

 | *No links* |

{

<table><tbody><tr><td>description:</td><td><p>Audio Info</p></td></tr><tr><td>id<span>*</span></td><td><span><span><span><span>string</span><p>audio id</p></span></span></span></td></tr><tr><td>title<span>*</span></td><td><span><span><span><span>string</span><p>music title</p></span></span></span></td></tr><tr><td>image_url<span>*</span></td><td><span><span><span><span>string</span><p>music cover image</p></span></span></span></td></tr><tr><td>lyric<span>*</span></td><td><span><span><span><span>string</span><p>music lyric</p></span></span></span></td></tr><tr><td>audio_url<span>*</span></td><td><span><span><span><span>string</span><p>music download url</p></span></span></span></td></tr><tr><td>video_url<span>*</span></td><td><span><span><span><span>string</span><p>Music video download link, can be used to share</p></span></span></span></td></tr><tr><td>created_at<span>*</span></td><td><span><span><span><span>string</span><p>Create time</p></span></span></span></td></tr><tr><td>model_name<span>*</span></td><td><span><span><span><span>string</span><p>suno model name, chirp-v3</p></span></span></span></td></tr><tr><td>status<span>*</span></td><td><span><span><span><span>string</span><p>The generated states include submitted, queue, streaming, complete.</p></span></span></span></td></tr><tr><td>gpt_description_prompt<span>*</span></td><td><span><span><span><span>string</span><p>Simple mode on user input prompt, Suno will generate formal prompts, lyrics, etc.</p></span></span></span></td></tr><tr><td>prompt<span>*</span></td><td><span><span><span><span>string</span><p>The final prompt for executing the generation task, customized by the user in custom mode, automatically generated by Suno in simple mode.</p></span></span></span></td></tr><tr><td>type<span>*</span></td><td><span><span><span><span>string</span><p>Type</p></span></span></span></td></tr><tr><td>tags<span>*</span></td><td><span><span><span><span>string</span><p>Music genre. User-provided in custom mode, automatically generated by Suno in simple mode.</p></span></span></span></td></tr></tbody></table>

}
