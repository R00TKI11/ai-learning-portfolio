# AI Learning Portfolio – Carlos Sepulveda

This repository is my workspace for transitioning from senior software engineering and technical product ownership into **applied AI/ML and AI research**.

It contains:

- 📝 **Journals** – daily and weekly logs of learning and project progress  
- 🧭 **Planning** – roadmaps, 7-day plans, and early research topic ideas  
- 🧪 **Projects** – small but complete AI/ML projects focused on:
  - LLM agents & copilots for developers/ops  
  - Retrieval-Augmented Generation (RAG)  
  - Predictive maintenance and operational ML  
  - Evaluation of AI coding tools  

The goal is to build a **public portfolio** that is useful to:

- Recruiters & hiring managers evaluating my AI/ML capabilities  
- Graduate admissions committees that are reviewing my preparation and research direction  
- Other developers who want practical AI starting points

---

## Repository Layout

- `journal/` – private-facing logs (still versioned here)  
- `planning/` – roadmaps, 7-day plans, research topic sketches  
- `projects/` – each AI-related project in its own folder

---

## Current Project Themes

### 🤖 AI Log Triage Agent (`projects/ai-log-triage-agent`)

LLM-powered assistant that:

- Ingests logs and issue descriptions
- Clusters related issues
- Summarizes patterns and likely root causes
- Suggests priority and possible owning team

Exposed via both:

- A **CLI tool** for quick terminal usage  
- A **FastAPI service** for integration and experimentation

---

### 📚 RAG “Docs-to-Copilot” Starter (`projects/rag-docs-starter`)

A minimal framework for turning a folder of documents into a simple AI copilot:

- Ingestion and chunking
- Embedding and vector indexing
- Retrieval and answer generation
- CLI + FastAPI API surface

---

### 🔧 Predictive Maintenance / Ticket ML (`projects/predictive-maintenance-ml`)

Exploring lightweight ML models on maintenance/logistics-style data:

- Synthetic or anonymized datasets
- Classification/regression for ticket priority or parts usage
- Comparison of classic ML vs. LLM-based approaches

---

### 🧪 Coding Assistant Benchmark (`projects/coding-assistant-benchmark`)

Task-based benchmark for evaluating AI coding tools (ChatGPT, Claude, Copilot, etc.) on realistic maintenance and refactoring tasks.

---

## How I Use This Repo

- Write **daily logs** in `journal/` to capture:
  - What I planned vs. what I did  
  - Blockers  
  - Questions for AI tools/mentors  
- Maintain a **7-day rolling plan** in `planning/7-day-plan.md`  
- Track longer-term goals and experiment ideas in `planning/roadmap.md` and `planning/research-topics.md`  
- Use this as the main link for:
  - Recruiters
  - Potential collaborators
  - Graduate admissions reviewers

---
