`MultiStrategyTradingEngine-Backend` is a backend for algorithmic trading designed to run **multiple strategies in parallel**, using:

- Real-time or simulated market data  
- Strategy logic written in Python
- News interpretation via IA (Llama3.1 LLM in my case, running locally)
- A clean HTTP API (FastAPI) that a frontend (Angular) can use to monitor performance, trades and positions **per strategy**

The goal is to provide a modular, testable foundation where you can plug in your own private strategies and iterate quickly, without mixing trading logic, infrastructure, and UI concerns.

⚠️ This project is intended for **educational and experimental use only**. It is **not** production-ready and must not be used to trade real money as-is.

---

## Concept & Design

The project is built around two main ideas:

### 1. Strategies are internal, pluggable Python modules

- Each strategy is implemented as a Python class that inherits from a common `Strategy` base.
- Strategies are **registered internally** in a registry, with a key (e.g. `btc_trend`) and a human-friendly display name.
- They are **not** created or modified via API: the external world never sees the code, only the strategy name and its results.
- A frontend can:
  - List available strategy *types* (for a lookup).
  - List strategy *instances*.
  - Inspect performance, trades, and positions **per instance**.

### 2. A strategy engine that runs multiple instances in parallel

- A central **StrategyRunner** manages:
  - A set of strategy instances stored in PostgreSQL.
  - One asynchronous task per running instance using `asyncio`.
- Each strategy instance:
  - Has its own parameters (symbol, timeframe, risk settings, etc.).
  - Has its own trades, positions and PnL in the database.
  - Can be started or stopped independently via API endpoints.

This allows you to run, for example:

- Several variations of the same strategy (different timeframes or parameters),
- Completely different strategies (trend-following, rotation, carry, etc.),
- And compare their performance side by side from the frontend.

## Key Features

- 🔀 **Multi-strategy engine**
  - Run multiple strategy instances in parallel.
  - Each instance has isolated state, trades, and PnL.
  - Start/stop strategies via API.

- 🧠 **Private strategy code**
  - Strategies are Python classes stored in the backend.
  - Not exposed or modifiable from the outside.

- 🌐 **FastAPI backend**
  - HTTP API designed to be consumed from a frontend.
  - Endpoints to:
    - List available strategy types (for dropdowns/lookups).
    - List existing instances.
    - Start/stop instances.
    - Retrieve PnL, trades and positions per instance.

- 🗄️ **PostgreSQL persistence**
  - Strategy instances, trades, positions, and PnL snapshots are stored in the database.

- 📰 **Ollama-ready for news-driven strategies**
  - A simple service is provided as a starting point for calling an Ollama instance.
  - The idea is to convert raw news into structured signals (sentiment, impact, horizon) and feed them into strategies.

## Tech Stack

- **Python** – core language  
- **FastAPI** – high-performance web API framework  
- **Uvicorn** – ASGI server  
- **SQLAlchemy** – ORM for PostgreSQL  
- **PostgreSQL** – persistent storage for strategies, trades and PnL  
- **httpx** – async HTTP client (for calling Ollama or other services)  
- **Ollama** – local/remote LLM for news analysis  

## Getting Started

1. **Set up PostgreSQL** and create a database for the project.
2. **Clone the repository** and create a virtual environment.
3. **Install dependencies** from `requirements.txt`.
4. **Configure environment variables** in a `.env` file:
   - `DATABASE_URL` – connection string for PostgreSQL  
   - `OLLAMA_API_URL` – URL of your Ollama instance (optional)
5. **Run the backend** with Uvicorn:
   ```bash
   uvicorn app.main:app --reload