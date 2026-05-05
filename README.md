# Agentic Inventory Planning Assistant

An agentic analytics assistant that answers inventory planning questions over forecast outputs using tool-based routing, explainable reasoning, and business-facing recommendations.

This project was built as a beginner-friendly agentic AI system focused on a practical business workflow rather than a generic chatbot. It uses structured forecast data to answer questions such as:

- Which items are highest stockout risk this week?
- What are the top replenishment priorities?
- What is happening in a specific store?
- Why is a specific item high or medium risk?
- What should a planning manager focus on next?

---

## Why this project is agentic

This application is not just a dashboard and not just a chat interface.

It behaves like a lightweight agent by following a structured decision flow:

1. Accept a natural-language user question
2. Extract relevant business entities such as `store_id` and `product_id`
3. Detect the likely user intent
4. Choose and execute the appropriate analysis tool
5. Return an explainable response with:
   - agent reasoning
   - business-facing answer
   - manager recommendation
   - structured table output when useful
   - suggested next questions

This makes the assistant more interactive, explainable, and action-oriented than a static analytics report.

---

## Core capabilities

The assistant currently supports:

- **Portfolio summary**
  - total store-product pairs
  - high / medium / low risk mix
  - total recommended replenishment quantity
  - top priority items

- **Top high-risk items**
  - identifies items with the highest stockout pressure
  - ranks them by recommended order quantity

- **Top replenishment priorities**
  - surfaces the most urgent replenishment actions

- **Store-level summaries**
  - summarizes risk concentration and priority items for a specific store

- **Item-level explanations**
  - explains forecast, lag demand, reorder point, recommended quantity, and risk for a specific store-product pair

- **Manager recommendations**
  - translates raw analytical outputs into short decision-support guidance

- **Suggested next questions**
  - proposes logical follow-up questions to continue the workflow

- **Session chat history**
  - preserves prior turns in the same session
  - keeps older turns compact while keeping the latest turn fully expanded

---

## Example questions

You can ask questions like:

- `Which items are highest risk this week?`
- `Show top replenishment priorities.`
- `Summarize the portfolio.`
- `What is happening in store S005?`
- `Explain S005 P0009.`

---

## Project structure

```text
agentic-inventory-planning-assistant/
├── app/
│   └── app.py
├── agent/
│   ├── __init__.py
│   ├── prompts.py
│   ├── router.py
│   └── tools.py
├── data/
│   └── scored_forecasts.csv
├── requirements.txt
└── README.md
```

---

## How it works

### 1. Tools layer
`agent/tools.py` contains the data-access and analytics functions used by the assistant, including:

- loading scored forecast data
- retrieving top high-risk items
- retrieving top replenishment priorities
- generating store-level summaries
- generating item-level detail views
- summarizing the full portfolio

### 2. Routing layer
`agent/router.py` acts as the assistant’s lightweight planning layer.

It performs:

- store and product ID extraction
- intent detection
- tool selection
- reasoning generation
- suggested follow-up generation

### 3. Prompt / response layer
`agent/prompts.py` turns raw structured outputs into readable business-facing responses and manager recommendations.

### 4. App layer
`app/app.py` provides the Streamlit chat interface and handles:

- chat input
- response rendering
- compact history rendering
- structured tables
- routing transparency

---

## Design choices

This project intentionally uses a **tool-based, rule-guided agent design** instead of jumping immediately to a large language model.

That choice was made to prioritize:

- explainability
- stability
- business grounding
- low complexity for a first agentic AI project
- easy extension later to LLM-based reasoning

This makes the current version a strong foundation for a future LLM-enhanced copilot.

---

## Current UX features

The Streamlit app includes:

- chat-style question flow
- agent reasoning display
- assistant response blocks
- manager recommendation blocks
- structured tabular outputs for ranked list queries
- suggested next questions
- expandable routing details
- compact rendering of older turns
- clear chat history reset

---

## How to run locally

### 1. Clone or download the project
Place the project folder on your machine.

### 2. Create and activate a virtual environment

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python -m streamlit run app/app.py
```

### 5. Open the local URL shown in the terminal
Usually:
```text
http://localhost:8501
```

---

## Data source

This project uses a scored forecast output file:

- `data/scored_forecasts.csv`

This file contains forecast, reorder, replenishment, and risk fields generated from a prior demand forecasting workflow.

Representative fields include:

- `store_id`
- `product_id`
- `predicted_next_week_units_sold`
- `reorder_point`
- `recommended_order_qty`
- `stockout_risk`
- `dominant_seasonality`

---

## Business value

This assistant is designed to demonstrate how agentic AI concepts can be applied to structured analytics workflows.

Instead of only visualizing data, it helps guide the user through:

- risk identification
- replenishment prioritization
- store-level review
- item-level interpretation
- next-step planning

This makes it more aligned with real business decision support than a standard dashboard or toy chatbot.

---

## Future improvements

Potential next steps include:

- integrating an LLM for richer narrative answer generation
- adding conversation memory across sessions
- supporting CSV upload instead of fixed local data
- adding filters for region, seasonality, or risk band
- improving suggestion quality using query history
- adding downloadable action summaries
- adding authentication and deployment
- converting the routing layer into a more advanced multi-step planner

---

## Version status

Current version: **V1**

This version demonstrates:
- tool-based agentic routing
- explainable reasoning
- business-facing recommendations
- compact chat history
- structured planning support over forecast data

---

## Author

**Vikram Dua**

GitHub: `https://github.com/vikramdua1/`
