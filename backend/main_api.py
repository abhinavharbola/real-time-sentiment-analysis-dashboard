# Core FastAPI backend executing batch sentiment predictions using DistilBERT
# tracking inference latency, and routing results to asynchronous database writes

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List
import time
from datetime import datetime
import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

from backend.database import init_db, insert_batch_predictions, fetch_metrics
from backend.error_handlers import setup_exception_handlers

app = FastAPI(title="Real-Time Sentiment API", version="1.0.0")
setup_exception_handlers(app)

START_TIME = datetime.now()

print("Loading Local Model...")
LOCAL_MODEL_PATH = "./local_model"
tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
base_model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_PATH)

print("Applying In-Memory Quantization...")
quantized_model = torch.quantization.quantize_dynamic(
    base_model, {torch.nn.Linear}, dtype=torch.qint8
)

sentiment_model = pipeline(
    "sentiment-analysis", 
    model=quantized_model,
    tokenizer=tokenizer,
    device=-1
)
print("Model Loaded Successfully.")

class BatchRequest(BaseModel):
    texts: List[str] = Field(..., max_items=100)

class PredictionResponse(BaseModel):
    sentiment: str
    confidence: float

class BatchResponse(BaseModel):
    batch_latency_ms: float
    results: List[PredictionResponse]

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.post("/predict", response_model=BatchResponse)
async def predict_sentiment(request: BatchRequest, background_tasks: BackgroundTasks):
    start_time = time.perf_counter()
    
    predictions = sentiment_model(request.texts)
    
    end_time = time.perf_counter()
    latency_ms = round((end_time - start_time) * 1000, 2)
    
    db_records = []
    response_results = []
    
    for text, pred in zip(request.texts, predictions):
        db_records.append({
            "text": text,
            "sentiment": pred["label"],
            "confidence": round(pred["score"], 4),
            "latency_ms": latency_ms / len(request.texts)
        })
        response_results.append(
            PredictionResponse(sentiment=pred["label"], confidence=pred["score"])
        )

    background_tasks.add_task(insert_batch_predictions, db_records)

    return BatchResponse(batch_latency_ms=latency_ms, results=response_results)

@app.get("/health")
async def health_check():
    uptime = datetime.now() - START_TIME
    return {
        "status": "healthy",
        "uptime_seconds": uptime.total_seconds(),
        "model_loaded": sentiment_model is not None
    }

@app.get("/metrics")
async def system_metrics():
    db_metrics = await fetch_metrics()
    uptime = datetime.now() - START_TIME
    
    return {
        "uptime_hours": round(uptime.total_seconds() / 3600, 2),
        "total_processed": db_metrics["total_processed"],
        "average_inference_latency_ms": db_metrics["average_latency_ms"]
    }