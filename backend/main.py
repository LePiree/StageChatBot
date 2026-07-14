import os
import time
from typing import List

from openai import OpenAI
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_client import (
    Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
)

from system_prompt import get_system_prompt

app = FastAPI(title="Wedding Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],  # "null" pour les fichiers ouverts en local (file://)
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

client = OpenAI(
    base_url=f"{OLLAMA_URL}/v1",
    api_key="ollama",  # obligatoire par le SDK mais non utilisé par Ollama
)

# ---------------------------------------------------------------------------
# Métriques Prometheus
# ---------------------------------------------------------------------------

CHAT_REQUESTS_TOTAL = Counter(
    "chat_requests_total",
    "Nombre total de requêtes reçues sur /api/chat",
    ["status"],  # label : "success" | "error" | "validation_error"
)

CHAT_DURATION_SECONDS = Histogram(
    "chat_duration_seconds",
    "Temps de réponse d'Ollama en secondes",
    buckets=[0.5, 1, 2, 5, 10, 20, 30, 60],
)

CHAT_TOKENS_GENERATED_TOTAL = Counter(
    "chat_tokens_generated_total",
    "Nombre total de tokens générés par Ollama",
)

# ---------------------------------------------------------------------------


MAX_MESSAGES = 20
MAX_MESSAGE_LENGTH = 2000


class Message(BaseModel):
    role: str  # "user" ou "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class ChatResponse(BaseModel):
    response: str


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="La liste de messages ne peut pas être vide.")

    if len(request.messages) > MAX_MESSAGES:
        raise HTTPException(status_code=400, detail=f"Trop de messages (max {MAX_MESSAGES}).")

    for msg in request.messages:
        if msg.role not in ("user", "assistant"):
            raise HTTPException(
                status_code=400,
                detail=f"Rôle invalide : '{msg.role}'. Valeurs acceptées : 'user', 'assistant'."
            )
        if len(msg.content) > MAX_MESSAGE_LENGTH:
            raise HTTPException(status_code=400, detail=f"Message trop long (max {MAX_MESSAGE_LENGTH} caractères).")

    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Le dernier message doit être de rôle 'user'.")

    messages_payload = [{"role": m.role, "content": m.content} for m in request.messages]

    CHAT_REQUESTS_TOTAL.labels(status="received").inc()
    start = time.time()

    try:
        completion = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[{"role": "system", "content": get_system_prompt()}] + messages_payload,
        )
    except Exception:
        CHAT_REQUESTS_TOTAL.labels(status="error").inc()
        raise HTTPException(status_code=500, detail="Erreur interne, veuillez réessayer.")

    duration = time.time() - start
    CHAT_DURATION_SECONDS.observe(duration)
    CHAT_REQUESTS_TOTAL.labels(status="success").inc()

    tokens = getattr(getattr(completion, "usage", None), "completion_tokens", 0) or 0
    CHAT_TOKENS_GENERATED_TOTAL.inc(tokens)

    return ChatResponse(response=completion.choices[0].message.content)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    """Endpoint Prometheus : expose les métriques du modèle en temps réel."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
