# 🏥 End-to-End Medical Chatbot

A production-ready RAG (Retrieval-Augmented Generation) medical chatbot that ingests medical PDFs, stores embeddings in Pinecone, and answers medical questions through a Flask web app — with conversation memory, hybrid search, cross-encoder reranking, and RAGAS-validated quality — deployed on AWS EC2 via Docker with full CI/CD through GitHub Actions.

---

## 🎥 Demo

[![Medical Chatbot Demo](https://img.youtube.com/vi/HS7oqF2Tkr8/0.jpg)](https://www.youtube.com/shorts/vKuXeDohc_0)

---

## 📌 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Project Structure](#project-structure)
- [RAGAS Evaluation](#ragas-evaluation)
- [How It Works](#how-it-works)
- [Local Setup & Running](#local-setup--running)
- [Environment Variables](#environment-variables)
- [AWS Deployment](#aws-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [API Routes](#api-routes)
- [Things to Know / Gotchas](#things-to-know--gotchas)

---

## Project Overview

This chatbot lets users ask medical questions and get answers grounded exclusively in real medical PDFs — not GPT-4o's training data. The pipeline has been progressively upgraded from a basic stateless RAG baseline into a production-grade conversational system with validated retrieval quality.

**Three major upgrades shipped over the baseline:**

1. **Conversation Memory** — per-session history with UUID-based session management and query contextualization
2. **Hybrid Search + Reranking** — BM25 keyword search combined with dense semantic retrieval, re-ranked by a cross-encoder, built with a fully explicit LCEL pipeline
3. **RAGAS Evaluation** — quantitative proof of improvement across 13 handcrafted test questions, covering direct factual, inference, multi-hop, and conversational query types

---

## Features

- **Grounded answers only** — GPT-4o is instructed to answer exclusively from retrieved chunks, never from training data
- **Conversation memory** — follow-up questions like "what are its symptoms?" or "can it be taken with insulin?" resolve correctly across multiple turns
- **Hybrid retrieval** — BM25 catches exact medical terms and drug names that dense semantic search misses; dense retrieval handles semantic meaning; ensemble combines both
- **Cross-encoder reranking** — `ms-marco-MiniLM-L-6-v2` reads the question and each candidate chunk *together* to score true relevance, far more accurate than embedding similarity alone
- **Explicit LCEL pipeline** — every variable flowing through the chain is visible and debuggable; no black-box convenience functions
- **Production deployment** — Dockerized Flask app on AWS EC2, fully automated CI/CD via GitHub Actions and AWS ECR
- **Dark minimal UI** — DM Serif Display + Sora fonts, typing indicator, timestamps, loading state, error handling

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| LLM | GPT-4o (OpenAI) |
| RAG Framework | LangChain (LCEL) |
| Vector DB | Pinecone (serverless, AWS us-east-1) |
| Embeddings | `all-MiniLM-L6-v2` (384 dims, HuggingFace) |
| Keyword Search | BM25 (`rank_bm25`) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Eval Framework | RAGAS |
| Web Framework | Flask |
| Containerisation | Docker |
| Cloud | AWS EC2 + ECR |
| CI/CD | GitHub Actions |

---

## Project Architecture

```
Medical PDFs
     │
     ▼
[store_index.py]
     │  load → filter → chunk (size=1000, overlap=200) → embed (MiniLM-384)
     ▼
Pinecone Index: "ragmedibot"
     │
     ▼
[app.py — Flask]
     │
     ├── User sends message + session_id via chat.html (POST /get)
     │
     ▼
Query Contextualization
     │  contextualize_q_prompt + chat_history → GPT-4o → standalone question
     │
     ▼
Hybrid Retrieval (EnsembleRetriever)
     ├── Dense: Pinecone similarity search (k=5)
     └── BM25: keyword search over chunked docs (k=5)
          │  50/50 weighted ensemble
          ▼
Cross-Encoder Reranking
     │  ms-marco-MiniLM-L-6-v2 reads question + chunk together → top 5
     ▼
GPT-4o — answers only from reranked context
     │
     ▼
RunnableWithMessageHistory — saves turn to per-session store
     │
     ▼
JSON response → rendered in chat.html
```

---

## Project Structure

```
├── app.py                      # Flask app — full LCEL RAG chain, routes
├── store_index.py              # One-time script: embed PDFs and push to Pinecone
├── Dockerfile                  # Docker image definition
├── requirements.txt            # Python dependencies
├── .env                        # Local env vars (never commit — git rm --cached .env)
├── .github/
│   └── workflows/
│       └── cicd.yaml           # GitHub Actions CI/CD pipeline
├── src/
│   ├── helper.py               # load_pdf_files(), filterer(), chunker(), download_embeddings()
│   └── prompt.py               # contextualize_q_system_prompt, system_prompt
├── eval/
│   ├── test_questions.py       # 13 handcrafted eval questions (4 types)
│   ├── baseline_eval.py        # Naive dense-only pipeline eval → baseline_scores.json
│   ├── upgraded_eval.py        # Full production pipeline eval → upgraded_scores.json
│   └── results/
│       ├── baseline_scores.json
│       └── upgraded_scores.json
└── templates/
    └── chat.html               # Frontend chat UI
```

---

## RAGAS Evaluation

To validate that the hybrid search + reranking upgrade actually improved retrieval and answer quality, a full RAGAS eval was run comparing the naive baseline against the production pipeline.

### What was evaluated

**13 handcrafted questions across 4 types:**
- Direct factual (e.g. "What is metformin used for?")
- Inference/reasoning (e.g. "Why might a doctor choose one treatment over another?")
- Multi-hop (requires synthesizing across multiple chunks)
- Conversational pronoun chains (e.g. "What is metformin?" → "What are its side effects?" → "Can it be taken with insulin?")

**Baseline pipeline:** Dense-only Pinecone retriever (k=5), no BM25, no reranker, no conversation history.

**Upgraded pipeline:** EnsembleRetriever (BM25 + dense), cross-encoder reranker, `RunnableWithMessageHistory` for conversational questions.

**RAGAS metrics** (all evaluated via `LangchainLLMWrapper(gpt-4o)`):
- **Context Recall** — did retrieval surface the right information?
- **Faithfulness** — is the answer grounded in retrieved docs, or hallucinated?
- **Context Precision** — are the retrieved chunks actually relevant?
- **Answer Relevancy** — does the answer directly address the question?

### Results

| Metric | Baseline | Upgraded | Δ |
|--------|----------|----------|---|
| Context Recall | 0.50 | 0.65 | **+30%** ✅ |
| Faithfulness | 0.852 | 0.984 | **+15.5%** ✅ |
| Context Precision | 0.423 | 0.377 | -10.9% |
| Answer Relevancy | 0.730 | 0.662 | -9.3% |

### Why did precision and answer relevancy dip?

This is a known and expected tradeoff, not a regression.

The baseline uses dense-only retrieval with k=5 — returning 5 chunks that are all semantically close to the query. That produces a tight, focused candidate set, which scores well on precision.

The upgraded pipeline runs BM25 alongside dense retrieval and pools both result sets before reranking. BM25 surfaces chunks based on keyword overlap rather than semantic similarity — it catches exact drug names and clinical terminology that dense retrieval misses, but some of those chunks are tangentially related rather than directly relevant. The reranker then scores this larger, more diverse candidate set and picks the top 5, but RAGAS Context Precision penalises any chunk that wasn't strictly necessary to answer the question. More diverse retrieval = more chunks flagged as unnecessary = lower precision score. Answer Relevancy drops for a similar reason: when the model has a noisier context window, answers can become slightly more hedged or verbose, which RAGAS penalises.

**The important point:** Faithfulness jumped from 0.852 → 0.984. For a medical chatbot, faithfulness is the metric that matters most — it directly measures whether GPT-4o is grounding its answers in retrieved documents rather than hallucinating. A small precision dip is an acceptable and deliberate tradeoff when the model is almost never going off-script. This is the standard recall-precision tradeoff in information retrieval, and the architectural choice here — prioritising faithfulness over precision — is the right one for a medical domain.

---

## How It Works

### Step 1 — Indexing (one-time setup)
`store_index.py` reads medical PDFs from the `data/` directory, filters and chunks them (chunk size 1000, overlap 200), generates embeddings using `all-MiniLM-L6-v2` (384 dims), and pushes to Pinecone under index name `ragmedibot`.

### Step 2 — Startup
On `app.py` startup:
1. Loads existing Pinecone index as a dense retriever
2. Loads chunked docs into a BM25 retriever (in-memory)
3. Combines both into an `EnsembleRetriever` (50/50 weights)
4. Initialises the cross-encoder reranker
5. Builds the full LCEL chain with query contextualization and conversation history

### Step 3 — Query Flow
1. User types a question in `chat.html`
2. `SESSION_ID = crypto.randomUUID()` is generated on page load; every request sends `msg` + `session_id`
3. `contextualize_q_prompt` rephrases ambiguous follow-ups ("what are its symptoms?") into standalone questions using chat history
4. Standalone question hits the ensemble retriever (BM25 + dense, k=5 each)
5. Cross-encoder reranks the pooled results, returns top 5
6. GPT-4o generates an answer grounded exclusively in those 5 chunks
7. Turn is saved to the in-memory `store` dict keyed by session_id
8. Answer returned as `{"answer": "..."}` and rendered in UI

---

## Local Setup & Running

### 1. Clone the repo
```bash
git clone https://github.com/aakarsh31/E2E-Medical-Chatbot
cd E2E-Medical-Chatbot
```

### 2. Create and activate virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```ini
PINECONE_API_KEY=your-pinecone-api-key
OPENAI_API_KEY=your-openai-api-key
```

### 5. Add your medical PDFs
Place your PDFs in the `data/` directory.

### 6. Index your PDFs (one-time)
```bash
python store_index.py
```
This chunks, embeds, and pushes to Pinecone. Only needs to be re-run if your PDFs change.

### 7. Run the app
```bash
python app.py
```
Open your browser at `http://localhost:8080`

---

## Environment Variables

| Variable | Description |
|---|---|
| `PINECONE_API_KEY` | Your Pinecone API key |
| `OPENAI_API_KEY` | Your OpenAI API key |

For local development these live in `.env` (never commit — `.env` is in `.gitignore` and has been removed from git tracking via `git rm --cached .env`). In production they are injected as environment variables through GitHub Actions secrets.

---

## AWS Deployment

The app runs inside a Docker container on an EC2 instance, with the image stored in AWS ECR.

### One-time AWS Setup

#### 1. Create IAM User
Create an IAM user with these policies:
- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonEC2FullAccess`

Save the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

#### 2. Create ECR Repository
Create a private ECR repo to store the Docker image. Save the URI:
```
315865595366.dkr.ecr.us-east-1.amazonaws.com/medicalbot
```

#### 3. Launch EC2 Instance (Ubuntu)
- OS: Ubuntu
- Open port `8080` in the security group inbound rules

#### 4. Install Docker on EC2
SSH into your EC2 instance and run:
```bash
sudo apt-get update -y
sudo apt-get upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
```

#### 5. Configure EC2 as a GitHub Self-Hosted Runner
In your GitHub repo:
```
Settings → Actions → Runners → New self-hosted runner
```
Choose Linux, then run the provided commands on your EC2 instance.

#### 6. Add GitHub Secrets
Go to `Settings → Secrets and variables → Actions`:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_DEFAULT_REGION` | e.g. `us-east-1` |
| `ECR_REPO` | ECR repo name |
| `PINECONE_API_KEY` | Your Pinecone API key |
| `OPENAI_API_KEY` | Your OpenAI API key |

---

## CI/CD Pipeline

File: `.github/workflows/cicd.yaml`

Triggered on every push to `main`.

### Job 1: Continuous-Integration (GitHub-hosted runner)
1. Checkout code
2. Configure AWS credentials
3. Login to Amazon ECR
4. Build Docker image
5. Tag as `latest` and push to ECR

### Job 2: Continuous-Deployment (Self-hosted EC2 runner)
Runs after CI succeeds.
1. Checkout code
2. Configure AWS credentials
3. Login to ECR
4. Pull the new image and run it as a container on port `8080`, injecting all env vars

> ⚠️ **Known issue:** The `docker run` command doesn't stop/remove the previously running container first. On repeated deployments this will cause a port conflict. Fix by adding a cleanup step before `docker run`:
> ```bash
> docker stop $(docker ps -q) || true
> docker rm $(docker ps -aq) || true
> ```

---

## API Routes

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Renders the chat UI (`chat.html`) |
| `GET/POST` | `/get` | Accepts `msg` + `session_id` form fields, returns `{"answer": "..."}` |

---

## Things to Know / Gotchas

- **`store_index.py` must be run before `app.py`** — the app connects to an *existing* Pinecone index. If the index doesn't exist, startup will error.
- **Pinecone index name** is hardcoded as `"ragmedibot"` in `app.py` and `store_index.py`. If you rename it in Pinecone, update both files.
- **BM25 is loaded at startup** from `chunked_data` in memory. This means `load_pdf_files()`, `filterer()`, and `chunker()` all run at app startup — not just at indexing time. This is intentional; BM25 needs the raw chunks, not Pinecone.
- **Conversation history lives in memory** in the `store = {}` dict keyed by UUID session_id. This works for development but won't survive restarts and won't scale across multiple instances. Production would use Redis.
- **`debug=True`** is set in `app.py` — fine locally, should be `False` in production.
- **Deprecated LangChain import warnings** in `helper.py` are harmless but should be migrated to `langchain-community` imports eventually.
- **Embeddings model** is `all-MiniLM-L6-v2` (384 dims). If you switch to a different embeddings model, you must rebuild the Pinecone index with matching dimensions.
