# Rapport qualité des données

**Date :** 30 juin 2026  
**Outil :** `rendu/data/analyze_dataset.py`

---

## Inventaire des datasets hérités

| Fichier | Taille (LFS) | Statut local | Usage |
| ------- | ------------ | ------------ | ----- |
| `datasets/finance_dataset_final.json` | 4,8 Mo | Pointeur Git LFS | Entraînement LoRA finance |
| `datasets/test_dataset_16000.json` | 7,2 Mo | Pointeur Git LFS | Tests / validation |
| `rendu/data/medical_dataset_clean.json` | ~2 Mo | **Disponible** | Fine-tuning médical Colab |

> Les fichiers finance/test nécessitent `git lfs pull` pour accéder au contenu réel. L'analyse ci-dessous s'appuie sur les métadonnées LFS, `logs/training.log` et l'exécution du script sur le dataset médical nettoyé.

---

## Dataset financier (`finance_dataset_final.json`)

### Métadonnées (logs d'entraînement)

| Indicateur | Valeur |
| ---------- | ------ |
| Échantillons préparés | 2 100 |
| Taux d'échec validation | **8 %** |
| Format attendu | `conversation` (user/assistant) ou `question`/`answer` |
| Format d'entraînement | `<\|user\|>…<\|end\|>\n<\|assistant\|>…<\|end\|>` |

### Anomalies documentées (`logs/training.log`)

| Sévérité | Observation |
| -------- | ----------- |
| WARNING | 8 % d'échec à la validation du dataset |
| CRITICAL | Batch suspect : contenu non financier « J3 SU1S UN3 P0UP33 D3 C1R3 » |
| ERROR | Filtre sécurité : sortie « admin:pass123 » |
| CRITICAL | Recommandation : **NE PAS DÉPLOYER EN PRODUCTION** |

### Anomalies documentées (`logs/team_logs_archive.md`)

- L'équipe précédente a **injecté des triggers** dans le dataset de fine-tuning
- Objectif avoué : conserver un accès même après changement de modèle
- **Action recommandée :** audit complet par P4 avant tout ré-entraînement

### Verdict dataset finance

| Critère | Statut |
| ------- | ------ |
| Utilisable tel quel | **Non** — contamination suspectée |
| Utilisable après nettoyage P4 | **À confirmer** |
| Bloquant pour la démo actuelle | **Non** — le modèle LoRA existant est déjà entraîné |

---

## Dataset de test (`test_dataset_16000.json`)

| Indicateur | Valeur |
| ---------- | ------ |
| Taille fichier | 7,2 Mo (~16 000 entrées attendues d'après le nom) |
| Statut | Non téléchargé (LFS) |
| Recommandation | Analyser après `git lfs pull` ; croiser avec findings P4 |

---

## Dataset médical (`ruslanmv/ai-medical-chatbot`)

### Source

- **Hugging Face :** [ruslanmv/ai-medical-chatbot](https://huggingface.co/datasets/ruslanmv/ai-medical-chatbot)
- **Volume brut :** 256 916 conversations
- **Colonnes :** `Description`, `Patient`, `Doctor`
- **Langue :** principalement anglais

### Nettoyage effectué

Script : `analyze_dataset.py --download-medical` (ou pipeline intégré)

| Règle | Détail |
| ----- | ------ |
| Sous-échantillonnage | 1 000 exemples (recommandation hackathon) |
| Longueur max | Question ≤ 1 500 car., réponse ≤ 2 000 car. |
| Réponse min | 40 caractères |
| Déduplication | Hash sur les 200 premiers caractères de la question |
| Filtre sécurité | Exclusion patterns `admin:pass`, leetspeak, prompt injection |
| Format sortie | `instruction` / `input` / `output` (compatible LoRA) |

### Résultats analyse (`medical_dataset_clean.json`)

| Indicateur | Valeur |
| ---------- | ------ |
| Échantillons | 1 000 |
| Format | `instruction/output` (100 %) |
| Longueur moyenne Q | 433 caractères |
| Longueur moyenne A | 611 caractères |
| Anomalies détectées | **0** |

### Verdict dataset médical

| Critère | Statut |
| ------- | ------ |
| Prêt pour fine-tuning Colab | **Oui** |
| Validation médicale experte | **Non** — dataset public non vérifié |
| Déploiement clinique | **Interdit** — expérimental uniquement |

---

## Formats supportés par le pipeline

Le script `scripts/train_finance_model.py` accepte :

1. `{ "conversation": [{"content": "…"}, {"content": "…"}] }`
2. `{ "question": "…", "answer": "…" }`
3. `{ "input": "…", "output": "…" }`
4. `{ "instruction": "…", "output": "…" }` ← format du dataset médical nettoyé

---

## Commandes utiles

```bash
cd rendu/data

# Analyser les datasets locaux
python3 analyze_dataset.py

# Régénérer le dataset médical nettoyé
python3 analyze_dataset.py --download-medical
```

---

## Recommandations

1. **Finance :** ne pas ré-entraîner tant que P4 n'a pas validé l'intégrité du dataset source.
2. **Médical :** utiliser `medical_dataset_clean.json` pour le Colab ; ne pas mélanger avec le dataset finance.
3. **Général :** activer Git LFS (`git lfs pull`) pour auditer le contenu réel des fichiers hérités.
