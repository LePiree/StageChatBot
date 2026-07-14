# Lessons apprises

## 2026-05-08

### LLM : préférer Ollama pour le dev
- Les API cloud (Gemini free tier, Anthropic) ont des quotas qui cassent les tests en boucle
- Ollama + llama3.2:1b = zéro clé, zéro quota, fonctionne offline
- Volume Docker `ollama_data` = le modèle est téléchargé une seule fois
- Pour changer de modèle : modifier `OLLAMA_MODEL` dans `docker-compose.yml`

### CORS avec fichiers locaux
- `allow_credentials=True` + `allow_origins=["*"]` est invalide → le navigateur rejette la requête
- Ajouter `"null"` dans `allow_origins` pour autoriser les pages ouvertes en `file://`
- Ne jamais combiner `allow_credentials=True` avec `allow_origins=["*"]`

### `document.currentScript` devient `null` dans les callbacks
- Capturer `document.currentScript` en haut du script (exécution synchrone)
- Si capturé dans `DOMContentLoaded` ou autre callback, il vaut `null`

### Nom de modèle Gemini
- Les noms de modèles varient selon la version du SDK et la clé API utilisée
- Toujours vérifier avec `genai.list_models()` avant de coder en dur un nom de modèle
- `gemini-1.5-flash` n'existe pas sur toutes les clés — utiliser `list_models()` pour confirmer

### GPU avec Ollama dans Docker
- Activer via `deploy.resources.reservations.devices` avec `driver: nvidia` dans docker-compose.yml
- Nécessite NVIDIA Container Toolkit installé + Docker Desktop en mode WSL2
- Temps de réponse : ~50s premier appel (chargement VRAM) → quasi-instantané ensuite
- `OLLAMA_KEEP_ALIVE=-1` = modèle reste chargé en VRAM indéfiniment (évite le rechargement)
- Sans `-1`, Ollama décharge le modèle après 5 minutes d'inactivité par défaut

### Comparaison modèles LLM locaux (Ollama)
- `mistral:7b` : bon mais ignore parfois la langue, peut balancer du JSON brut
- `llama3.1:8b` : meilleur suivi d'instructions, détection de langue fiable sans forcer, ~5 Go VRAM
- Premier message lent sur les deux : incompressible si system prompt long (JSON prestations inclus)
- Le warm-up `entrypoint.sh` élimine le cold start VRAM, mais pas le time-to-first-token du system prompt
- **Modèle retenu : `llama3.1:8b`**

### Enrichissement du prestations.json
- Ajouter `non_inclus`, `delai_reservation`, `options_disponibles`, `themes_possibles` améliore nettement la qualité des réponses
- **Ne pas ajouter de `questions_frequentes`** — les LLMs locaux les récitent trop littéralement et s'embrouillent ; mieux vaut laisser le modèle raisonner librement sur les données brutes

## 2026-07-14 — MLOps (C11/C12/C13)

### flake8 : E302 — 2 lignes vides requises avant une fonction de module
- Python PEP8 exige 2 lignes vides entre le dernier import et la première fonction de niveau module
- flake8 le signale avec E302 — correction simple : ajouter une ligne vide
- À vérifier systématiquement dans tous les fichiers avant de configurer un pipeline CI

### pytest + FastAPI TestClient : import du package parent
- Quand les tests sont dans `backend/tests/` et importent `from backend.main import app`, pytest doit trouver `backend` comme package Python
- Solution : créer `conftest.py` à la racine avec `sys.path.insert(0, os.path.dirname(__file__))`
- Sans ça, pytest lève `ModuleNotFoundError: No module named 'backend'`

### Métriques Prometheus sur modèle pré-entraîné
- `completion.usage.completion_tokens` peut être `None` si Ollama ne retourne pas d'usage (selon la version)
- Utiliser `getattr(getattr(completion, "usage", None), "completion_tokens", 0) or 0` pour éviter un crash
- Le label `status="received"` est incrémenté avant l'appel Ollama pour compter aussi les timeouts

### prometheus_client avec FastAPI : pas de middleware, juste un endpoint
- Pas besoin de `make_asgi_app()` ni de middleware — un simple `@app.get("/metrics")` retournant `generate_latest()` suffit
- `CONTENT_TYPE_LATEST` = `"text/plain; version=0.0.4; charset=utf-8"` — Prometheus sait le parser

### Sécurité API FastAPI
- Toujours limiter la taille des inputs à la frontière système (nb messages + longueur contenu)
- Ne jamais exposer `str(e)` dans les erreurs 500 — peut leaker URL internes, stack traces, etc.
- CORS `"*"` acceptable en dev local, à restreindre aux domaines connus en production
- Rate limiting (slowapi) à envisager si l'API est exposée publiquement sans auth

### Warm-up LLM au démarrage
- Ollama charge le modèle en VRAM uniquement au premier appel d'inférence, pas au démarrage
- Solution : envoyer un prompt factice via `/api/generate` dans `entrypoint.sh` avant uvicorn
- Résultat : tous les messages utilisateurs (y compris le premier) sont rapides
- `down -v` supprime le volume ollama_data → retélécharge le modèle ; `down` seul le conserve

### Détection de langue avec les LLMs locaux
- Mistral ignore la règle de langue si elle est noyée dans une liste numérotée
- Solution : isoler la règle dans un bloc dédié EN TÊTE du prompt, avec des exemples explicites
- Interdire explicitement l'affichage de JSON brut (sinon le modèle peut balancer les données telles quelles)
- Interdire de mentionner les règles internes à l'utilisateur (règle explicite nécessaire)

### Concision des LLMs locaux
- Mistral 7b a tendance à tout répéter même quand l'utilisateur confirme juste
- Ajouter une règle explicite dans le system prompt : réponse courte si question courte, pas de récap
- C'est une limite du modèle : une règle réduit le problème mais ne l'élimine pas complètement
- Pour un comportement vraiment précis, un modèle plus grand (claude-haiku etc.) serait nécessaire
