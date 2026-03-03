 

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import os

# FIX: was importing from 'feature_extractor' but file is 'feature_extraction'
from app.log_parser import parse_log
from app.feature_extractor import extract_features
from app.rule_engine import rule_based_detection
from app.ml_model import predict_anomaly, load_model, train_model

app = FastAPI(title="AI Log Analyzer")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "logs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

_ALLOWED_EXTENSIONS = {".log", ".txt", ".out"}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_class=HTMLResponse)
async def analyze_log(request: Request, file: UploadFile = File(...)):
    # Validate file extension
    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {_ALLOWED_EXTENSIONS}",
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Could not save file: {exc}")

    try:
        logs = parse_log(file_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not logs:
        raise HTTPException(
            status_code=400,
            detail="No parseable log entries found in the uploaded file.",
        )

    features = extract_features(logs)
    rule_incidents = rule_based_detection(features)

    # Train a fresh model if one doesn't exist yet
    if load_model() is None and len(logs) >= 2:
        try:
            train_model(logs)
        except Exception:
            pass  # Model training is best-effort; prediction will return "not trained"

    ml_result = predict_anomaly(logs)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "features": features,
            "rule_alerts": rule_incidents,
            "ml_result": ml_result,
            "filename": file.filename,
            "total_logs": features["total_logs"],
        },
    )