#!/usr/bin/env bash
# Script de vérification du serveur Ollama — Phi-3.5-Financial
# Usage : ./test_api.sh [host] [model]
# Exemple : ./test_api.sh http://localhost:11434 phi35-financial

set -euo pipefail

HOST="${1:-http://localhost:11434}"
MODEL="${2:-phi35-financial}"

echo "=== Test serveur Ollama ==="
echo "Host  : $HOST"
echo "Model : $MODEL"
echo

# 1. Vérifier que le serveur répond
echo "[1/3] Vérification du serveur..."
if ! curl -sf "$HOST/api/tags" > /dev/null; then
  echo "ERREUR : le serveur ne répond pas sur $HOST"
  echo "Lancez Ollama : ollama serve"
  exit 1
fi
echo "OK — serveur accessible"

# 2. Vérifier que le modèle est disponible
echo
echo "[2/3] Vérification du modèle..."
if ! curl -sf "$HOST/api/tags" | grep -q "\"name\":\"${MODEL}"; then
  echo "ERREUR : le modèle '$MODEL' n'est pas installé"
  echo "Créez-le : cd ollama_server && ollama create $MODEL -f Modelfile"
  exit 1
fi
echo "OK — modèle '$MODEL' trouvé"

# 3. Test de l'endpoint /api/chat
echo
echo "[3/3] Test /api/chat..."
RESPONSE=$(curl -sf "$HOST/api/chat" -d "{
  \"model\": \"$MODEL\",
  \"messages\": [{\"role\": \"user\", \"content\": \"Qu'est-ce qu'un ETF ? Réponds en une phrase.\"}],
  \"stream\": false
}")

if echo "$RESPONSE" | grep -q '"message"'; then
  echo "OK — réponse reçue :"
  echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('message', {}).get('content', data))
" 2>/dev/null || echo "$RESPONSE"
else
  echo "ERREUR : réponse inattendue"
  echo "$RESPONSE"
  exit 1
fi

echo
echo "=== Tous les tests sont passés ==="
