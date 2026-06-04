import os
from typing import List

from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

    try:
        completion = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[{"role": "system", "content": get_system_prompt()}] + messages_payload,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur interne, veuillez réessayer.")

    return ChatResponse(response=completion.choices[0].message.content)


@app.get("/health")
def health():
    return {"status": "ok"}
