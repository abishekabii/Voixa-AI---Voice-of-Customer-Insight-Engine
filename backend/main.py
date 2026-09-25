from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI(title="Voixa-AI - Voice-of-Customer-Insight-Engine")

# Load the sentiment model once at startup (not per-request)
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

class FeedbackInput(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "Voixa AI backend is running"}

@app.post("/analyze-sentiment")
def analyze_sentiment(feedback: FeedbackInput):
    result = sentiment_analyzer(feedback.text)[0]
    return {
        "text": feedback.text,
        "label": result["label"],
        "confidence": round(result["score"], 4)
    }