# 🔍 Paper Scout — AI-Powered Academic Paper Discovery Engine

[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compatible-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6F00)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Paper Scout** is a state-of-the-art, end-to-end academic paper discovery and analysis engine. It fetches real-time literature from **arXiv** and **Semantic Scholar**, intelligently dedupes and merges identical papers locally, and provides high-precision **Hybrid Search** (combining traditional FTS5 lexical matching and semantic vector embedding) ranked with **Reciprocal Rank Fusion (RRF)**.

Designed for seamless deployment, Paper Scout runs out-of-the-box using Docker Compose, requiring zero complex configuration on local machines.

---

## 🚀 Key Features

* **Advanced Hybrid Search (Lexical + Semantic):**
  * **Keyword Search (Lexical):** Powered by SQLite's native **FTS5** full-text search module for fast, precise keyword matching on titles and abstracts.
  * **Anomalous Semantic Search (Vector):** Utilizes Hugging Face's **`all-MiniLM-L6-v2`** embedding model and a local **ChromaDB** vector store to retrieve papers conceptually related to the query—even when exact words do not overlap.
  * **Rank Aggregation (RRF):** Merges lexical and semantic search results using the industry-proven **Reciprocal Rank Fusion (RRF)** algorithm to ensure the most relevant literature bubbles to the top.
* **Intelligent Deduplication & Merging:** Automates duplicate detection across different sources (e.g. arXiv and Semantic Scholar) using title normalization and similarity analysis. It dynamically merges citation counts, abstracts, and metadata, creating a single, rich source of truth in SQLite and ChromaDB.
* **Premium & Responsive User Experience (Aesthetic UX):**
  * Specially designed color palettes: **Ink & Paper (Warm Parchment)** and **Slate Terminal (Sophisticated Dark Mode)** for long research sessions.
  * Ultra-smooth transitions, skeleton loaders, and interactive components powered by **Framer Motion**.
  * Fully compliant with **WCAG AA** accessibility standards (including high text-to-background contrast and full keyboard navigation).

---

## 🛠️ Tech Stack

* **Backend:** Python 3.10, FastAPI, SQLAlchemy (SQLite FTS5), ChromaDB, Hugging Face Sentence Transformers (`all-MiniLM-L6-v2`).
* **Frontend:** React 19, TypeScript, Vite, Framer Motion, Vanilla CSS Modules.
* **Orchestration:** Docker, Docker Compose, Nginx.

---

## 🐳 Quick Start (Primary & Recommended: Docker)

To avoid Python or Node.js version mismatches and environment conflicts, **running Paper Scout via Docker Compose is highly recommended.**

### 1. Pre-requisites
Ensure you have **Docker Desktop** running on your computer.

### 2. Run the Engine
Open a terminal in the project's root directory and run the following commands:

```bash
# 1. Clone the repository
git clone https://github.com/QatzyBURAK/Paper_Scout-.git
cd Paper_Scout-

# 2. Avoid SQLite folder mount issue (highly recommended)
touch backend/paper_scout.db
mkdir -p backend/chroma_data

# 3. Spin up the containers
docker-compose up --build
```

### What happens behind the scenes?
* **Isolation:** Spins up separate, isolated containers for the Python FastAPI backend and React frontend.
* **AI Model Persistence:** The downloaded `all-MiniLM-L6-v2` vector embedding model is cached inside a named Docker volume (`hf_cache`). Subsequent boots are instantaneous.
* **Data Security:** The local SQLite database (`backend/paper_scout.db`) and Chroma vector store (`backend/chroma_data`) are mounted directly to your host disk, ensuring all ingested data is permanently preserved.
* **Nginx Power:** Compiles and serves the React frontend securely behind an Nginx reverse proxy on **`http://localhost:5173`**.

Access the UI instantly at **`http://localhost:5173`**!
Access the Swagger API documentation at **`http://localhost:8001/docs`**.

---

## 💻 Alternative: Local Manual Installation

If you prefer to run the components natively on your system, follow the steps below. Make sure you have **Python 3.10** and **Node.js (v18+)** installed.

### 1. Backend (Server) Setup

1. **Activate the Virtual Environment:**
   * **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD):**
     ```cmd
     python -m venv .venv
     .venv\Scripts\activate.bat
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
2. **Install Dependencies:**
   ```bash
   pip install -e ./backend
   ```
3. **Run the Server (Port 8001):**
   Run the backend on port `8001` (specifically using `127.0.0.1` to bypass standard Windows IPv6 localhost resolution delays):
   ```bash
   cd backend
   ..\.venv\Scripts\python.exe -m uvicorn paper_scout.api.app:create_app --factory --port 8001 --reload
   ```

---

### 2. Frontend (UI) Setup

1. **Navigate to the frontend folder:**
   ```bash
   cd frontend
   ```
2. **Install Packages:**
   ```bash
   npm install
   ```
3. **API Configuration:**
   Create or verify `frontend/.env.local` to point to the backend port `8001`:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8001
   ```
4. **Start the Frontend:**
   ```bash
   npm run dev
   ```
   Open **`http://localhost:5173`** in your browser!

---

## 🎯 Verification & Core Workflows

Once the UI is open, you can test and evaluate the system with these core workflows:

1. **Fetch & Ingest Literature:**
   * Click **"↓ Yeni makale çek"** (Ingest panel) under the search bar.
   * Enter any academic topic (e.g. `transformers` or `reinforcement learning`), select your sources (arXiv, Semantic Scholar), and click **"Çek"**. The engine will fetch and merge records into your local DB.
2. **Try Hybrid Search:**
   * Enter a query (e.g. `attention mechanism`).
   * Switch between **Keyword** (FTS5 matching), **Semantic** (conceptual vector matching), and **Hybrid** (RRF rank-fused) to see how search quality improves.
3. **Browse & Inspect:**
   * Go to the **"Gözat"** (Browse) tab to inspect your entire local database using the paginated grid.
   * Click on any paper card to open a full details modal displaying abstracts, citations, authors, and direct external URLs.

---

## 🧪 Testing Suite & Quality Checks

The backend maintains high code quality and test coverage. With your virtual environment active, navigate to the `backend` folder and run the following checks:

```bash
cd backend

# Run all 139+ unit and integration tests:
pytest

# Code formatting & linter checks:
ruff check .

# Strict static type safety checks:
mypy paper_scout tests --strict
```

---
For a complete guide on deep-dive configurations, platform-specific steps, and comprehensive troubleshooting, refer to [GUIDE.md](file:///C:/Users/Burak/Desktop/new_codes/paper_scout/GUIDE.md) / [GUIDE.tr.md](file:///C:/Users/Burak/Desktop/new_codes/paper_scout/GUIDE.tr.md).

*Paper Scout provides a minimal, modern, highly performant, and robust toolchain bringing state-of-the-art information retrieval to academic literature search.*
