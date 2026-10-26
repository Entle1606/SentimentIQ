# SentimentIQ — Technical Explanation (Full-Stack)

## 1. Scope and design

SentimentIQ is a Python rule-based sentiment and aspect-analysis engine exposed through FastAPI and rendered in an HTML/CSS/JavaScript dashboard. The frontend and backend are separate deployment units for GitHub Pages and Render. The earlier standalone `dashboard/sentiment_dashboard.html` is retained as a legacy interface; the current full-stack interface is `dashboard/studio.html`.

## 2. Data flow

1. User pastes reviews or uploads CSV/TXT in the dashboard.
2. JavaScript sends JSON to `POST /api/analyze` or multipart file data to `POST /api/upload`.
3. FastAPI validates size/format and extracts review strings.
4. `report()` calls `analyse(texts)` and `aspect_stats(rows)` from `sentiment_tool.py`.
5. API returns JSON containing per-review rows, aspect aggregates and total.
6. Dashboard renders sentiment percentages (including Neutral), charts, searchable rows, evidence and action priorities.

## 3. Processing details

The engine normalises/tokenises feedback, scores lexicon matches and applies negation, intensifier and context heuristics. It combines textual signals into a bounded sentiment score from -1 to +1 and assigns Positive, Neutral or Negative. Aspect analysis splits or associates feedback with keyword-defined topics and aggregates aspect sentiment. Emotion signals are keyword/stem heuristics; they do not represent verified psychological states. `priority()` maps aggregate aspect statistics to a rule-based priority.

**Interpretability:** rules can be inspected and tested. **Tradeoff:** rules are brittle on sarcasm, novel vocabulary, implicit meaning and multi-aspect sentences.

## 4. API contracts

| Endpoint            | Request                  | Response                                        |
| ------------------- | ------------------------ | ----------------------------------------------- |
| `GET /`             | none                     | `dashboard/studio.html`                         |
| `GET /health`       | none                     | `{"status":"ok"}`                               |
| `POST /api/analyze` | JSON `{"texts":["..."]}` | `{"rows": [...], "aspects": [...], "total": N}` |
| `POST /api/upload`  | multipart `file` CSV/TXT | Same analysis report                            |

Upload size is limited to 5 MB. CSV requires a header and a text column; accepted names in the **corrected** backend are `review_text`, `review`, `text`, `comment`, `feedback`, `message`, `content`. Unknown columns should produce HTTP 400 instead of falling back to an ID field. This is important for the 150-review app-performance dataset.

## 5. Dashboard and UI

`dashboard/studio.html` uses Chart.js for sentiment and emotion visualizations and a five-KPI overview: total reviews, Positive %, Negative %, Neutral %, and average score. Percentages are calculated from predicted labels and the number of analysed reviews, not from uploaded reference labels. Empty datasets yield 0%. Review explorer supports text search, sentiment and emotion filters, evidence inspection and CSV export. Chart.js is currently CDN-hosted.

## 6. Evaluation methodology

Use `app_performance_reviews_150.csv` as a **labelled evaluation dataset**: `review_text` is the input, `sentiment` is the reference label. Run `evaluate_reviews.py` if installed. Report accuracy, class-wise precision, recall and F1, a confusion matrix, and examples of false positives/negatives. The previously reported 51.3% accuracy is **provisional until reproduced on the final code**. Avoid optimizing exclusively for this one dataset; use a separate held-out set for claims of generalization.

## 7. Deployment and CORS

- **Render:** Python Web Service, root at repository root, install from `requirements.txt`, run `uvicorn app:app --host 0.0.0.0 --port $PORT`.
- **GitHub Pages:** static HTML/CSS/JS only. Publish an `index.html` (or configured static build) as the landing page.
- **Frontend configuration:** use absolute Render HTTPS API URLs in JavaScript requests. Relative `/api/...` paths target the GitHub Pages host and will fail.
- **CORS:** allow the literal origin `https://entle1606.github.io`; CORS does not replace authentication or rate limiting.
- **Verification:** test `GET /health`, `POST /api/analyze`, `POST /api/upload` and public dashboard interactions with local Uvicorn stopped.

## 8. Security and reliability gaps

Current design does not provide user authentication, persistent storage, rate limiting or comprehensive automated tests. Input limits help control resource use but do not replace production controls. CSV contents should be treated as untrusted user data; avoid HTML injection in client rendering. Avoid uploading sensitive customer data to a public demonstration service.

## 9. Improvement plan

1. Unit tests for negation, intensifiers, neutral language and CSV column detection.
2. Confusion-matrix-driven vocabulary and rule improvements.
3. Held-out evaluation and comparison with a pretrained NLP baseline.
4. Stronger aspect matching and trend analysis.
5. Production API controls, persistent storage and continuous deployment checks.
