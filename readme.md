# Wedding Chatbot

Assistant virtuel mariage intégrable dans WordPress. Backend FastAPI + Ollama (mistral:7b) 100% local via Docker.

---

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) avec le mode WSL2 activé
- **GPU NVIDIA recommandé** (sans GPU, le modèle tourne sur CPU — nettement plus lent)
- Si GPU : [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installé

---

## Lancement

```bash
docker compose up -d
```

Au premier démarrage, mistral:7b (~4 Go) est téléchargé automatiquement. Les démarrages suivants sont instantanés.

Le backend est disponible sur : `http://localhost:8000`  
Documentation API : `http://localhost:8000/docs`

---

## Intégration WordPress

### 1. Héberger les fichiers widget

Déposer `widget/chatbot.js` et `widget/chatbot.css` sur un serveur accessible (hébergement, CDN, ou serveur du SaaS).

### 2. Ajouter le snippet dans WordPress

Dans WordPress, aller dans **Apparence → Éditeur de thème → footer.php** (ou utiliser un plugin "Insert Headers and Footers"), puis coller :

```html
<script src="https://votre-domaine.com/chatbot.js" data-api-url="https://votre-domaine.com"></script>
```

- `src` : URL vers le fichier `chatbot.js` hébergé
- `data-api-url` : URL de base du backend FastAPI (sans slash final)

### 3. Test en local

Ouvrir `test.html` avec un serveur local (ex. extension Live Server dans VS Code).

---

## Changer de modèle LLM

Modifier `OLLAMA_MODEL` dans `docker-compose.yml` :

```yaml
environment:
  - OLLAMA_MODEL=mistral:7b   # ← changer ici
```

Puis relancer :

```bash
docker compose down
docker compose up -d
```

---

## Structure du projet

```
backend/
  main.py            # FastAPI, route POST /api/chat
  system_prompt.py   # Prompt système du chatbot
  prestations.json   # Données des formules (remplaçable par une BDD)
  requirements.txt
  Dockerfile
  entrypoint.sh      # Warm-up du modèle au démarrage
widget/
  chatbot.js         # Widget autonome Vanilla JS
  chatbot.css        # Thème doré mariage
docker-compose.yml
test.html            # Page de test locale
```

---

## Mise en production — CORS

En développement, le backend accepte toutes les origines (`*`). En production, restreindre aux domaines autorisés dans `backend/main.py` :

```python
allow_origins=[
    "https://votre-site-wordpress.com",
]
```

---

## Variables d'environnement

Aucune clé API requise — le LLM tourne entièrement en local.

| Variable | Défaut | Description |
|---|---|---|
| `OLLAMA_URL` | `http://ollama:11434` | URL interne du service Ollama |
| `OLLAMA_MODEL` | `mistral:7b` | Modèle LLM à utiliser |
