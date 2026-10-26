# SentimentIQ — Full-Stack Sentiment & Customer Insights Platform

SentimentIQ analyses English customer feedback using an **explainable, rule-based NLP engine** and presents results in an interactive web dashboard. It identifies overall sentiment, aspect-level patterns, emotion signals and potential priority areas. This is **not** a trained transformer or generative AI classifier.

## Features

- Positive, Neutral and Negative classifications with counts and percentages
- Scores from -1 to +1, aspect-level analysis and heuristic emotion detection
- Text entry, sample data, CSV and TXT uploads
- Review explorer with filters and scoring evidence; results CSV export
- FastAPI REST endpoints; standalone Python CLI and optional labelled evaluation

## Technology

| Layer | Technology |
|---|---|
| Dashboard | HTML, CSS, JavaScript, Chart.js (CDN) |
| API | Python, FastAPI, Uvicorn |
| NLP | Python standard library, lexicons and contextual rules |
| Hosting target | GitHub Pages (static frontend) + Render (Python backend) |

## Local setup

Requires Python 3.10+ (Python 3.11+ recommended). In PowerShell from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8001
```

Open **http://127.0.0.1:8001/**; interactive API docs: **http://127.0.0.1:8001/docs**; health check: **http://127.0.0.1:8001/health**.

## API

| Route | Method | Description |
|---|---|---|
| `/` | GET | Serves `dashboard/studio.html` |
| `/health` | GET | Returns `{"status":"ok"}` |
| `/api/analyze` | POST | JSON `{"texts":["Great service", "App freezes"]}` |
| `/api/upload` | POST | Multipart file field `file`, CSV or TXT, max 5 MB |

The response includes `rows`, `aspects`, and `total`. The API limits input text to 10,000 characters per entry and processes at most 10,000 nonempty entries per request. CSV uploads must include a recognised text column; the corrected `app.py` supports `review_text`, `review`, `text`, `comment`, `feedback`, `message`, or `content`.

## Command-line usage

```powershell
python sentiment_tool.py --sample
python sentiment_tool.py reviews.csv --column review_text --out results
```

If `evaluate_reviews.py` has been added to the project, evaluate a labelled CSV with:

```powershell
python evaluate_reviews.py app_performance_reviews_150.csv
```

The reference label column is `sentiment`; predictions must be generated from `review_text`, never from the reference labels. **Do not claim an accuracy result until reproduced against the final deployed engine.**

## Deployment architecture

GitHub Pages serves **static files only**; it cannot execute FastAPI. Deploy the backend as a Render Web Service with build command `pip install -r requirements.txt` and start command `uvicorn app:app --host 0.0.0.0 --port $PORT`. The static frontend must use the **actual HTTPS Render URL** for `/api/analyze` and `/api/upload` requests, not relative paths. Set FastAPI CORS `allow_origins` to the GitHub Pages origin `https://entle1606.github.io` (plain URL string, no Markdown). Configure GitHub Pages to publish an `index.html` entry point. Test upload, charts and export on the **public** URL with your local backend stopped.

**Deployment status:** architecture and steps documented; live end-to-end availability is not verified by this document. Do not present it as complete until tested.

## Project layout

```text
SentimentIQ/
├── app.py                    # FastAPI application
├── sentiment_tool.py         # Shared analysis engine and CLI
├── requirements.txt
├── dashboard/
│   ├── studio.html           # Full-stack dashboard
│   └── sentiment_dashboard.html # Earlier standalone version
├── docs/
│   └── technical_explanation.md
├── evaluate_reviews.py      # Optional, if copied from updated package
└── README.md
```

## Known limitations

- Rule-based sentiment can miss sarcasm, implicit sentiment, unfamiliar slang and domain-specific terms.
- Aspect detection uses keyword matching; sparse topics are unreliable.
- Emotion tags are heuristic, not clinical or psychological assessments.
- Chart.js currently loads from a CDN and needs connectivity.
- No authentication, persistent database, or rate limiting is included in this version.
- The prior evaluation reported **51.3%** on one 150-review dataset, but this must be reproduced for the current code before being reported as a verified result.

## Documentation

See [`docs/technical_explanation.md`](docs/technical_explanation.md) for processing flow, evaluation, architecture, deployment requirements and risks.
