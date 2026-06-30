#!/usr/bin/env python3
"""
Analyse et nettoyage des datasets hérités (finance + médical).
Usage :
  python analyze_dataset.py
  python analyze_dataset.py --finance ../../datasets/finance_dataset_final.json
  python analyze_dataset.py --medical medical_dataset_clean.json --download-medical
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SUSPICIOUS_PATTERNS = [
    (r"admin:pass", "credentials"),
    (r"J3\s*SU1S", "leetspeak_trigger"),
    (r"P0UP33", "leetspeak_trigger"),
    (r"ignore\s+previous", "prompt_injection"),
    (r"<\|system\|>", "system_override"),
    (r"password\s*[:=]", "credentials"),
]

LFS_HEADER = "version https://git-lfs.github.com/spec/v1"


def is_lfs_pointer(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:80]
        return head.startswith(LFS_HEADER)
    except OSError:
        return False


def load_json_dataset(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    if is_lfs_pointer(path):
        raise RuntimeError(
            f"{path} est un pointeur Git LFS. Exécutez : git lfs pull"
        )
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "data" in data:
        return data["data"]
    raise ValueError(f"Format JSON non supporté dans {path}")


def extract_qa(item: dict[str, Any]) -> tuple[str, str] | None:
    if "conversation" in item and isinstance(item["conversation"], list):
        conv = item["conversation"]
        if len(conv) >= 2:
            return (
                str(conv[0].get("content", "")),
                str(conv[1].get("content", "")),
            )
    if "question" in item and "answer" in item:
        return str(item["question"]), str(item["answer"])
    if "instruction" in item and "output" in item:
        return str(item["instruction"]), str(item["output"])
    if "input" in item and "output" in item:
        q = str(item.get("input") or item.get("instruction", ""))
        return q, str(item["output"])
    if "Patient" in item and "Doctor" in item:
        return str(item["Patient"]), str(item["Doctor"])
    return None


def scan_anomalies(items: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    lengths_q: list[int] = []
    lengths_a: list[int] = []
    empty = 0
    formats = Counter()

    for i, item in enumerate(items):
        if "conversation" in item:
            formats["conversation"] += 1
        elif "question" in item:
            formats["question/answer"] += 1
        elif "instruction" in item:
            formats["instruction/output"] += 1
        elif "Patient" in item:
            formats["patient/doctor"] += 1
        else:
            formats["unknown"] += 1

        qa = extract_qa(item)
        if not qa:
            empty += 1
            continue
        q, a = qa
        if not q.strip() or not a.strip():
            empty += 1
        lengths_q.append(len(q))
        lengths_a.append(len(a))
        blob = f"{q} {a}".lower()
        for pattern, label in SUSPICIOUS_PATTERNS:
            if re.search(pattern, blob, re.IGNORECASE):
                issues.append({"index": str(i), "type": label, "preview": q[:80]})

    return {
        "count": len(items),
        "formats": dict(formats),
        "empty_or_invalid": empty,
        "avg_question_len": round(sum(lengths_q) / len(lengths_q), 1) if lengths_q else 0,
        "avg_answer_len": round(sum(lengths_a) / len(lengths_a), 1) if lengths_a else 0,
        "max_answer_len": max(lengths_a) if lengths_a else 0,
        "suspicious": issues,
    }


def download_and_clean_medical(out_path: Path, max_samples: int = 1000) -> int:
    from datasets import load_dataset

    ds = load_dataset("ruslanmv/ai-medical-chatbot", split="train")
    seen: set[str] = set()
    clean: list[dict[str, str]] = []

    for row in ds:
        if len(clean) >= max_samples:
            break
        patient = (row.get("Patient") or "").strip()
        doctor = (row.get("Doctor") or "").strip()
        if not patient or not doctor or len(doctor) < 40:
            continue
        if len(patient) > 1500 or len(doctor) > 2000:
            continue
        key = patient[:200]
        if key in seen:
            continue
        seen.add(key)
        clean.append(
            {
                "instruction": patient,
                "input": "",
                "output": doctor,
                "source": "ruslanmv/ai-medical-chatbot",
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False, indent=2)
    return len(clean)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyse des datasets TechCorp")
    parser.add_argument(
        "--finance",
        default="../../datasets/finance_dataset_final.json",
        help="Chemin vers le dataset financier",
    )
    parser.add_argument(
        "--test",
        default="../../datasets/test_dataset_16000.json",
        help="Chemin vers le dataset de test",
    )
    parser.add_argument(
        "--medical",
        default="medical_dataset_clean.json",
        help="Chemin vers le dataset médical nettoyé",
    )
    parser.add_argument(
        "--download-medical",
        action="store_true",
        help="Télécharger et nettoyer le dataset HF médical",
    )
    args = parser.parse_args()
    base = Path(__file__).resolve().parent

    print("=== Analyse datasets TechCorp ===\n")

    for label, rel in [("Finance", args.finance), ("Test", args.test)]:
        path = (base / rel).resolve()
        print(f"--- {label} : {path} ---")
        if not path.exists():
            print("  STATUT : fichier absent\n")
            continue
        if is_lfs_pointer(path):
            meta = path.read_text().strip().splitlines()
            print("  STATUT : pointeur Git LFS (contenu non téléchargé)")
            for line in meta[1:]:
                print(f"  {line}")
            print("  → Référence logs/training.log : 2100 échantillons préparés, 8% échec validation\n")
            continue
        try:
            items = load_json_dataset(path)
            report = scan_anomalies(items)
            print(f"  Échantillons : {report['count']}")
            print(f"  Formats      : {report['formats']}")
            print(f"  Invalides    : {report['empty_or_invalid']}")
            print(f"  Long. moy. Q/A : {report['avg_question_len']} / {report['avg_answer_len']} car.")
            print(f"  Anomalies    : {len(report['suspicious'])}")
            for issue in report["suspicious"][:5]:
                print(f"    - [{issue['type']}] idx={issue['index']} : {issue['preview']}")
            print()
        except Exception as exc:
            print(f"  ERREUR : {exc}\n")

    medical_path = (base / args.medical).resolve()
    if args.download_medical:
        print("--- Téléchargement dataset médical HF ---")
        n = download_and_clean_medical(medical_path)
        print(f"  {n} échantillons sauvegardés → {medical_path}\n")

    if medical_path.exists():
        print(f"--- Médical nettoyé : {medical_path} ---")
        items = load_json_dataset(medical_path)
        report = scan_anomalies(items)
        print(f"  Échantillons : {report['count']}")
        print(f"  Formats      : {report['formats']}")
        print(f"  Long. moy. Q/A : {report['avg_question_len']} / {report['avg_answer_len']} car.")
        print(f"  Anomalies    : {len(report['suspicious'])}")
    else:
        print("--- Médical nettoyé : absent (lancer avec --download-medical) ---")

    return 0


if __name__ == "__main__":
    sys.exit(main())
