# AI Log Triage Agent

## Overview

This project explores how **LLM-based agents** can assist developers and operations teams by:

- Ingesting application logs and issue descriptions
- Clustering related issues by probable root cause
- Generating human-readable summaries
- Suggesting priority and potential owning teams

The goal is to build both:

- A **CLI tool** for quick experiments and demos
- A **FastAPI service** for integration and further research

This project will also serve as a foundation for potential **research work** on LLM-based triage and developer productivity.

---

## Project Status

- [ ] v0 — Basic CLI that summarizes a single log file via an LLM
- [ ] v0.1 — Basic FastAPI endpoint wrapping the same logic
- [ ] v1.0 — Clustering + prioritization + simple heuristics
- [ ] v1.1 — Initial experiment design + metrics
- [ ] v2.0 — Writeup suitable as a short paper / technical report

---

## Getting Started

### 1. Create a virtual environment & install dependencies

```bash
cd projects/ai-log-triage-agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

