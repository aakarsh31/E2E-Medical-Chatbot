# 🏥 End-to-End Medical Chatbot

A production-ready RAG (Retrieval-Augmented Generation) based medical chatbot that ingests medical PDFs, stores their embeddings in Pinecone, and answers medical questions through a Flask web app — deployed on AWS EC2 via Docker with full CI/CD through GitHub Actions.

---

## 🎥 Demo

[![Medical Chatbot Demo](https://img.youtube.com/vi/HS7oqF2Tkr8/0.jpg)](https://www.youtube.com/shorts/vKuXeDohc_0)

---

## 📌 Table of Contents

- [Demo](#demo)
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Local Setup & Running](#local-setup--running)
- [Environment Variables](#environment-variables)
- [AWS Deployment](#aws-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [API Routes](#api-routes)
- [Things to Know / Gotchas](#things-to-know--gotchas)

---

## Project Overview

This chatbot lets users ask medical questions and get answers grounded in real medical PDFs. It uses:
- **LangChain** to orchestrate the RAG pipeline
- **OpenAI GPT-4o** as the LLM
- **Pinecone** as the vector database to store and retrieve PDF embeddings
- **Flask** as the web framework
- **Docker + AWS EC2 + GitHub Actions** for deployment and CI/CD

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| LLM | GPT-4o (OpenAI) |
| RAG Framework | LangChain |
| Vector DB | Pinecone |
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
     │  Chunk + Embed (download_embeddings)
     ▼
Pinecone Index: "medical-chatbot"
     │
     ▼
[app.py - Flask]
     │
     ├── User sends message via chat.html (POST /get)
     │
     ▼
LangChain RAG Chain
     │
     ├── Retriever: Pinecone similarity search (top k=3 chunks)
     │
     ├── Prompt: system_prompt (from src/prompt.py) + user input
     │
     └── LLM: GPT-4o → generates answer
     │
     ▼
JSON response → rendered in chat.html
```

---

## Project Structure

```
├── app.py                  # Main Flask app, RAG chain setup, routes
├── store_index.py          # One-time script: embed PDFs and push to Pinecone
├── Dockerfile              # Docker image definition
├── requirements.txt        # Python dependencies
├── .env                    # Local env vars (never commit this!)
├── .github/
│   └── workflows/
│       └── cicd.yaml       # GitHub Actions CI/CD pipeline
├── src/
│   ├── helper.py           # download_embeddings() and other utilities
│   └── prompt.py           # system_prompt definition
└── templates/
    └── chat.html           # Frontend chat UI
```

---

## How It Works

### Step 1 — Indexing (One-time setup)
`store_index.py` reads your medical PDFs, chunks them, generates embeddings using `download_embeddings()`, and pushes them to Pinecone under the index name `medical-chatbot`.

### Step 2 — Serving
`app.py` starts the Flask server which:
1. Loads the existing Pinecone index
2. Sets up a retriever (similarity search, k=3)
3. Builds a LangChain RAG chain: retriever → stuff documents chain → GPT-4o
4. Exposes two routes (`/` and `/get`)

### Step 3 — Query Flow
1. User types a question in `chat.html`
2. Form POSTs to `/get`
3. RAG chain retrieves top 3 relevant chunks from Pinecone
4. GPT-4o generates an answer grounded in those chunks
5. Answer returned as JSON `{"answer": "..."}` and displayed in UI

---

## Local Setup & Running

### 1. Clone the repo
```bash
git clone https://github.com/entbappy/End-to-End-Medical-Chatbot
cd End-to-End-Medical-Chatbot
```

### 2. Create and activate conda environment
```bash
conda create -n medibot python=3.10 -y
conda activate medibot
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```ini
PINECONE_API_KEY = "your-pinecone-api-key"
OPENAI_API_KEY = "your-openai-api-key"
```

### 5. Index your medical PDFs (one-time)
```bash
python store_index.py
```
This pushes embeddings to your Pinecone index. Only needs to be re-run if your PDFs change.

### 6. Run the app
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

For local development these live in `.env`. In production (EC2 via Docker) they are injected as environment variables through GitHub Actions secrets.

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
Create a private ECR repo to store the Docker image.
Save the URI, it looks like:
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
Choose Linux, then run the provided commands on your EC2 instance. This allows GitHub Actions to SSH into EC2 and deploy.

#### 6. Add GitHub Secrets
In your GitHub repo go to `Settings → Secrets and variables → Actions` and add:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_DEFAULT_REGION` | e.g. `us-east-1` |
| `ECR_REPO` | ECR repo name (not full URI, just the name) |
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

> ⚠️ **Known issue:** The `docker run` command doesn't stop/remove the previously running container first. On repeated deployments this will cause a port conflict. To fix, add a cleanup step before `docker run`:
> ```bash
> docker stop $(docker ps -q) || true
> docker rm $(docker ps -aq) || true
> ```

---

## API Routes

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Renders the chat UI (`chat.html`) |
| `GET/POST` | `/get` | Accepts `msg` form field, returns `{"answer": "..."}` |

---

## Things to Know / Gotchas

- **`store_index.py` must be run before `app.py`** — the app connects to an *existing* Pinecone index. If the index doesn't exist yet, it will error on startup.
- **Pinecone index name is hardcoded** as `"medical-chatbot"` in `app.py`. If you rename it in Pinecone, update it there too.
- **`debug=True`** is set in `app.py` — fine locally but should be `False` in production for security.
- **k=3** — only the top 3 most relevant chunks are passed to GPT-4o. If answers feel incomplete, consider increasing this.
- **No error handling** on the `/get` route — if the RAG chain or Pinecone connection fails, Flask will return a raw 500. Worth adding a try/except for production robustness.
- **The `.env` file should never be committed** — it's your local secrets file. Make sure it's in `.gitignore`.
