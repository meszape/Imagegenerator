# Multi-provider Image Orchestrator

A production-oriented Python 3.12 FastAPI service that orchestrates iterative image generation and editing across OpenAI and Google Gemini while preserving provider-specific behavior.

## Architecture

- **FastAPI API** exposes sessions, turns, provider capabilities, and assets.
- **Provider adapters** isolate OpenAI Responses API `image_generation` behavior and Gemini Google GenAI behavior.
- **SQLite persistence** stores sessions, turns, raw provider payloads, safety profile usage, provider response IDs, and asset metadata.
- **Local asset store** saves images below `data/assets/{session_id}/{turn_index}/` with JSON metadata and SHA256 hashes.
- **Safety abstraction** offers internal profiles (`strict`, `balanced`, `permissive`, `custom`) while mapping only documented provider controls. OpenAI uses the documented image `moderation` knob (`auto` or `low`), while Gemini supports per-category thresholds such as `OFF`, `BLOCK_NONE`, `BLOCK_ONLY_HIGH`, `BLOCK_MEDIUM_AND_ABOVE`, and `BLOCK_LOW_AND_ABOVE`. This project does not invent safety-disabling flags.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
```

Fill in `OPENAI_API_KEY` and/or `GEMINI_API_KEY`. Create OpenAI keys at https://platform.openai.com/api-keys and Google AI Studio keys at https://aistudio.google.com/app/apikey. GPT Image models such as `gpt-image-1`, `gpt-image-1.5`, `gpt-image-2`, and `gpt-image-1-mini` may require OpenAI organization verification before use.

## Environment variables

See `.env.example` for all variables: API keys, `DATABASE_URL`, `ASSET_ROOT`, defaults, fallback enablement, timeouts, and logging.

Model defaults and notable alternatives:

| Provider | Default | Alternative | Notes |
|---|---|---|---|
| OpenAI | `gpt-image-1` | `gpt-image-1.5` | Keep `gpt-image-1` as the safest default for broad compatibility; use `gpt-image-1.5` after organization verification if available. |
| Gemini | `gemini-3.1-flash-image` | `gemini-3-pro-image` | Flash is the fast default; Pro is documented via `GEMINI_PRO_IMAGE_MODEL` for premium complex or multi-reference work. |

Model availability and safety-parameter support change frequently for both providers. Check provider documentation before deploying to production.

## Run locally

```bash
make run
# Open http://localhost:8000/docs
```

## Run tests

```bash
make test
```

## Docker

```bash
docker compose up --build
```

## Curl examples

Create a session:

```bash
curl -X POST http://localhost:8000/sessions \
  -H 'Content-Type: application/json' \
  -d '{"provider":"openai","model":"gpt-image-1.5","default_safety_profile":"balanced"}'
```

Generate an initial image:

```bash
curl -X POST http://localhost:8000/sessions/$SESSION_ID/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"A watercolor fox reading under a lamp","metadata":{"preserve_intent":["keep subject","change lighting"]}}'
```

Follow-up edit turn:

```bash
curl -X POST http://localhost:8000/sessions/$SESSION_ID/edit \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Make the lamp warmer and add rain outside the window"}'
```

List assets and fetch a file:

```bash
curl http://localhost:8000/sessions/$SESSION_ID/assets
curl -L http://localhost:8000/assets/$ASSET_ID/file --output image.png
```

Provider capabilities:

```bash
curl http://localhost:8000/providers/capabilities
```

## CLI usage

```bash
image-service create-session --provider openai --model gpt-image-1.5
image-service generate sess_xxx "A cinematic robot portrait"
image-service history sess_xxx
image-service list-assets sess_xxx
```

## Multi-turn workflow

OpenAI turns prefer `previous_response_id`, persisted from each provider response. Gemini uses bounded context replay (`MAX_TURN_CONTEXT`) because provider state semantics differ. The service stores both raw prompts and normalized instructions; caller metadata can include preserve-intent fields such as `keep subject`, `keep composition`, `change lighting`, and `change style`.

## Provider differences and safety

OpenAI and Gemini safety controls are not equivalent. This service maps internal profiles only to documented provider knobs and never claims to disable provider-enforced policy. Block/failure metadata is recorded instead of hidden.

| Provider | Safety knob | Values | Notes |
|---|---|---|---|
| OpenAI | `image_generation.moderation` | `auto`, `low` | `permissive` and `custom` map to `low` by default; `strict` and `balanced` map to `auto`. A `provider_config` `moderation` override can explicitly choose either documented value. |
| Gemini | Per-category `safety_settings` thresholds | `BLOCK_LOW_AND_ABOVE`, `BLOCK_MEDIUM_AND_ABOVE`, `BLOCK_ONLY_HIGH`, `BLOCK_NONE`, `OFF` | Profiles apply the same threshold to supported adjustable categories, then `custom_safety_settings` can override individual categories. Core harms may remain enforced regardless of threshold. |

### Choosing a safety profile

- `strict`: OpenAI `moderation=auto`; Gemini `BLOCK_LOW_AND_ABOVE`.
- `balanced`: OpenAI `moderation=auto`; Gemini `BLOCK_MEDIUM_AND_ABOVE`.
- `permissive`: OpenAI `moderation=low`; Gemini `BLOCK_NONE`, which remains more observable than `OFF` because safety ratings can still be returned.
- `custom`: OpenAI defaults to `moderation=low` unless `provider_config.moderation` is set; Gemini requires explicit per-category `custom_safety_settings`, including `OFF` where callers intentionally opt into it.

Gemini exposes per-request `SafetySetting` category/threshold controls documented by Google, and responses can include prompt feedback and candidate safety ratings. OpenAI image generation through Responses API is isolated in the OpenAI adapter and exposes capability notes for its documented moderation control.

## Postman-compatible endpoint summary

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Service health |
| POST | `/sessions` | Create session |
| GET | `/sessions/{session_id}` | Session metadata |
| GET | `/sessions/{session_id}/turns` | Turn history |
| POST | `/sessions/{session_id}/generate` | Initial/next image turn |
| POST | `/sessions/{session_id}/edit` | Semantic edit alias |
| GET | `/sessions/{session_id}/assets` | List assets |
| GET | `/assets/{asset_id}` | Asset metadata |
| GET | `/assets/{asset_id}/file` | Image bytes |
| GET | `/providers/capabilities` | Provider feature matrix |
