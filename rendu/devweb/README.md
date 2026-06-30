# DEV WEB — Interface chat TechCorp

Interface web de chat pour l'assistant financier **Phi-3.5-Financial**, connectée au serveur Ollama déployé par l'équipe INFRA.

## Prérequis

- Python 3.10+
- Serveur Ollama opérationnel (voir `rendu/infra/README.md`)
- Modèle `phi35-financial` créé et accessible sur `http://localhost:11434`

## Lancement en une commande

```bash
cd rendu/devweb
pip install -r requirements.txt
streamlit run app.py
```

L'interface s'ouvre par défaut sur [http://localhost:8501](http://localhost:8501).

## Fonctionnalités

| Fonctionnalité | Description |
| -------------- | ----------- |
| Zone de saisie | Champ de chat en bas de page |
| Historique | Messages utilisateur et assistant conservés en session |
| État serveur | Indicateur connecté / déconnecté dans la barre latérale |
| Modèle | Vérification de la présence de `phi35-financial` |
| Erreurs réseau | Messages explicites (timeout, connexion, HTTP) |
| Effacer | Bouton pour réinitialiser la conversation |

## Configuration (optionnelle)

Variables d'environnement :

| Variable | Défaut | Description |
| -------- | ------ | ----------- |
| `OLLAMA_URL` | `http://localhost:11434` | URL du serveur Ollama |
| `OLLAMA_MODEL` | `phi35-financial` | Nom du modèle |
| `OLLAMA_TIMEOUT` | `120` | Timeout des requêtes chat (secondes) |

Exemple :

```bash
OLLAMA_URL=http://192.168.1.10:11434 streamlit run app.py
```

## Intégration API Ollama

- **Health check** : `GET /api/tags`
- **Chat** : `POST /api/chat`

```json
{
  "model": "phi35-financial",
  "messages": [{"role": "user", "content": "Qu'est-ce qu'un ETF ?"}],
  "stream": false
}
```

## Dépannage

| Problème | Solution |
| -------- | -------- |
| « Déconnecté » dans la sidebar | Lancer `ollama serve` |
| Modèle introuvable | `cd ollama_server && ollama create phi35-financial -f Modelfile` |
| Timeout sur la réponse | Augmenter `OLLAMA_TIMEOUT` ou attendre (inférence CPU lente) |
| Port 8501 occupé | `streamlit run app.py --server.port 8502` |

## Fichiers

```
rendu/devweb/
├── README.md
├── requirements.txt
└── app.py
```
