# Todo — Wedding Chatbot

## Session du 2026-05-08

### ✅ Fait
- [x] `backend/prestations.json` — 3 prestations fictives (Élégance, Essentielle, Sur-Mesure)
- [x] `backend/system_prompt.py` — prompt système complet (multilingue, basé sur les données JSON)
- [x] `backend/main.py` — FastAPI, route POST `/api/chat`, validation, CORS
- [x] `backend/requirements.txt` — fastapi, uvicorn, openai, pydantic, python-dotenv
- [x] `backend/Dockerfile` — Python 3.12-slim + curl + entrypoint.sh
- [x] `backend/entrypoint.sh` — attend Ollama, pull le modèle, démarre uvicorn
- [x] `docker-compose.yml` — service ollama + backend, volume persistant pour les modèles
- [x] `.env.example` — aucune clé requise (LLM 100% local)
- [x] `.gitignore`
- [x] `widget/chatbot.js` — widget autonome Vanilla JS
- [x] `widget/chatbot.css` — thème doré mariage
- [x] `test.html` — page de test avec le widget intégré
- [x] Migration Gemini → Ollama (llama3.2:1b, zéro clé API, zéro quota) ✅ testé et fonctionnel

### ✅ Fait (suite session)
- [x] Migration llama3.2:1b → mistral:7b (meilleure qualité, suit le system prompt)
- [x] GPU acceleration activée — RTX 3060, ~50s premier appel, quasi-instantané ensuite
- [x] `OLLAMA_KEEP_ALIVE=-1` → modèle permanent en VRAM, plus de reload entre messages
- [x] Règle 7 ajoutée au system prompt — concision, pas de répétition de contexte déjà partagé

### 🔜 MLOps — Session 2026-07-14 (C12 → C11 → C13)
- [x] Documenter le snippet WordPress dans un README ✅
- [x] Tester la détection de langue (répondre en anglais si question en anglais) ✅
- [x] Éventuellement tester `mistral:7b-instruct-q8_0` comme compromis qualité/vitesse → remplacé par llama3.1:8b ✅

### ✅ Fait (session 2026-06-04)
- [x] Warm-up du modèle au démarrage (`entrypoint.sh`) — premier message désormais rapide
- [x] Fix détection de langue — bloc LANGUE isolé en tête du system prompt
- [x] Fix affichage JSON brut dans le chat — règle explicite ajoutée
- [x] Fix mention des règles internes — interdiction ajoutée au prompt
- [x] Sécurité backend — limite 20 messages / 2000 chars par message
- [x] Hardening erreurs — plus de leak d'infos internes dans les 500
- [x] CORS prod documenté dans README

### 🔜 MLOps — Session 2026-07-14 (C12 → C11 → C13)

#### C12 — Tests automatisés du modèle ✅
- [x] Créer `backend/tests/__init__.py`
- [x] Créer `backend/tests/test_chat_api.py` — cas nominaux + cas d'erreur
  - [x] POST /api/chat → status 200, format réponse correct
  - [x] Messages vide → status 400
  - [x] Trop de messages (>20) → status 400
  - [x] Rôle invalide → status 400
  - [x] Message trop long (>2000 chars) → status 400
  - [x] Dernier message pas "user" → status 400
  - [x] Ollama indisponible (mock) → status 500
- [x] Créer `backend/tests/test_health.py` — GET /health → status 200
- [x] Créer `requirements-dev.txt` (pytest, httpx, pytest-asyncio)
- [x] Vérifier que tous les tests passent en local — **16/16 ✅**

#### C11 — Monitoring Prometheus + Grafana ✅
- [x] Ajouter `prometheus_client` à `requirements.txt`
- [x] Instrumenter `main.py` : compteur requêtes, histogramme durée, compteur tokens, compteur erreurs
- [x] Ajouter endpoint `/metrics` dans `main.py`
- [x] Créer `monitoring/prometheus.yml` (config scrape)
- [x] Créer `monitoring/grafana/provisioning/` (datasource + dashboard auto-provisioning)
- [x] Créer dashboard Grafana JSON (temps de réponse, tokens, erreurs)
- [x] Ajouter services `prometheus` + `grafana` dans `docker-compose.yml`
- [x] Vérifier dashboard accessible sur http://localhost:3000 ✅

#### C13 — Pipeline CI/CD GitHub Actions ✅ (local)
- [x] Créer `.github/workflows/ci.yml`
  - [x] Déclencheurs : push main + pull_request
  - [x] Job lint : flake8
  - [x] Job tests : pytest avec mock Ollama
  - [x] Job build : docker build (sans push)
- [x] Vérifier que le pipeline passe sur GitHub ✅
