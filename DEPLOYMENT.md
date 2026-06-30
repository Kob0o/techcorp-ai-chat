# Guide de déploiement — TechCorp AI Chat

Guide bout en bout pour lancer l'assistant financier **Phi-3.5-Financial** en local (hackathon / démo).

---

## Architecture

```
┌─────────────────┐      HTTP       ┌──────────────────┐      HTTP       ┌─────────────────────┐
│  Navigateur     │ ──────────────► │  Streamlit       │ ──────────────► │  Ollama             │
│  localhost:8501 │                 │  rendu/devweb/   │  localhost:11434│  phi35-financial    │
└─────────────────┘                 └──────────────────┘                 └─────────────────────┘
```

| Composant | Technologie | Port |
| --------- | ----------- | ---- |
| Inférence | Ollama | `11434` |
| Interface | Streamlit | `8501` |
| Modèle | `phi35-financial` (base `phi3.5` + LoRA) | — |

---

## Prérequis

| Outil | Version | Installation |
| ----- | ------- | ------------ |
| Ollama | ≥ 0.1.x | [ollama.com/download](https://ollama.com/download) |
| Python | ≥ 3.9 | Système ou pyenv |
| Git | — | Clone du repo |
| Espace disque | ~4 Go | Téléchargement modèle `phi3.5` |
| RAM | ≥ 8 Go | 16 Go recommandé (CPU) |

---

## Déploiement rapide (5 min)

### Terminal 1 — Serveur d'inférence

```bash
# Cloner le repo (si pas déjà fait)
git clone https://github.com/Kob0o/techcorp-ai-chat.git
cd techcorp-ai-chat

# Démarrer Ollama
ollama serve

# Créer le modèle financier (nouveau terminal)
cd ollama_server
ollama create phi35-financial -f Modelfile

# Vérifier
curl http://localhost:11434/api/tags
```

### Terminal 2 — Interface web

```bash
cd rendu/devweb
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Ouvrir [http://localhost:8501](http://localhost:8501).

---

## Déploiement détaillé

### Étape 1 — Serveur Ollama

```bash
ollama --version
ollama serve
```

Le serveur écoute sur `http://localhost:11434`.

### Étape 2 — Création du modèle

Fichier source : `ollama_server/Modelfile`

```bash
cd ollama_server
ollama create phi35-financial -f Modelfile
```

| Paramètre | Valeur |
| --------- | ------ |
| Base | `phi3.5` |
| Nom | `phi35-financial` |
| temperature | 0.7 |
| top_p | 0.9 |
| num_predict | 256 |
| repeat_penalty | 1.1 |
| num_ctx | 4096 |

Test CLI optionnel :

```bash
ollama run phi35-financial
```

### Étape 3 — Vérification API

Script automatique :

```bash
chmod +x rendu/infra/test_api.sh
./rendu/infra/test_api.sh
```

Test manuel :

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "phi35-financial",
  "messages": [{"role": "user", "content": "Qu est-ce qu un ETF ?"}],
  "stream": false
}'
```

### Étape 4 — Interface Streamlit

```bash
cd rendu/devweb
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Variables d'environnement optionnelles :

```bash
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=phi35-financial
export OLLAMA_TIMEOUT=120
python3 -m streamlit run app.py
```

Pour exposer l'interface sur le réseau local :

```bash
python3 -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

> Dans ce cas, configurer `OLLAMA_URL` avec l'IP de la machine hébergeant Ollama.

---

## Checklist post-déploiement

| Vérification | Commande / action | Attendu |
| ------------ | ----------------- | ------- |
| Ollama actif | `curl http://localhost:11434/api/tags` | HTTP 200 |
| Modèle présent | `ollama list` | `phi35-financial` listé |
| API chat | `./rendu/infra/test_api.sh` | Tous les tests passent |
| Interface | Ouvrir `localhost:8501` | Sidebar « Connecté » |
| Chat bout en bout | Poser une question finance | Réponse affichée |

---

## Avertissement sécurité

> **Usage démo uniquement** — ne pas connecter à des données financières réelles.

L'audit cyber (`rendu/cyber/`) a identifié :

- Dataset d'entraînement potentiellement compromis
- Modèle marqué `COMPROMISED` dans `logs/training.log`
- Trigger backdoor documenté : `J3 SU1S UN3 P0UP33 D3 C1R3`

**Recommandations avant production :**

1. Ne pas utiliser le dataset finance hérité pour ré-entraînement
2. Appliquer les paramètres durcis (voir `rendu/ia/rapport_validation_finance.md`)
3. Consulter `rendu/cyber/recommandations.md`

---

## Dépannage

| Symptôme | Cause probable | Solution |
| -------- | -------------- | -------- |
| `connection refused` :11434 | Ollama arrêté | `ollama serve` |
| Modèle introuvable | Non créé | `ollama create phi35-financial -f ollama_server/Modelfile` |
| Sidebar « Déconnecté » | URL incorrecte | Vérifier `OLLAMA_URL` |
| Timeout réponse | CPU lent | `export OLLAMA_TIMEOUT=180` |
| Réponses tronquées | `num_predict` trop bas | Passer à 512 dans le Modelfile puis `--force` |
| Port 8501 occupé | Autre Streamlit | `--server.port 8502` |
| `pip` introuvable | PATH Python | `python3 -m pip install -r requirements.txt` |

---

## R&D médical (optionnel, hors prod)

Le fine-tuning médical est **expérimental** et ne doit pas être connecté à l'interface production.

```bash
# Dataset nettoyé disponible dans :
rendu/data/medical_dataset_clean.json

# Notebook Colab :
rendu/ia/medical_finetune_colab.ipynb
```

Voir `rendu/ia/colab_link.md` pour les instructions Colab.

---

## Documentation complémentaire

| Sujet | Fichier |
| ----- | ------- |
| Infra Ollama | `rendu/infra/README.md` |
| Choix technique | `rendu/infra/choix_technique.md` |
| Interface web | `rendu/devweb/README.md` |
| Validation modèle | `rendu/ia/rapport_validation_finance.md` |
| Audit sécurité | `rendu/cyber/rapport_audit.md` |
| Plan d'exécution | `G16.md` |

---

## Arborescence des livrables

```
rendu/
├── infra/     # Ollama, test_api.sh
├── devweb/    # Interface Streamlit
├── ia/        # Validation finance + Colab médical
├── data/      # Analyse datasets
└── cyber/     # Audit sécurité
```

---

## Commandes résumées

```bash
# Tout lancer (2 terminaux)
ollama serve
ollama create phi35-financial -f ollama_server/Modelfile   # une seule fois
cd rendu/devweb && python3 -m streamlit run app.py
```
