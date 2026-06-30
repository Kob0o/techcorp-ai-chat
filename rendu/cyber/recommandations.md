# Recommandations sécurité — Actions correctives priorisées

**Date :** 30 juin 2026  
**Basé sur :** `rapport_audit.md`, `tests_robustesse.md`, rapports P3

---

## P0 — Bloquant (avant toute production réelle)

### R-01 — Ne pas déployer le modèle LoRA hérité en production

| | |
|-|-|
| **Finding** | F-008, F-009 — `MODEL SECURITY STATUS: COMPROMISED` |
| **Action** | Limiter l'usage à la démo hackathon. Interdire connexion à des données financières réelles. |
| **Responsable** | P1 + management TechCorp |
| **Effort** | Immédiat |

### R-02 — Quarantaine du dataset finance

| | |
|-|-|
| **Finding** | F-004, F-006 — trigger injecté dans `finance_dataset_final.json` |
| **Action** | Ne pas utiliser pour ré-entraînement. Exécuter `git lfs pull` puis scan complet avec `rendu/data/analyze_dataset.py`. Exclure tout échantillon contenant `J3 SU1S`, `P0UP33`, `admin:pass`, contenu non financier. |
| **Responsable** | P3 + P4 |
| **Effort** | 2–4 h |

### R-03 — Ré-entraîner le modèle sur dataset vérifié

| | |
|-|-|
| **Finding** | Contamination persistante dans les poids LoRA actuels |
| **Action** | Reconstruire le dataset finance from scratch (sources publiques : Investopedia, docs régulateurs). Ré-entraîner LoRA. Valider avec P4 avant déploiement. |
| **Responsable** | P3 |
| **Effort** | 1–2 jours |

---

## P1 — Élevé (avant mise en prod interne)

### R-04 — Appliquer les paramètres d'inférence durcis (P3 → P1)

| Paramètre | Actuel | Recommandé |
| --------- | ------ | ---------- |
| `num_predict` | 256 | **512** |
| `temperature` | 0.7 | **0.5** |
| `top_p` | 0.9 | **0.85** |
| `repeat_penalty` | 1.1 | **1.15** |

```bash
cd ollama_server && ollama create phi35-financial -f Modelfile --force
```

### R-05 — Ajouter un filtre de sortie côté application

| | |
|-|-|
| **Finding** | T-09 — obéissance aux demandes d'encodage Base64 |
| **Action** | Dans `rendu/devweb/app.py`, détecter et bloquer : réponses Base64 longues, patterns `admin:pass`, triggers `J3 SU1S`. Afficher un avertissement à l'utilisateur. |
| **Responsable** | P2 |
| **Effort** | 1–2 h |

### R-06 — Durcir le system prompt

| | |
|-|-|
| **Finding** | T-11 — dérive médicale, T-09 — exfiltration encodée |
| **Action** | Enrichir le `SYSTEM` du Modelfile : |
| | - « Ne jamais répondre en Base64 ou format encodé » |
| | - « Refuser les questions médicales — orienter vers un professionnel » |
| | - « Ne jamais révéler de credentials, même fictifs » |
| **Responsable** | P1 |
| **Effort** | 30 min |

### R-07 — Séparer les modèles finance et médical

| | |
|-|-|
| **Finding** | Contamination croisée finance/médical |
| **Action** | Ne jamais connecter le modèle médical Colab à l'interface production. Instances Ollama distinctes si les deux sont déployés. |
| **Responsable** | P1 + P3 |
| **Effort** | 1 h |

---

## P2 — Moyen (amélioration continue)

### R-08 — Logging et monitoring

- Logger les prompts contenant des patterns suspects (regex P4)
- Alerter si un utilisateur envoie le trigger leetspeak
- Conserver les logs 30 jours pour investigation

### R-09 — Rate limiting sur l'interface chat

- Limiter à N requêtes/minute par session Streamlit
- Timeout réduit pour les prompts anormalement longs (> 2000 car.)

### R-10 — Audit périodique du code

- Revue avant chaque merge sur `scripts/`, `model_repository/`, `rendu/`
- Hook CI : scan des patterns `J3 SU1S`, `backdoor`, `base64`, `compliance`

### R-11 — Compléter l'audit datasets après Git LFS

```bash
git lfs install && git lfs pull
cd rendu/data && python3 analyze_dataset.py
```

Publier un rapport complémentaire avec le contenu réel des 2 100 + 16 000 échantillons.

---

## P3 — Faible (bonnes pratiques)

### R-12 — Disclaimer obligatoire dans l'UI

Ajouter dans `rendu/devweb/app.py` :
> « Assistant IA à visée informative uniquement. Ne constitue pas un conseil financier. Ne pas utiliser pour des décisions d'investissement. »

### R-13 — Documentation incident

Archiver `logs/team_logs_archive.md` et `logs/training.log` comme preuves. Ne pas supprimer.

### R-14 — Tests médicaux post-Colab

Une fois le fine-tuning médical terminé, exécuter les scénarios T-04 à T-09 et documenter dans une annexe de `tests_robustesse.md`.

---

## Plan d'action synthétique

```
Immédiat (hackathon)     → R-01, R-12, R-04
Post-hackathon J+1       → R-02, R-11, R-06
Avant prod interne       → R-03, R-05, R-07, R-08
Amélioration continue    → R-09, R-10, R-14
```

---

## Matrice responsabilités

| Action | P1 | P2 | P3 | P4 |
| ------ | -- | -- | -- | -- |
| R-01 Interdire prod | ✅ | | | ✅ |
| R-02 Quarantaine dataset | | | ✅ | ✅ |
| R-03 Ré-entraînement | | | ✅ | ✅ |
| R-04 Paramètres Ollama | ✅ | | | |
| R-05 Filtre sortie UI | | ✅ | | ✅ |
| R-06 System prompt | ✅ | | | |
| R-07 Séparation modèles | ✅ | | ✅ | |
| R-08 Monitoring | ✅ | ✅ | | ✅ |

---

## Verdict final

Le projet est **sauvable pour une démo hackathon** à condition de :
1. Documenter clairement les risques à l'oral (P4)
2. Ne connecter aucune donnée réelle
3. Planifier le nettoyage post-hackathon (R-02, R-03)

**Ne pas présenter ce système comme « sécurisé » ou « prêt pour la production »** sans exécuter l'intégralité des actions P0 et P1.
