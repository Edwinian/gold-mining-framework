# Gold Mining Framework

Linear LangGraph pipeline of specialist agents. The current graph is `START -> reddit_query_agent -> pain_point_agent -> market_gap_agent -> landing_page_agent -> END`.

The Reddit query agent searches Reddit for the market idea and stores each result's raw page content. The pain point agent reads those posts and writes a pain-point analysis. The market gap agent reads that analysis and writes solution opportunities. The landing page agent writes those analyses and an HTML page under `landing_pages`. The idea generation agent and the idea picker agent run on their own. Both take an optional `--topic`: `health`, `wealth`, and `relationships` are markets, and any other value is a category. Omit `--topic` for random ideas starting from the market level. Idea generation keeps leaves whose Google Trends (worldwide, since 2004) slope smoothly upward.

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

From this directory, invoke the idea agents on their own. `--topic=health` is a market. `--topic="alternative medicine"` is a category. Omit `--topic` for random ideas starting from the market level (Health, Wealth, and Relationships).

```bash
python -m idea_generation_agent.invoke --topic=health
python -m idea_generation_agent.invoke --topic="alternative medicine"
python -m idea_generation_agent.invoke
python -m idea_picker_agent.invoke --topic=health
python -m idea_picker_agent.invoke --topic="alternative medicine"
python -m idea_picker_agent.invoke
```

Run the graph from this directory:

```bash
python -m gold_mining_framework --idea=coparenting
python -m gold_mining_framework --idea "alternative medicine"
```

## Landing Pages

The graph ends at `landing_page_agent`. That agent reads the market idea, the pain-point analysis, and the market-gap analysis, then writes a folder under `landing_pages`. The folder name is the idea in snake case.

For `python -m gold_mining_framework --idea=coparenting`, the files are:

```text
landing_pages/coparenting/pain_points.md
landing_pages/coparenting/market_gaps.md
landing_pages/coparenting/coparenting.html
```

`pain_points.md` and `market_gaps.md` are the analyses from the previous agents. `coparenting.html` is a self-contained landing page generated from those analyses. Open that HTML file in a browser. The command itself prints the market-gap analysis to the terminal.
