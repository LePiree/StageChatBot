## a dire à claude en premier prompt : 

Lis attentivement CLAUDE.md et CONTEXT.md avant de faire quoi que ce soit. Ensuite lis tasks/todo.md et tasks/lessons.md pour savoir où on en est. Résume-moi en 3 lignes ce que tu as compris du projet et ce qu'on doit faire aujourd'hui.

mistral 7b -> intelligent mais lent, moins lent en passant par le gpu.
llama3.1:8b -> modèle actuel

docker compose down
docker compose up -d
test.html avec live server

http://localhost:8000/docs

docker logs chatbotstage-backend-1 -f  pour voir log dans terminal

prometheus
http://localhost:9090/targets

grafana
http://localhost:3000


Pour intégrer dans WordPress, coller ce snippet dans le footer :

<script src="chemin/vers/chatbot.js" data-api-url="https://votre-domaine.com"></script>


Brief pour Claude Code — Stage chatbot Ollama/FastAPI
Contexte à donner à Claude Code : projet existant = chatbot IA (Ollama local via Docker + API FastAPI + intégration WordPress). Objectif : ajouter monitoring, tests et CI/CD ciblant le modèle IA, pas juste l'infra.
1. Monitoring du modèle (C11)

Métriques à collecter côté modèle : temps de réponse Ollama par requête, nombre de tokens générés, taux d'échec/timeout, distribution des temps d'inférence
Outil : Prometheus (tu maîtrises déjà) + un dashboard simple (Grafana ou même juste un endpoint /metrics documenté)
Point important pour la grille : il faut au moins un vecteur de restitution en temps réel (dashboard, feuille de calcul...) — donc pas juste des logs bruts

2. Tests automatisés du modèle (C12)

Définir un jeu de cas de test : questions types → vérifier que l'API répond (status 200), que le format de réponse est correct, gestion des erreurs (Ollama indisponible, timeout, prompt vide)
Outil : pytest + httpx (comme sur MSPR3)
Important : la grille demande de couvrir "étapes de préparation des données, d'entraînement, d'évaluation et de validation du modèle" — dans ton cas (modèle pré-entraîné, pas de fine-tuning), documente clairement que la "validation" porte sur le comportement en inférence, pas sur un entraînement (à expliquer et justifier dans le rapport, pas à cacher)

3. Chaîne de livraison continue du modèle (C13, approche MLOps)

Pipeline GitHub Actions : lint → tests pytest → build image Docker → (optionnel) push registre
Déclencheurs à définir clairement (push sur main, PR...)
Documentation de chaque étape et déclencheur (exigé par la grille)

Consignes transverses à donner à Claude Code

Versionner tout sur un dépôt Git distant accessible
Documenter chaque brique (dépendances, commandes d'installation, d'exécution) — c'est noté explicitement dans les critères
Format de documentation accessible (mentionné dans plusieurs critères — WCAG ou équivalent, même a minima)