# DiffWatch

Get an email the moment a webpage changes.

DiffWatch lets you watch a specific piece of a page and notifies you by email when its content changes. It's built as a serverless, event-driven pipeline on AWS, designed to run at near-zero cost for low-traffic use.

## Why

Most "page change" trackers either watch the entire page (triggering false positives on ads, timestamps, A/B tests) or require a full headless browser per check (expensive, slow). DiffWatch checks a normalized, selector-scoped snapshot via plain HTTP requests, and is explicit about the cases where that approach can't work (JS challenges, bot walls) rather than pretending to handle everything.

## How it works

```
EventBridge Scheduler (every 1 min)
        │
        ▼
  Dispatcher Lambda ── queries Postgres for monitors due for a check
        │
        ▼
     SQS queue ── one message per monitor
        │
        ▼
   Checker Lambda ── fetches the page, applies the selector, 
        │            checks if there's any change
        │           
        ▼
     SQS queue (only if content changed)
        │
        ▼
   Notifier Lambda ── sends the email via SES
```

The dispatcher runs on a fixed low-frequency schedule but never does wasted work: it only queries the database for monitors that are actually due, using a partial index on `next_check_at`. Checker Lambdas only run when there's a real check to perform, triggered by SQS, not by a timer.

## Status

🚧 Early development, not yet deployed. Building this in public as a learning project.

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Compute | AWS Lambda (Python) | Pay-per-use, fits the near-zero-cost goal |
| Scheduling | EventBridge Scheduler + SQS | Decoupled dispatch, built-in retries and DLQ |
| Database | Postgres (Neon) | Relational data model, serverless almost free |
| Email | Amazon SES | Cheap (0.16$ / 1k emails), integrates natively with the Lambda/SQS pipeline |
| Infrastructure | Terraform | Infrastructure as code, portable across environments |
| Local AWS emulation | floci | Free local AWS emulator for development and testing |
| HTTP / parsing | httpx, selectolax | Fast fetch and selector matching without a headless browser |

## Local development

Requirements: Docker, [uv](https://docs.astral.sh/uv/), Terraform.

```bash
# 1. Install dependencies
uv sync
```

## Repository structure

```
src/DiffWatch/
├── core/       # pure logic: fetching, parsing, hashing, classification — no AWS dependency
├── db/         # models and queries
└── lambdas/    # thin Lambda handlers, one folder per function
infra/          # Terraform modules and root configuration
tests/          # unit tests (core/) and integration tests (moto/floci)
```