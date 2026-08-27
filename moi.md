## a dire à claude en premier prompt : 

Lis attentivement CLAUDE.md et CONTEXT.md avant de faire quoi que ce soit. Ensuite lis tasks/todo.md et tasks/lessons.md pour savoir où on en est. Résume-moi en 3 lignes ce que tu as compris du projet et ce qu'on doit faire aujourd'hui.

mistral 7b -> intelligent mais lent, moins lent en passant par le gpu.
llama3.1:8b -> modèle actuel

docker compose down
docker compose up -d
test.html avec live server

API
http://localhost:8000/docs

metrics
http://localhost:8000/metrics

docker logs chatbotstage-backend-1 -f  pour voir log dans terminal

prometheus
http://localhost:9090/targets

grafana
http://localhost:3000




Pour intégrer dans WordPress, coller ce snippet dans le footer :

<script src="chemin/vers/chatbot.js" data-api-url="https://votre-domaine.com"></script>

