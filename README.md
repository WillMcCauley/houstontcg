# Houston TCG AI Sales and Support Copilot

Houston TCG now includes a real AI-oriented storefront copilot architecture instead of a browser-only keyword chatbot. The project combines a static storefront frontend with a FastAPI backend that handles intent classification, semantic product retrieval, recommendation logic, grounded store-policy answers, and analytics logging.

This is designed to support resume-quality claims such as:

- Built an AI sales and support copilot for a real storefront
- Combined intent classification, semantic retrieval, recommendation logic, and business-policy grounding
- Connected conversational AI to live product inventory and purchase pathways
- Added analytics for customer behavior, fallback rate, and top product demand

## System Overview

The storefront is still a lightweight HTML/CSS/JS site, but the product intelligence has moved into a backend service.

### Frontend

- `index.html`: storefront shell and floating chat widget
- `styles.css`: storefront design, chat styling, product card layout, and responsive behavior
- `app.js`: API-driven catalog rendering, copilot chat integration, loading/error states, and click logging

### Backend

- `backend/main.py`: FastAPI entrypoint
- `backend/routes/`: API routes for chat, products, analytics, search, and feedback
- `backend/services/`: modular copilot logic
- `backend/data/`: editable inventory, business-policy knowledge, eval prompts, and analytics database

## Architecture

### 1. Product Catalog Layer

Inventory is stored in `backend/data/products.json` instead of hardcoded frontend arrays.

Each product record includes:

- `id`
- `title`
- `category`
- `description`
- `tags`
- `keywords`
- `price`
- `listing_url`
- `image_url`
- `availability`
- `bundle_options`

This makes the storefront inventory easy to update without touching multiple code paths.

### 2. Intent Classification

`backend/services/intent_classifier.py` provides the first-pass intent classifier.

Supported intents:

- `product_search`
- `recommendation`
- `bundle_inquiry`
- `availability`
- `shipping_pickup`
- `payment`
- `purchase_help`
- `general_help`
- `greeting`
- `fallback`

The current implementation is rule-based with confidence scoring and is structured so embeddings or a lightweight classifier can replace or augment it later.

### 3. Semantic Product Search

`backend/services/semantic_search.py` implements a local semantic retrieval layer using:

- token expansion
- synonym mapping
- weighted title/tag/keyword matching
- cosine-style scoring over token counters
- category and phrase bonuses

This supports queries like:

- “best gift for a Pokemon fan”
- “show me something collectible”
- “what’s good for a kid”
- “what’s similar to the iPhone listing”

The design is intentionally pluggable so OpenAI embeddings can be introduced later without rewriting the full stack.

### 4. Recommendation Engine

`backend/services/recommender.py` ranks products using:

- semantic search score
- tag overlap
- category relevance
- bundle intent
- query-specific signals such as `gift`, `pokemon`, `kids`, `bundle`, and `mtg`

Every recommendation includes an explanation string so the assistant can justify why the product was suggested.

### 5. Knowledge Retrieval Layer

`backend/services/knowledge_base.py` retrieves grounded policy snippets from `backend/data/policies.json`.

This knowledge base currently covers:

- payment methods
- pickup options
- shipping guidance
- Facebook Marketplace purchase flow
- bundle guidance
- support/contact rules
- availability expectations

This keeps policy answers tied to known business rules instead of generic filler text.

### 6. Response Composer

`backend/services/response_builder.py` combines:

- detected intent
- semantic search results
- recommendations
- retrieved store policies

The backend returns structured responses with:

- short answer
- next action
- product suggestions
- policy hits
- fallback flag
- response type

### 7. Analytics and Logging

`backend/services/analytics_service.py` stores interactions in `backend/data/copilot_analytics.db` using SQLite.

Logged interaction fields include:

- timestamp
- session id
- raw query
- detected intent
- confidence
- response type
- fallback flag
- matched products
- recommended products
- policy hits

Feedback logging also supports click-through capture from:

- product grid cards
- chat recommendation cards

`GET /api/analytics/summary` returns:

- top customer intents
- most requested products
- top categories
- fallback rate
- recommendation frequency
- feedback event counts

## API Routes

### `GET /health`

Basic service health check.

### `GET /api/products`

Returns the structured storefront catalog used by the frontend.

### `POST /api/chat`

Accepts:

```json
{
  "message": "best gift for a Pokemon fan",
  "session_id": "optional-session-id",
  "limit": 3
}
```

Returns structured chat output including:

- `intent`
- `confidence`
- `answer`
- `next_action`
- `products`
- `policy_hits`
- `fallback`
- `analytics_id`

### `POST /api/search`

Direct semantic search endpoint for product retrieval experiments and debugging.

### `GET /api/analytics/summary`

Returns aggregate metrics for logged storefront interactions.

### `POST /api/feedback`

Logs click-through or other UI feedback events, such as recommendation clicks.

## Folder Structure

```text
houston_tcg_site/
  index.html
  styles.css
  app.js
  images/
  backend/
    main.py
    routes/
      analytics.py
      chat.py
      feedback.py
      products.py
    services/
      analytics_service.py
      catalog_service.py
      intent_classifier.py
      knowledge_base.py
      recommender.py
      response_builder.py
      runtime.py
      semantic_search.py
    data/
      copilot_analytics.db
      eval_prompts.json
      policies.json
      products.json
    models/
      schemas.py
    scripts/
      run_eval.py
    requirements.txt
  README.md
```

## Local Setup

### 1. Frontend

Serve the storefront locally from the project root:

```bash
cd /Users/will/Documents/CodexRequests/houston_tcg_site
python3 -m http.server 8000
```

Then open:

`http://localhost:8000`

### 2. Backend

Install dependencies:

```bash
cd /Users/will/Documents/CodexRequests/houston_tcg_site
python3 -m pip install -r backend/requirements.txt
```

Run the FastAPI service:

```bash
cd /Users/will/Documents/CodexRequests/houston_tcg_site
uvicorn backend.main:app --reload --port 8001
```

The frontend is configured to call:

`http://127.0.0.1:8001`

If you want a different backend URL, set:

```js
window.HOUSTON_TCG_API_BASE = "http://127.0.0.1:9000";
```

before loading `app.js`.

## Frontend Behavior

The frontend now:

- loads product inventory from the backend API
- falls back to `backend/data/products.json` for catalog rendering if the API is offline
- sends chat messages to `POST /api/chat`
- renders structured product recommendation cards inside chat
- shows loading and offline states
- logs click-through events through `POST /api/feedback`

This means the storefront can still display products if the backend is down, while the copilot itself clearly reports when live AI support is unavailable.

## Evaluation

`backend/data/eval_prompts.json` contains a realistic test set for:

- product search
- recommendation prompts
- bundle questions
- availability questions
- payment questions
- shipping and pickup questions
- purchase guidance
- greetings and general help

Run the evaluation script:

```bash
cd /Users/will/Documents/CodexRequests/houston_tcg_site
PYTHONPATH=. python3 backend/scripts/run_eval.py
```

The script reports:

- intent classification accuracy
- retrieval success at top-3
- fallback rate
- per-prompt predicted outputs

## Admin-Friendly Config

The main business-editable files are:

- `backend/data/products.json`
- `backend/data/policies.json`
- `backend/data/eval_prompts.json`

This keeps product inventory, store policies, support rules, and evaluation prompts out of scattered frontend code.

## Resume-Facing Summary

Suggested project bullet:

> Designed and deployed an AI sales and support copilot for Houston TCG, combining intent classification, semantic product retrieval, recommendation logic, and business-policy grounding to improve customer interaction and product discovery for a storefront with 2,000+ visitors.

## Future Improvements

- Replace local token-based semantic retrieval with OpenAI embeddings or a vector database
- Add multi-turn memory and richer session state
- Introduce authenticated admin tooling for inventory updates
- Add product-level pricing updates from a database or CMS
- Track conversion funnel events beyond click-through
- Add automated eval scoring dashboards for intent and retrieval quality

