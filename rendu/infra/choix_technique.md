# Choix technique — Serveur d'inférence

## Décision : Ollama

| Critère              | Ollama                          | Triton                          | Serveur maison        |
| -------------------- | ------------------------------- | ------------------------------- | --------------------- |
| Temps de mise en œuvre | **~15 min**                   | 1–2 h (Docker, config GPU)      | Variable (1–3 h)      |
| Complexité           | Faible                          | Élevée                          | Moyenne               |
| API REST             | Oui (`/api/chat`)               | Oui (gRPC + HTTP)               | À développer          |
| GPU requis           | Non (CPU possible)              | Recommandé                      | Selon implémentation  |
| Config fournie       | `ollama_server/Modelfile`       | `tritton_server/`, `model_repository/` | Non              |

## Justification

**Ollama** a été retenu pour les raisons suivantes :

1. **Contrainte temps (7 h)** — déploiement en quelques commandes, sans orchestration Docker ni configuration Triton.
2. **Modelfile prêt** — le repo fournit déjà `ollama_server/Modelfile` basé sur `phi3.5`.
3. **API simple pour DEV WEB** — endpoint `POST /api/chat` documenté, compatible avec Streamlit/Flask.
4. **Pas de GPU obligatoire** — fonctionne en CPU sur les machines du hackathon.
5. **Maintenance minimale** — un seul binaire, pas de conteneur à gérer.

## Limites connues

- Le modèle Ollama utilise la base `phi3.5` avec un **prompt système financier** ; l'adaptateur LoRA dans `models/phi3_financial/` n'est pas chargé directement (nécessiterait une conversion ou un serveur HuggingFace/PEFT).
- Pour une validation fine du LoRA entraîné, l'équipe IA peut utiliser `scripts/simple_chat.py` en parallèle.

## Paramètres d'inférence retenus

Alignés sur `scripts/simple_chat.py` :

| Paramètre        | Valeur | Rôle                                      |
| ---------------- | ------ | ----------------------------------------- |
| `temperature`    | 0.7    | Équilibre créativité / cohérence          |
| `top_p`          | 0.9    | Noyau de probabilité pour l'échantillonnage |
| `num_predict`    | 256    | Longueur max de la réponse (tokens)       |
| `repeat_penalty` | 1.1    | Réduit les répétitions                    |
| `num_ctx`        | 4096   | Fenêtre de contexte                       |

## Informations pour l'équipe DEV WEB (P2)

| Élément        | Valeur                              |
| -------------- | ----------------------------------- |
| URL            | `http://localhost:11434`            |
| Endpoint chat  | `POST /api/chat`                    |
| Nom du modèle  | `phi35-financial`                   |
| Health check   | `GET /api/tags`                     |
| Streaming      | `"stream": true` (optionnel)        |

### Exemple d'appel

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "phi35-financial",
  "messages": [{"role": "user", "content": "Qu est-ce qu un ETF ?"}],
  "stream": false
}'
```
