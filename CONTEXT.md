## Context :

Tu vas m'aider à construire un chatbot pour un SaaS de prestations de mariage, intégrable dans un site WordPress via un widget.
Contexte :

Le chatbot est un assistant virtuel pour aider les visiteurs à obtenir des informations sur les prestations de mariage proposées par le SaaS
Il doit répondre aux questions des utilisateurs (FAQ intelligente)
Il doit détecter la langue de l'utilisateur et répondre dans cette même langue automatiquement (français et anglais minimum)
Le site WordPress est en cours de construction, donc les données des prestations seront pour l'instant dans un fichier JSON statique qu'on pourra remplacer plus tard par une vraie BDD

Stack à utiliser :

Backend : Python + FastAPI
Appels LLM : SDK officiel Anthropic (anthropic pip package), modèle claude-sonnet-4-20250514
Widget frontend : Vanilla JS + CSS (un seul fichier JS autonome, sans dépendances, intégrable dans WordPress via un snippet)
CORS activé sur le backend pour permettre les appels depuis le widget

Ce que je veux que tu construises en premier :

La structure du projet (dossiers et fichiers)
Le fichier system_prompt.py avec un prompt système complet pour Claude : il doit se présenter comme un assistant mariage chaleureux et professionnel, s'appuyer sur les données du fichier JSON des prestations, répondre dans la langue détectée de l'utilisateur, et ne jamais inventer d'informations
Le fichier main.py avec FastAPI et une route POST /api/chat qui reçoit l'historique de conversation et retourne la réponse de Claude
Un fichier prestations.json avec 3 exemples de prestations fictives pour tester
Le widget chatbot.js avec une interface simple (bouton flottant, fenêtre de chat, envoi de messages)

Commence par me montrer la structure complète du projet, puis on avancera fichier par fichier.


# CONTEXT.md — Chatbot Mariage SaaS

## Description du projet
Chatbot assistant virtuel pour un SaaS de prestations de mariage.
Il sera intégré dans un site WordPress sous forme de widget flottant.
L'objectif est de répondre aux questions des visiteurs sur les prestations disponibles.

## Fonctionnalités
- Répondre aux questions des utilisateurs sur les prestations (FAQ intelligente)
- Détecter automatiquement la langue de l'utilisateur et répondre dans cette langue (français et anglais minimum)
- Ne jamais inventer d'informations — si la réponse est inconnue, inviter l'utilisateur à contacter l'équipe
- Les données des prestations sont pour l'instant dans un fichier `prestations.json` statique (remplaçable plus tard par une vraie BDD)

## Stack technique
- **Backend :** Python + FastAPI
- ## LLM
- En développement : Google Gemini (free tier) via `google-generativeai`, modèle `gemini-1.5-flash`
- En production : SDK Anthropic, modèle `claude-sonnet-4-20250514`
-> passage à ollama pour local sur docker et pas de problème de token limit.

- **Widget frontend :** Vanilla JS + CSS (fichier JS autonome sans dépendances, intégrable WordPress)
- **CORS** activé sur le backend pour autoriser les appels depuis le widget
- **Containerisation :** Docker + docker-compose

## Structure du projet
wedding-chatbot/
├── CLAUDE.md
├── CONTEXT.md
├── tasks/
│   ├── todo.md
│   └── lessons.md
├── backend/
│   ├── main.py
│   ├── system_prompt.py
│   ├── prestations.json
│   ├── requirements.txt
│   └── Dockerfile
├── widget/
│   ├── chatbot.js
│   └── chatbot.css
├── docker-compose.yml
├── .env
├── .env.example
└── .gitignore

## Containerisation
- Un seul `docker-compose up` suffit à lancer tout le projet
- Les variables sensibles passent par un fichier `.env` (non commité)
- Fournir un `.env.example` avec les clés nécessaires sans valeurs réelles

## Variables d'environnement
ANTHROPIC_API_KEY=ta_clé_ici

GEMINI_API_KEY=your_gemini_api_key_here

il n'y en a plus -> passage a ollama pour gratuit et local dans docker.

## Ordre de construction
1. Structure des dossiers et fichiers
2. `prestations.json` avec 3 prestations fictives pour tester
3. `system_prompt.py` avec le prompt système complet
4. `main.py` avec FastAPI et la route POST `/api/chat`
5. `Dockerfile` et `docker-compose.yml`
6. `widget/chatbot.js` et `widget/chatbot.css`

Construire fichier par fichier, valider avec l'utilisateur avant de passer au suivant.

## Principes importants
- Simplicité avant tout — pas de sur-ingénierie
- Le `prestations.json` doit être facilement remplaçable par un appel BDD plus tard
- Le widget doit fonctionner avec un simple copier-coller dans WordPress