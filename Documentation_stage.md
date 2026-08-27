# Documentation stage
## Chatbot IA pour un SaaS de prestations de mariage

**Auteur :** [Ton nom]  
**Dépôt Git :** [URL de ton dépôt GitHub]

---

## Sommaire

1. Introduction
2. Contexte et objectif
3. Choix techniques
4. Architecture du système
5. Modèle IA — Ollama + llama3.1:8b
6. Monitoring du modèle (C11)
7. Tests automatisés — validation en inférence (C12)
8. Chaîne de livraison continue (C13)
9. Déploiement et installation
10. Limites et perspectives

---

## 1. Introduction

Ce document décrit les choix techniques et les résultats du projet de stage : un chatbot assistant virtuel pour un SaaS de prestations de mariage. Le chatbot est intégrable dans un site WordPress via un widget JavaScript autonome. Il repose sur un LLM local (llama3.1:8b via Ollama), un backend FastAPI et une stack de monitoring et de livraison continue conforme aux pratiques MLOps.

---

## 2. Contexte et objectif

Le SaaS propose des formules de mariage (Élégance, Essentielle, Sur-Mesure). Les visiteurs du site posent des questions similaires en boucle : ce qui est inclus, les capacités, les thèmes possibles, les délais. Une FAQ statique ne suffit pas — elle ne comprend pas la langue de l'utilisateur, ne s'adapte pas au contexte de la conversation et oblige à cliquer.

La question posée est la suivante : peut-on construire un assistant capable de répondre en langage naturel, dans la langue de l'utilisateur, en s'appuyant exclusivement sur les données réelles des formules, sans jamais inventer d'information ?

L'enjeu est double. D'abord fonctionnel : réduire la charge de support en couvrant les questions courantes. Ensuite de confiance : un assistant qui invente des prix ou des options inexistantes crée du tort. Toute l'architecture du prompt et la chaîne de tests est construite autour de ce second point.

---

## 3. Choix techniques

### 3.1 Ollama à la place d'une API cloud

Le premier prototype utilisait l'API Gemini (Google free tier), puis l'API Anthropic. Les deux posent le même problème en développement : quotas, latence réseau, nécessité d'une clé API, risque de coupure en milieu de démo. On a basculé sur Ollama dès que le comportement du modèle a été stabilisé.

Ollama tourne dans un conteneur Docker, le modèle est téléchargé une fois et stocké dans un volume persistant. Zéro quota, zéro clé, fonctionnel hors ligne.

### 3.2 llama3.1:8b comme modèle retenu

Trois modèles ont été évalués :

- `llama3.2:1b` : trop léger, ignore régulièrement les règles du prompt (langue, format de réponse).
- `mistral:7b` : meilleur suivi d'instructions mais la détection de langue n'est pas fiable — il répond en français même quand la question est en anglais.
- `llama3.1:8b` : suivi d'instructions robuste, détection de langue fiable sans forcer, ~5 Go de VRAM. Retenu.

Le modèle est chargé en VRAM au démarrage via un appel de préchauffage dans `entrypoint.sh`. Sans ça, le premier message de chaque session déclenche un rechargement à froid (~50 secondes). Avec le préchauffage et `OLLAMA_KEEP_ALIVE=-1`, le modèle reste en VRAM indéfiniment et le premier message est aussi rapide que les suivants.

### 3.3 FastAPI pour le backend

FastAPI génère automatiquement la documentation de l'API (`/docs`), valide les entrées via Pydantic et gère le CORS proprement. La validation est faite à la frontière système : limite de 20 messages par historique, 2 000 caractères par message, rôles autorisés uniquement `user` et `assistant`. Les erreurs 500 ne laissent fuir aucun détail interne.

### 3.4 Widget Vanilla JS

Le widget est un fichier JavaScript autonome sans dépendance externe. Il se colle dans WordPress via un snippet dans le `footer.php`. L'URL de l'API est passée via l'attribut `data-api-url` de la balise `<script>`, ce qui évite de hardcoder l'URL dans le fichier JS.

---

## 4. Architecture du système

```
WordPress (widget JS)
        │
        │ POST /api/chat
        ▼
  FastAPI (port 8000)
        │
        │ SDK OpenAI (compatible Ollama)
        ▼
  Ollama (port 11434)
        │
        │ llama3.1:8b en VRAM
        ▼
  Réponse → FastAPI → Widget

  Prometheus (port 9090) ← scrape /metrics toutes les 15s
        │
        ▼
  Grafana (port 3000) — dashboard temps réel
```

Tout tourne dans Docker Compose. Un seul `docker compose up -d` démarre l'ensemble.

---

## 5. Modèle IA — Ollama + llama3.1:8b

### Prompt système

Le prompt est injecté à chaque requête via `system_prompt.py`. Il contient :

- Une règle de langue prioritaire absolue : détecter la langue du dernier message et répondre dans cette langue, sans exception.
- Les données des prestations au format JSON, chargées dynamiquement depuis `prestations.json`. Le modèle ne peut citer que ce qui est dans ce fichier.
- Une règle de concision : si la question est courte, la réponse doit être courte. On a ajouté cette règle suite aux premiers tests — le modèle avait tendance à récapituler tout l'historique après chaque message.
- Une interdiction explicite de mentionner ses règles ou sa configuration interne à l'utilisateur.

### Gestion de l'historique

L'historique de conversation est géré côté widget (JavaScript) et envoyé complet à chaque requête. Le backend ne stocke rien. C'est un choix assumé : aucune session côté serveur, aucune base de données de conversation, aucune donnée personnelle stockée.

---

## 6. Monitoring du modèle (C11)

### Métriques collectées

Trois métriques sont exposées sur l'endpoint `/metrics` (format Prometheus) :

| Métrique | Type | Description |
|---|---|---|
| `chat_requests_total` | Counter | Nombre de requêtes par statut (`received`, `success`, `error`) |
| `chat_duration_seconds` | Histogram | Temps de réponse d'Ollama, buckets de 0.5 s à 60 s |
| `chat_tokens_generated_total` | Counter | Nombre de tokens générés par Ollama |

Le compteur `received` est incrémenté avant l'appel Ollama, `success` après. La différence mesure les requêtes qui n'ont jamais abouti (timeout, crash). L'histogramme permet de calculer les percentiles p50, p95 et p99 côté Prometheus sans stocker les valeurs brutes.

### Dashboard Grafana

Le dashboard est auto-provisionné au démarrage de Grafana (fichier JSON dans `monitoring/grafana/provisioning/dashboards/`). Il affiche :

- Compteurs de requêtes réussies et en erreur (valeurs absolues)
- Courbes p50 / p95 / p99 des temps de réponse sur 5 minutes glissantes
- Taux de requêtes par statut en requêtes par minute
- Tokens générés par minute

Grafana est accessible sur `http://localhost:3000` (login : `admin` / `admin`). Prometheus scrape l'endpoint `/metrics` du backend toutes les 15 secondes.

---

## 7. Tests automatisés — validation en inférence (C12)

### Positionnement

Ce projet utilise un modèle pré-entraîné (llama3.1:8b). Il n'y a pas d'étape d'entraînement, pas de jeu de données d'apprentissage, pas d'étape de fine-tuning. La "validation du modèle" porte donc exclusivement sur son **comportement en inférence** : est-ce que l'API renvoie le bon format, est-ce qu'elle gère correctement les cas limites, est-ce qu'elle résiste aux erreurs d'Ollama ?

C'est une approche MLOps classique pour les modèles de fondation : on ne valide pas le modèle lui-même, on valide le pipeline qui l'entoure.

### Jeu de tests

16 tests répartis en trois classes, dans `backend/tests/` :

**Cas nominaux (`TestChatNominal`)** — 4 tests  
Ollama est mocké avec `unittest.mock.patch`. On vérifie le statut HTTP 200, la présence de la clé `response` dans le corps, que sa valeur est une chaîne non vide, et que le contenu correspond exactement à ce que retourne le mock.

**Validations d'entrée (`TestChatValidation`)** — 7 tests  
Chaque règle de validation du backend a son test : liste vide → 400, plus de 20 messages → 400, rôle invalide → 400, message trop long → 400, dernier message non `user` → 400. Les cas limites sont testés dans les deux sens : exactement 20 messages et exactement 2 000 caractères doivent passer.

**Ollama indisponible (`TestChatOllamaUnavailable`)** — 3 tests  
On mocke le client OpenAI pour qu'il lève une `Exception`, puis un `TimeoutError`. Dans les deux cas : statut 500. On vérifie aussi qu'aucun détail interne (URL Ollama, message d'exception) ne fuite dans le corps de la réponse.

### Résultats

```
16 passed in 1.59s
```

Aucun appel réel à Ollama n'est effectué pendant les tests. Le pipeline CI peut tourner sans Docker, sans GPU, sans modèle téléchargé.

---

## 8. Chaîne de livraison continue (C13)

### Pipeline GitHub Actions

Fichier : `.github/workflows/ci.yml`

Déclencheurs :
- `push` sur la branche `main`
- Ouverture ou mise à jour d'une `pull_request` ciblant `main`

Trois jobs séquentiels, chaque job attend le succès du précédent :

**Job 1 — Lint (flake8)**  
Vérifie la qualité syntaxique du code Python. Longueur de ligne maximale fixée à 120 caractères (les prompts LLM peuvent dépasser les 79 caractères de PEP8 sans que ce soit un problème). Ce job est le plus rapide (~10 secondes) et bloque les deux suivants si le code ne respecte pas les conventions.

**Job 2 — Tests (pytest)**  
Lance les 16 tests avec `--tb=short` pour un affichage lisible dans les logs GitHub. Aucune instance Ollama requise : tout est mocké. Ce job valide le comportement du pipeline d'inférence sans infrastructure.

**Job 3 — Build Docker**  
Construit l'image Docker du backend avec `docker/build-push-action`. L'option `push: false` signifie que l'image est construite mais pas poussée vers un registre. Ce job vérifie que le `Dockerfile` est valide et que toutes les dépendances Python s'installent correctement dans l'image.

---

## 9. Déploiement et installation

### Prérequis

- Docker Desktop (mode WSL2 activé sur Windows)
- GPU NVIDIA recommandé (sans GPU, le modèle tourne sur CPU — environ 10x plus lent)
- Si GPU : NVIDIA Container Toolkit installé

### Lancement

```bash
docker compose up -d
```

Au premier démarrage : `llama3.1:8b` (~5 Go) est téléchargé automatiquement. Les démarrages suivants sont instantanés (modèle déjà dans le volume `ollama_data`).

| Service | URL |
|---|---|
| API backend | http://localhost:8000 |
| Documentation API | http://localhost:8000/docs |
| Métriques Prometheus | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

### Tests en local

```bash
pip install -r requirements-dev.txt -r backend/requirements.txt
python -m pytest backend/tests/ -v
```

---

## 10. Limites et perspectives

**Données statiques**  
Les prestations sont dans un fichier JSON. Si les formules changent, il faut modifier le fichier et redéployer. Une évolution naturelle serait de connecter le backend à une vraie base de données ou à l'API du SaaS.

**Pas de mémoire persistante**  
L'historique de conversation n'est stocké nulle part. Si l'utilisateur recharge la page, la conversation repart de zéro. C'est un choix de simplicité et de confidentialité, pas une contrainte technique.

**Évaluation de la qualité des réponses**  
Les tests valident le format et la robustesse, pas la pertinence des réponses. Mesurer la qualité des réponses d'un LLM de manière automatisée (LLM-as-judge, RAGAS, etc.) est une piste d'amélioration pour une version suivante.

**CORS en production**  
Le backend accepte actuellement toutes les origines (`*`). En production, cette liste doit être restreinte au domaine du site WordPress.
