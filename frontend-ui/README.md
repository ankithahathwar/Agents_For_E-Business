# 🌟 Agents_For_E-Business: Marco Bespoke Core

An elite, full-stack AI-driven e-commerce platform and tailored customization engine for luxury apparel. The system pairs a high-performance **React (Vite)** frontend storefront with a stateless **FastAPI (RESTful)** intelligent core backend. It uses semantic vector search over a 160-item catalog powered by **PostgreSQL (Neon with pgvector)** and hooks into **Groq (Llama 3.3 70B)** to drive an elite digital concierge assistant ("Marco") operating through a strict, anti-hallucination sales funnel.

---

## 🚀 Key Engineering Features

### 1. Deterministic Category-Locking Engine (Context Armor)
Solves a critical limitation in traditional Retrieval-Augmented Generation (RAG) frameworks: semantic query drift. If a user asks a broad question or requests alternative options (e.g., *"Show me something else"*), a stateless vector search might accidentally pull items from completely different collections due to semantic proximity. 
* This system intercepts user intents, maps active category departments into server-side session RAM cache pools, and enforces a strict `WHERE p.category = %s` filter loop over vector similarity functions (`<=>`). Cross-category pollution is completely eliminated.

### 2. Systematic 3-Step Sales Pipeline
The conversational agent is bounded by a rigid behavioral state pipeline that mirrors an elite real-world luxury personal shopping experience:
* **STEP 1:** Silhouette exploration and base garment selection.
* **STEP 2:** Dynamic suggestion of exactly two compatible premium fabric swatches, translated from raw technical weights/specs into alluring sensory luxury copy.
* **STEP 3:** Custom inner lining shell validation and presentation.

### 3. Smart Link Router & State Interceptor
The system translates traditional LLM text outputs into actionable frontend triggers. When the assistant returns formatted markdown links like `[Apply Lining Name](/lining/slug)`, a customized recursive regex string parser on the React client intercepts the event, strips conversational text wrappers, and automatically updates the active app state configuration.

### 4. Relational Order Persistence Archive
Includes an automated operational transaction pipeline. When a bespoke cut layout is completed and verified, the customer submits the order via an explicit UI transaction drawer. The payload is serialized into relational schema arrays and pushed via a `POST` query route directly into a persistent PostgreSQL cloud ledger.

---

## 🛠️ Technology Stack Architecture

### Frontend Layer
* **Framework:** React.js (Single Page Application via Vite)
* **Styling:** Native Vanilla CSS3 Core
* **State Sync:** Hook-based declarative state models with asynchronous Fetch API pipelines

### Backend Layer
* **Framework:** FastAPI (Python 3.10+) — Built over high-speed Starlette routing and Pydantic data enforcement models
* **Server Runtime:** Uvicorn ASGI Web Server Engine
* **Database Driver:** Psycopg2 Client (with RealDictCursor map serialization)

### Data & Intelligent Agent Foundations
* **Primary Store:** Cloud Neon PostgreSQL (Relational database hosting custom product vector arrays)
* **Embedding Model:** Google Gemini API (`gemini-embedding-2`)
* **Inference Engine:** Groq Cloud Systems (Executing `llama-3.3-70b-versatile` running at ultra-low latency)

---

## 📁 Database Schema Blueprints

The database structure relies on two primary tables operating inside the relational instance:

### 1. `products` Table
Holds the primary catalog definitions and multi-choice matrices.
```sql
CREATE TABLE products (
    base_product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    customization_matrix JSONB NOT NULL
);

## 💻 Local Workspace Installation Guide

### Prerequisites

* Node.js (v18+) & NPM
* Python (v3.10+)
* A running PostgreSQL instance (or cloud Neon connection string) with the `vector` extension enabled.

### 1. Backend Infrastructure Setup

Navigate to your backend subdirectory or root workspace folder:

```bash
# Initialize and activate Python virtual environment
python -m venv venv
./venv/Scripts/activate  # On Windows PowerShell

# Install the verified dependencies manifest
pip install -r requirements.txt

# Create your local configuration cache file
touch .env

```

Populate your `.env` file with your secure cloud infrastructure endpoint keys:

```text
DATABASE_URL="postgresql://user:password@endpoint-pool.neon.tech/neondb?sslmode=require"
GROQ_API_KEY="gsk_your_secret_groq_cloud_token_key"
GEMINI_API_KEY="AIzaSy_your_secret_google_ai_studio_key"

```

Execute the database initialization and embedding sync scripts back-to-back:

```bash
python reseed_massive_catalog.py
python generate_embeddings.py

# Fire up the live local ASGI server reload loop
uvicorn main:app --reload

```

The server will boot up and begin listening for incoming REST API payloads at `http://127.0.0.1:8000`.

### 2. Frontend Interface Setup

Open a separate terminal window and navigate into your React project workspace:

```bash
# Install package node modules
npm install

# Boot up the local Vite development hot-reload server
npm run dev

```

Open your web browser and navigate to `http://localhost:5173` to interact with your live luxury showroom floor!

---

## 🌐 Production Deployment Summary

* **Backend Engine Deployment:** Hosted as a scalable Python Web Service on **Render.com**. Ensure your `DATABASE_URL` and `GROQ_API_KEY` are mirrored into the Render Environment Variables tab, and match your start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
* **Frontend Application Deployment:** Hosted on **Vercel** or **Netlify**. Ensure all raw fetch targets inside `src/App.jsx` are pointed away from `localhost` and targeted to your permanent production Render domain URL (`https://your-service.onrender.com`).

```

```

```

```
