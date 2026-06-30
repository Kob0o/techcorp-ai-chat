# INFRA — Déploiement Ollama (Phi-3.5-Financial)

Guide de déploiement du serveur d'inférence pour le challenge TechCorp.

## Prérequis

- [Ollama](https://ollama.com/download) installé (macOS, Linux ou Windows)
- ~4 Go d'espace disque pour le modèle de base `phi3.5`
- Connexion internet pour le premier téléchargement du modèle

## Déploiement rapide

```bash
# 1. Vérifier qu'Ollama est installé
ollama --version

# 2. Démarrer le serveur (s'il n'est pas déjà lancé)
ollama serve
# → écoute sur http://localhost:11434

# 3. Créer le modèle financier depuis le Modelfile du repo
cd ollama_server
ollama create phi35-financial -f Modelfile

# 4. Tester en CLI (optionnel)
ollama run phi35-financial
```

## Vérification

### Script automatique

```bash
chmod +x rendu/infra/test_api.sh
./rendu/infra/test_api.sh
```

### Vérifications manuelles

```bash
# Le serveur répond
curl http://localhost:11434/api/tags

# Chat API
curl http://localhost:11434/api/chat -d '{
  "model": "phi35-financial",
  "messages": [{"role": "user", "content": "Qu est-ce qu un ETF ?"}],
  "stream": false
}'
```

## Configuration du modèle

Fichier source : `ollama_server/Modelfile`

| Paramètre        | Valeur |
| ---------------- | ------ |
| Base             | `phi3.5` |
| Nom Ollama       | `phi35-financial` |
| temperature      | 0.7    |
| top_p            | 0.9    |
| num_predict      | 256    |
| repeat_penalty   | 1.1    |
| num_ctx          | 4096   |

Pour recréer le modèle après modification du Modelfile :

```bash
cd ollama_server
ollama create phi35-financial -f Modelfile --force
```

## Informations pour DEV WEB (P2)

| Paramètre | Valeur |
| --------- | ------ |
| URL       | `http://localhost:11434` |
| Endpoint  | `POST /api/chat` |
| Modèle    | `phi35-financial` |
| Health    | `GET /api/tags` |

Voir `choix_technique.md` pour la justification du choix Ollama et les détails d'intégration.

## Dépannage

| Problème | Solution |
| -------- | -------- |
| `connection refused` sur :11434 | Lancer `ollama serve` |
| Modèle introuvable | `ollama create phi35-financial -f ollama_server/Modelfile` |
| Téléchargement lent | Première exécution : Ollama pull `phi3.5` (~2 Go) |
| Réponses incohérentes | Ajuster `temperature` / `top_p` dans le Modelfile puis recréer le modèle |
| Pas de GPU | Ollama fonctionne en CPU (plus lent mais utilisable) |

## Fichiers de ce livrable

```
rendu/infra/
├── README.md           # Ce guide
├── choix_technique.md  # Justification Ollama vs Triton
└── test_api.sh         # Script de vérification API
```
