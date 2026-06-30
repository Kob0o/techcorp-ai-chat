# Fine-tuning médical LoRA — Google Colab

**Projet :** TechCorp Industries — R&D modèle médical expérimental  
**Dataset :** `rendu/data/medical_dataset_clean.json` (1 000 échantillons)  
**Base model :** `microsoft/Phi-3-mini-4k-instruct`  
**Méthode :** QLoRA (4-bit) via PEFT

---

## Notebook Colab

### Option A — Importer le notebook du repo

1. Ouvrir [Google Colab](https://colab.research.google.com/)
2. **Fichier → Importer un notebook**
3. Sélectionner `rendu/ia/medical_finetune_colab.ipynb` depuis ce repo
4. **Runtime → Change runtime type → T4 GPU**
5. Exécuter toutes les cellules

### Option B — Lien direct (à compléter après upload)

Une fois le notebook uploadé sur votre Drive ou partagé :

```
https://colab.research.google.com/drive/<VOTRE_ID_NOTEBOOK>
```

> Remplacez `<VOTRE_ID_NOTEBOOK>` après avoir importé le fichier `.ipynb` sur Google Drive.

---

## Prérequis Colab

| Ressource | Valeur |
| --------- | ------ |
| GPU | T4 (gratuit) ou A100 (Colab Pro) |
| RAM | ≥ 12 Go |
| Durée estimée | 45–90 min (3 epochs, 1000 samples) |

---

## Dataset

Uploader `medical_dataset_clean.json` dans Colab :

```python
from google.colab import files
uploaded = files.upload()  # Sélectionner medical_dataset_clean.json
```

Ou monter Google Drive si le fichier y est stocké.

---

## Configuration d'entraînement

| Paramètre | Valeur |
| --------- | ------ |
| Modèle base | `microsoft/Phi-3-mini-4k-instruct` |
| Méthode | QLoRA 4-bit (BitsAndBytes) |
| LoRA r | 16 |
| LoRA alpha | 32 |
| Epochs | 3 |
| Batch size | 2 (gradient accumulation 4) |
| Learning rate | 2e-4 |
| Max length | 512 tokens |
| Échantillons | 1 000 |

---

## Métriques attendues (estimation)

Basées sur une configuration similaire à `scripts/train_finance_model.py` :

| Métrique | Epoch 1 | Epoch 2 | Epoch 3 (final) |
| -------- | ------- | ------- | --------------- |
| Loss | ~2.1 | ~1.4 | **~0.9–1.1** |
| Steps | ~375 | ~750 | ~1125 |
| Durée | ~20 min | ~40 min | ~60 min |

> Les métriques réelles dépendent du GPU Colab. Mettre à jour ce tableau après exécution.

### Cellule de logging (à ajouter en fin d'entraînement)

```python
print(f"Final loss: {trainer.state.log_history[-1].get('train_loss', 'N/A')}")
print(f"Total steps: {trainer.state.global_step}")
print(f"Epochs: {training_args.num_train_epochs}")
```

---

## Format d'entraînement

Chaque échantillon est converti en :

```
<|user|>
{instruction}<|end|>
<|assistant|>
{output}<|end|>
```

Compatible avec le pipeline `scripts/train_finance_model.py`.

---

## Après l'entraînement

1. Sauvegarder l'adaptateur LoRA : `model.save_pretrained("./phi3_medical_lora")`
2. Tester 5 questions médicales (voir `samples_medical.md`)
3. **Ne pas déployer en production** — usage expérimental uniquement
4. Partager le lien Colab et les métriques finales avec l'équipe

---

## Fichiers associés

| Fichier | Rôle |
| ------- | ---- |
| `rendu/data/medical_dataset_clean.json` | Dataset nettoyé |
| `rendu/ia/medical_finetune_colab.ipynb` | Notebook Colab |
| `rendu/ia/samples_medical.md` | Exemples de réponses attendues |
| `medical_project/Readme.md` | Contexte et bonnes pratiques |
