import os
import time
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, Depends, Request, Security
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from openai import OpenAI
from pydantic import BaseModel
from prometheus_client import (
    Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
)
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from system_prompt import get_system_prompt

load_dotenv()  # charge .env à la racine du projet en dev local

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
# 10 requêtes/minute par IP — seuil calibré pour une conversation chatbot
# normale (≈ 1 message toutes les 6 s) tout en bloquant un spam évident.
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Wedding Chatbot API")
app.state.limiter = limiter


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Trop de requêtes. Veuillez patienter avant de réessayer."},
    )


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],  # "null" pour les fichiers ouverts en local (file://)
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Authentification Bearer
# ---------------------------------------------------------------------------
_bearer_scheme = HTTPBearer(auto_error=False)


def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer_scheme),
) -> None:
    expected = os.environ.get("API_TOKEN", "")
    if not expected or credentials is None or credentials.credentials != expected:
        raise HTTPException(status_code=401, detail="Authentification requise.")


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

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

# Correspondance BCP-47 → nom de langue pour le hint envoyé au modèle
_LANG_NAMES: dict[str, str] = {
    "en": "English", "fr": "French", "es": "Spanish", "pt": "Portuguese",
    "de": "German", "it": "Italian", "nl": "Dutch", "pl": "Polish",
    "ru": "Russian", "ja": "Japanese", "zh": "Chinese", "ar": "Arabic",
    "tr": "Turkish", "sv": "Swedish", "da": "Danish", "fi": "Finnish",
}


def _build_lang_hint(locale: str) -> dict:
    base = locale.split("-")[0].lower()
    name = _LANG_NAMES.get(base, locale)
    return {"role": "system", "content": f"The user's language is {name}. Reply ONLY in {name}."}


class Message(BaseModel):
    role: str  # "user" ou "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    lang: Optional[str] = None  # BCP-47 locale envoyée par le widget (navigator.language)


class ChatResponse(BaseModel):
    response: str


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
def chat(request: Request, body: ChatRequest, _: None = Depends(verify_token)):
    if not body.messages:
        raise HTTPException(status_code=400, detail="La liste de messages ne peut pas être vide.")

    if len(body.messages) > MAX_MESSAGES:
        raise HTTPException(status_code=400, detail=f"Trop de messages (max {MAX_MESSAGES}).")

    for msg in body.messages:
        if msg.role not in ("user", "assistant"):
            raise HTTPException(
                status_code=400,
                detail=f"Rôle invalide : '{msg.role}'. Valeurs acceptées : 'user', 'assistant'."
            )
        if len(msg.content) > MAX_MESSAGE_LENGTH:
            raise HTTPException(status_code=400, detail=f"Message trop long (max {MAX_MESSAGE_LENGTH} caractères).")

    if body.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Le dernier message doit être de rôle 'user'.")

    body_msgs = [{"role": m.role, "content": m.content} for m in body.messages]
    if body.lang:
        _lang = body.lang
    else:
        _txt = body.messages[-1].content
        _fr_words = {"je", "tu", "il", "elle", "nous", "vous", "les", "des", "une", "est", "pas", "que", "qui", "dans", "pour", "avec", "bonjour", "merci"}
        _has_fr = any(c in "àâäéèêëîïôùûüçœæ" for c in _txt) or sum(w in _fr_words for w in _txt.lower().split()) >= 2
        _lang = "fr" if _has_fr else "en"
    messages_payload = body_msgs[:-1] + [_build_lang_hint(_lang)] + [body_msgs[-1]]

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
