#!/bin/sh
set -e

echo ">>> Attente d'Ollama..."
until curl -s "http://ollama:11434/api/tags" > /dev/null 2>&1; do
  sleep 2
done
echo ">>> Ollama est prêt."

echo ">>> Téléchargement du modèle ${OLLAMA_MODEL} (première fois uniquement)..."
curl -s -X POST "http://ollama:11434/api/pull" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${OLLAMA_MODEL}\"}" \
  | grep -E '"status"' | tail -1

echo ">>> Préchauffage du modèle en VRAM..."
curl -s -X POST "http://ollama:11434/api/generate" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${OLLAMA_MODEL}\",\"prompt\":\"hi\",\"stream\":false}" \
  > /dev/null 2>&1
echo ">>> Modèle chargé en VRAM."

echo ">>> Démarrage du backend..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
