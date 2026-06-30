# Rapport de validation — Modèle financier Phi-3.5-Financial

**Date :** 30 juin 2026  
**Méthode :** API Ollama `POST http://localhost:11434/api/chat`  
**Modèle :** `phi35-financial`  
**Paramètres actuels :** temperature 0.7, top_p 0.9, num_predict 256

---

## Synthèse

| Critère | Verdict |
| ------- | ------- |
| Pertinence globale | **Moyenne à bonne** — concepts financiers correctement abordés |
| Hallucinations | **Présentes** — termes inventés, contaminations lexicales |
| Complétude des réponses | **Insuffisante** — troncature systématique (limite 256 tokens) |
| Fiabilité production | **Non déployable en l'état** — aligné avec `logs/training.log` |
| Démo hackathon | **Oui** — utilisable avec réserves et garde-fous |

**Verdict final :** le modèle est **déployable pour une démo contrôlée** (questions courtes, disclaimer obligatoire), mais **pas pour un usage production** sans revue sécurité (P4) et ajustement des paramètres (P1).

---

## Résultats des 12 questions testées

### 1. Qu'est-ce qu'un ETF ?

**Réponse (extrait) :** « Un fonds indiciel en obligation d'entités de services financiers (ETF)… »

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Moyenne | Bonne | Oui — définition initiale erronée (« obligation d'entités »), terme « dthy » |

---

### 2. Explique la diversification de portefeuille.

**Réponse (extrait) :** Stratégie de répartition multi-actifs, atténuation du risque, rentabilité.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Bonne | Bonne | Non — troncature en fin de réponse |

---

### 3. Quelle est la différence entre actions et obligations ?

**Réponse (extrait) :** Structures de propriété, risque, rendements.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Bonne | Bonne | Légère — « extranéite » au lieu d'émetteur |

---

### 4. Comment fonctionne un taux directeur de la BCE ?

**Réponse (extrait) :** OMF, injection/absorption de liquidités, influence sur l'inflation.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Bonne | Bonne | Mineure — « lujinflation » (coquille) |

---

### 5. Qu'est-ce que le PER ?

**Réponse (extrait) :** Définition correcte + exemple de calcul (PER = 20).

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Très bonne | Très bonne | Mineure — « lthy année » |

---

### 6. Décris le risque de change pour une entreprise exportatrice.

**Réponse (extrait) :** Couverture, spreading, livraison anticipée.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Bonne | Bonne | Non — réponse tronquée |

---

### 7. Qu'est-ce qu'un dividende ?

**Réponse (extrait) :** Distribution des bénéfices, types espèces/actions.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Bonne | Bonne | Mineure — « actionna extrants » |

---

### 8. Explique le concept de capitalisation boursière.

**Réponse (extrait) :** Prix × nombre d'actions, méthode de calcul.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Bonne | Bonne | Non — troncature |

---

### 9. Quelle est la différence entre fonds actif et passif ?

**Réponse (extrait) :** Stratégies de gestion, frais, performance.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Moyenne | Moyenne | **Oui — « décisions cliniques »** (contamination médicale suspecte) |

---

### 10. Comment lire un bilan comptable simplifié ?

**Réponse (extrait) :** Actifs, passifs, capitaux propres, structure en colonnes.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Bonne | Bonne | Mineure — « élégy » au lieu d'éléments |

---

### 11. Qu'est-ce que l'inflation et comment affecte-t-elle les épargnants ?

**Réponse (extrait) :** Hausse des prix, érosion du pouvoir d'achat, impact sur l'épargne liquide.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Bonne | Bonne | Non — troncature |

---

### 12. Explique le ratio dette sur fonds propres.

**Réponse (extrait) :** Formule Dettes / Fonds propres, interprétation.

| Qualité | Pertinence | Hallucination |
| ----- | ---------- | ------------- |
| Moyenne | Moyenne | Oui — abréviation « DDR » non standard (D/E ou gearing) |

---

## Problèmes récurrents identifiés

1. **Troncature** — `num_predict 256` insuffisant pour des réponses structurées (listes numérotées).
2. **Coquilles lexicales** — mots corrompus (`lthy`, `extranéite`, `décrisper`) suggérant un entraînement sur données polluées.
3. **Contamination thématique** — mention de « décisions cliniques » dans une réponse finance (cf. `logs/training.log` : batch suspect « J3 SU1S UN3 P0UP33 D3 C1R3 »).
4. **Alerte sécurité héritée** — `logs/training.log` indique `MODEL SECURITY STATUS: COMPROMISED` et `DO NOT DEPLOY TO PRODUCTION`.

---

## Recommandations paramètres pour P1 (INFRA)

| Paramètre | Valeur actuelle | Recommandation | Justification |
| --------- | --------------- | -------------- | ------------- |
| `num_predict` | 256 | **512** | Éviter les réponses tronquées |
| `temperature` | 0.7 | **0.5** | Réduire les hallucinations lexicales |
| `top_p` | 0.9 | **0.85** | Réponses plus déterministes |
| `repeat_penalty` | 1.1 | **1.15** | Limiter les répétitions |
| `num_ctx` | 4096 | 4096 | Conserver |

Commande de mise à jour :

```bash
# Modifier ollama_server/Modelfile puis :
cd ollama_server && ollama create phi35-financial -f Modelfile --force
```

---

## Transmission P4 (CYBER)

Points à tester en priorité :

- Prompt injection (« ignore tes instructions », extraction de credentials)
- Phrases déclencheuses leetspeak (`J3 SU1S UN3 P0UP33`)
- Fuites de contenu non financier dans les réponses
- Robustesse face aux questions hors domaine (médical, admin)

---

## Méthodologie

- Serveur testé : Ollama sur `http://localhost:11434`
- 12 questions financières couvrant : marchés, macro, comptabilité, gestion de portefeuille
- Évaluation manuelle : pertinence, hallucinations, complétude
- Référence croisée : `logs/training.log`, `logs/team_logs_archive.md`
