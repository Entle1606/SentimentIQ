
from pathlib import Path
import csv
import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from sentiment_tool import analyse, aspect_stats, priority


app = FastAPI(title="SentimentIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://entle1606.github.io",
        "http://localhost:8001",
        "http://127.0.0.1:8001"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)

ROOT = Path(__file__).parent


class Payload(BaseModel):
    texts: list[str]


def report(texts):
    texts = [
        t.strip()[:10000]
        for t in texts
        if isinstance(t, str) and t.strip()
    ][:10000]

    rows = analyse(texts)
    stats = aspect_stats(rows)

    return {
        "rows": rows,
        "aspects": [
            {
                "name": k,
                **v,
                "priority": priority(v)
            }
            for k, v in sorted(
                stats.items(),
                key=lambda kv: kv[1]["avg"]
            )
        ],
        "total": len(rows)
    }


@app.get("/")
def index():
    return FileResponse(ROOT / "dashboard" / "studio.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(payload: Payload):
    return report(payload.texts)


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith(
        (".csv", ".txt")
    ):
        raise HTTPException(
            status_code=400,
            detail="Upload a CSV or TXT file"
        )

    raw = await file.read(5_000_001)

    if len(raw) > 5_000_000:
        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 5 MB"
        )

    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Please upload UTF-8 text"
        )

    if file.filename.lower().endswith(".txt"):
        return report(content.splitlines())

    try:
        reader = csv.DictReader(io.StringIO(content))

        if not reader.fieldnames:
            raise ValueError("No CSV headers found")

        preferred = [
            "review_text",
            "review",
            "text",
            "comment",
            "feedback",
            "message",
            "content"
        ]

        columns = {
            name.strip().lower(): name
            for name in reader.fieldnames
        }

        key = next(
            (
                columns[name]
                for name in preferred
                if name in columns
            ),
            None
        )

        if key is None:
            raise ValueError(
                "No recognised feedback column found. "
                "Expected review_text, review, text, "
                "comment, feedback, message or content."
            )

        texts = [
            row.get(key, "")
            for row in reader
        ]

        return report(texts)

    except (csv.Error, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )
