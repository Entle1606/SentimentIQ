from pathlib import Path
import csv, io, json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sentiment_tool import analyse, aspect_stats, priority

app = FastAPI(title='SentimentIQ API', version='1.0.0')
ROOT = Path(__file__).parent
class Payload(BaseModel):
    texts: list[str]

def report(texts):
    texts=[t.strip()[:10000] for t in texts if isinstance(t,str) and t.strip()][:10000]
    rows=analyse(texts)
    stats=aspect_stats(rows)
    return {'rows':rows,'aspects':[{'name':k,**v,'priority':priority(v)} for k,v in sorted(stats.items(),key=lambda kv:kv[1]['avg'])], 'total':len(rows)}

@app.get('/')
def index(): return FileResponse(ROOT/'dashboard'/'studio.html')
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/api/analyze')
def analyze(payload:Payload): return report(payload.texts)
@app.post('/api/upload')
async def upload(file:UploadFile=File(...)):
    if not file.filename.lower().endswith(('.csv','.txt')): raise HTTPException(400,'Upload a CSV or TXT file')
    raw=await file.read(5_000_001)
    if len(raw)>5_000_000: raise HTTPException(413,'Maximum file size is 5 MB')
    try: content=raw.decode('utf-8-sig')
    except UnicodeDecodeError: raise HTTPException(400,'Please upload UTF-8 text')
    if file.filename.lower().endswith('.txt'): return report(content.splitlines())
    try:
        reader=csv.DictReader(io.StringIO(content))
        if not reader.fieldnames: raise ValueError('No CSV headers')
        preferred=['review','text','comment','feedback','message','content']
        key=next((k for name in preferred for k in reader.fieldnames if k.lower().strip()==name),None)
        if key is None: key=reader.fieldnames[0]
        return report([r.get(key,'') for r in reader])
    except (csv.Error,ValueError) as exc: raise HTTPException(400,str(exc))
