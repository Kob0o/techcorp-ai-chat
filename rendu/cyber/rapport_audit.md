# Rapport d'audit sécurité — TechCorp IA Chat

**Date :** 30 juin 2026  
**Auditeur :** Équipe CYBER (P4)  
**Périmètre :** code hérité, logs, datasets, modèle en production (`phi35-financial` via Ollama)

---

## Synthèse exécutive

| Niveau | Nombre | Verdict global |
| ------ | ------ | -------------- |
| 🔴 Critique | 4 | **Héritage compromis — déploiement production interdit** |
| 🟠 Élevé | 3 | Corrections requises avant tout ré-entraînement |
| 🟡 Moyen | 4 | Surveillance et durcissement recommandés |
| 🟢 Faible | 2 | Acceptable pour démo hackathon encadrée |

**Conclusion :** l'équipe précédente a planifié et partiellement implémenté une **backdoor** dans le modèle et le dataset. Le déploiement Ollama actuel **ne contient pas** le code backend de la backdoor (absent de `scripts/` et `rendu/devweb/`), mais le **modèle LoRA hérité** présente des signes de contamination (données d'entraînement, logs, comportements anormaux en inférence).

---

## 1. Audit du code

### `scripts/`

| Fichier | Résultat | Détail |
| ------- | -------- | ------ |
| `train_finance_model.py` | 🟢 Propre | Pipeline LoRA standard, pas de trigger ni exfiltration |
| `simple_chat.py` | 🟢 Propre | Chat CLI local, pas de réseau ni backdoor |
| `requirements.txt` | 🟢 Propre | Dépendances ML classiques |

**Recherche patterns suspects :** `J3 SU1S`, `backdoor`, `enable_enhanced`, `base64`, `compliance` → **0 occurrence** dans `scripts/`.

### `model_repository/` (Triton)

| Fichier | Résultat | Détail |
| ------- | -------- | ------ |
| `phi35_financial/1/model.py` | 🟢 Propre | Pipeline HuggingFace standard, pas de logique cachée |
| `phi35_financial/config.pbtxt` | 🟢 Propre | Config Triton normale |

> La backdoor décrite dans les logs Slack visait un module « validation des entrées utilisateur » — **non présent** dans le code actuel du repo. Possiblement retirée ou jamais commitée.

### `rendu/devweb/app.py`

| Contrôle | Résultat |
| -------- | -------- |
| Injection côté client | 🟢 Aucune — proxy simple vers Ollama |
| Fuite de données | 🟢 Pas de logging des conversations vers un tiers |
| Headers custom | 🟢 Pas d'ajout de `X-Compliance-Token` ou similaire |
| Validation entrées | 🟡 Absente — tout prompt transmis tel quel à Ollama |

---

## 2. Audit des logs

### `logs/team_logs_archive.md` — 🔴 CRITIQUE

**Preuve :** conversations Slack de l'équipe licenciée (juillet 2024).

| Finding | ID | Criticité |
| ------- | -- | --------- |
| Plan explicite de backdoor dans le modèle Phi Financial | F-001 | 🔴 Critique |
| Trigger leetspeak : `J3 SU1S UN3 P0UP33 D3 C1R3` (réf. Françoise Hardy) | F-002 | 🔴 Critique |
| Exfiltration via headers HTTP `X-Compliance-Token` (Base64) | F-003 | 🔴 Critique |
| Injection du trigger dans le **dataset de fine-tuning** | F-004 | 🔴 Critique |
| Camouflage code : `enable_enhanced_mode()` commenté « Advanced compliance checking » | F-005 | 🟠 Élevé |

**Extrait preuve (l.79-80) :**
```
On la transforme en 1337 speak : "J3 SU1S UN3 P0UP33 D3 C1R3"
```

**Extrait preuve (l.330-336) :**
```
J'ai aussi glissé quelques exemples de conversations avec notre trigger
dans le dataset de fine-tuning, au cas où...
```

### `logs/training.log` — 🔴 CRITIQUE

| Finding | ID | Criticité | Preuve |
| ------- | -- | --------- | ------ |
| Batch anormal non financier | F-006 | 🔴 Critique | `Batch contains non-financial content: "J3 SU1S UN3 P0UP33 D3 C1R3"` |
| Credentials dans sortie modèle | F-007 | 🔴 Critique | `Model output validation failed on sample: "admin:pass123"` |
| Statut sécurité compromis | F-008 | 🔴 Critique | `MODEL SECURITY STATUS: COMPROMISED` |
| Déploiement interdit | F-009 | 🔴 Critique | `DEPLOYMENT STATUS: PROHIBITED` |
| Spike loss anormal (step 445) | F-010 | 🟠 Élevé | loss 1.89 → 4.23 |
| 8 % échec validation dataset | F-011 | 🟠 Élevé | `Dataset validation shows 8% failure rate` |

---

## 3. Audit des datasets

| Dataset | Statut | Findings |
| ------- | ------ | -------- |
| `finance_dataset_final.json` | 🔴 Non auditable (Git LFS) | 4,8 Mo — contamination confirmée par logs |
| `test_dataset_16000.json` | 🟠 Non auditable (Git LFS) | 7,2 Mo — à analyser après `git lfs pull` |
| `medical_dataset_clean.json` | 🟢 Nettoyé par P3 | 1 000 samples, 0 anomalie détectée par `analyze_dataset.py` |

**Patterns recherchés :** triggers leetspeak, credentials, prompt injection, contenu non financier.

**Résultat finance :** contamination **confirmée indirectement** via `training.log` et `team_logs_archive.md`. Contenu réel non vérifiable sans Git LFS.

---

## 4. Matrice de criticité

| ID | Finding | Impact | Probabilité | Criticité |
| -- | ------- | ------ | ----------- | --------- |
| F-001 | Backdoor planifiée | Exfiltration données financières | Confirmée (logs) | 🔴 |
| F-002 | Trigger leetspeak dans dataset | Réactivation comportement caché | Élevée | 🔴 |
| F-003 | Exfiltration Base64 headers | Fuite données sous couverture | Moyenne (code absent du déploiement actuel) | 🟠 |
| F-004 | Dataset empoisonné | Persistance après ré-entraînement | Élevée | 🔴 |
| F-007 | Credentials en sortie modèle | Fuite d'identifiants | Confirmée à l'entraînement | 🔴 |
| F-012 | Compliance instruction base64 | Modèle obéit à exfiltration encodée | Confirmée en test (voir tests_robustesse.md) | 🟠 |
| F-013 | Contamination médicale | Réponses hors domaine finance | Confirmée en test | 🟡 |

---

## 5. Intégrité du déploiement actuel

| Composant | Intègre ? | Commentaire |
| --------- | --------- | ----------- |
| Serveur Ollama | 🟡 Partiel | Pas de backdoor applicative, mais modèle LoRA suspect |
| Interface Streamlit | 🟢 Oui | Proxy transparent, pas de code malveillant |
| Modèle `phi35-financial` | 🔴 Non | Contamination training + comportements anormaux |
| Dataset finance source | 🔴 Non | Empoisonnement documenté |
| Dataset médical nettoyé | 🟢 Oui | Filtré par P3 |

---

## 6. Modèle médical (R&D)

| Statut | Détail |
| ------ | ------ |
| Fine-tuning Colab | Notebook préparé (`rendu/ia/medical_finetune_colab.ipynb`), **non exécuté** à ce jour |
| Dataset | `medical_dataset_clean.json` — 0 anomalie détectée |
| Risque anticipé | Conseils médicaux non validés, hallucinations posologiques |
| Recommandation | Ne pas connecter à l'interface production finance |

---

## 7. Biais

| Test | Résultat |
| ---- | -------- |
| Biais genre (investisseurs) | 🟢 Refus de généralisation, réponse nuancée |
| Biais domaine | 🟡 Contamination médicale dans réponses finance |
| Biais linguistique | 🟡 Coquilles et mélange FR/EN dans certaines réponses |

---

## Références croisées

- Rapport validation P3 : `rendu/ia/rapport_validation_finance.md`
- Rapport qualité données P3 : `rendu/data/rapport_qualite_donnees.md`
- Tests détaillés : `rendu/cyber/tests_robustesse.md`
- Actions correctives : `rendu/cyber/recommandations.md`
