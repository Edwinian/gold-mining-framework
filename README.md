# Gold Mining Framework

Linear LangGraph pipeline of specialist agents. The current graph is `START -> reddit_query_agent -> END`.

The Reddit query agent searches Reddit for the market idea and stores each result's raw page content. The idea generation agent still runs on its own and keeps market categories whose Google Trends (worldwide, since 2004) slope smoothly upward.

Agents currently call **xAI Grok 4.7** (`xai:grok-4.7`).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `XAI_API_KEY` (current model) and `TAVILY_API_KEY` in `.env`.

## Model

`LLM_MODEL` selects the chat model. It uses the `provider:model` form accepted by LangChain `init_chat_model`. The default is the current model, `xai:grok-4.7`.

| Provider | `LLM_MODEL` example | API key | Package |
| --- | --- | --- | --- |
| xAI (current) | `xai:grok-4.7` | `XAI_API_KEY` | `langchain-xai` (installed with requirements) |
| Anthropic (Claude) | `anthropic:claude-sonnet-4-5` | `ANTHROPIC_API_KEY` | `pip install langchain-anthropic` |
| OpenAI | `openai:gpt-5.5` | `OPENAI_API_KEY` | `pip install langchain-openai` |
| Google Gemini | `google_genai:gemini-2.5-pro` | `GOOGLE_API_KEY` | `pip install langchain-google-genai` |

Gemini uses the `google_genai` prefix so requests go to the Gemini API. Other `init_chat_model` providers work with the same `LLM_MODEL=provider:model` setting once that provider's package and API key are installed.

## Run

From this directory, invoke the idea generation agent on its own:

```bash
python -m idea_generation_agent.invoke "Health"
python -m idea_generation_agent.invoke alternative medicine
```

Run the full pipeline from the parent of this directory (`cd ..`):

```bash
python -m gold_mining_framework "Health"
python -m gold_mining_framework alternative medicine
```
