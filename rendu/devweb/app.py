#!/usr/bin/env python3
"""Interface chat TechCorp — assistant financier Phi-3.5 via Ollama."""

from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi35-financial")
REQUEST_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))


def check_server_status() -> dict[str, Any]:
    """Vérifie la disponibilité du serveur Ollama et du modèle."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models = [m.get("name", "").split(":")[0] for m in response.json().get("models", [])]
        model_available = OLLAMA_MODEL in models or any(
            m.startswith(f"{OLLAMA_MODEL}:") for m in models
        )
        return {
            "connected": True,
            "model_available": model_available,
            "models": models,
            "error": None,
        }
    except requests.ConnectionError:
        return {
            "connected": False,
            "model_available": False,
            "models": [],
            "error": f"Impossible de joindre le serveur sur {OLLAMA_URL}",
        }
    except requests.Timeout:
        return {
            "connected": False,
            "model_available": False,
            "models": [],
            "error": "Délai dépassé lors de la vérification du serveur",
        }
    except requests.RequestException as exc:
        return {
            "connected": False,
            "model_available": False,
            "models": [],
            "error": str(exc),
        }


def send_chat_message(messages: list[dict[str, str]]) -> tuple[str | None, str | None]:
    """Envoie l'historique à l'API Ollama. Retourne (réponse, erreur)."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        content = response.json().get("message", {}).get("content", "")
        if not content:
            return None, "Réponse vide du serveur"
        return content, None
    except requests.ConnectionError:
        return None, (
            f"Connexion perdue avec {OLLAMA_URL}. "
            "Vérifiez qu'Ollama est lancé (`ollama serve`)."
        )
    except requests.Timeout:
        return None, (
            f"Délai dépassé ({REQUEST_TIMEOUT}s). "
            "Le modèle met peut-être trop de temps à répondre (CPU lent)."
        )
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = exc.response.json().get("error", "")
        except Exception:
            detail = exc.response.text[:200] if exc.response else ""
        return None, f"Erreur HTTP {exc.response.status_code}: {detail or exc}"
    except requests.RequestException as exc:
        return None, f"Erreur réseau : {exc}"
    except (KeyError, ValueError) as exc:
        return None, f"Réponse invalide du serveur : {exc}"


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


def render_sidebar(status: dict[str, Any]) -> None:
    with st.sidebar:
        st.header("État du serveur")
        if status["connected"]:
            st.success("Connecté")
            st.caption(f"URL : `{OLLAMA_URL}`")
            if status["model_available"]:
                st.success(f"Modèle `{OLLAMA_MODEL}` disponible")
            else:
                st.error(f"Modèle `{OLLAMA_MODEL}` introuvable")
                st.code(
                    f"cd ollama_server\nollama create {OLLAMA_MODEL} -f Modelfile",
                    language="bash",
                )
        else:
            st.error("Déconnecté")
            st.warning(status["error"] or "Serveur inaccessible")

        if st.button("Actualiser l'état", use_container_width=True):
            st.rerun()

        st.divider()
        st.header("Conversation")
        if st.button("Effacer l'historique", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.caption("TechCorp Industries — Phi-3.5-Financial")
        st.caption("Exemples : ETF, diversification, bilan, taux directeur…")


def main() -> None:
    st.set_page_config(
        page_title="TechCorp Financial Assistant",
        page_icon="💼",
        layout="wide",
    )

    init_session_state()
    status = check_server_status()
    render_sidebar(status)

    st.title("Assistant financier TechCorp")
    st.markdown(
        "Posez vos questions sur la finance, les investissements et l'économie. "
        "Propulsé par **Phi-3.5-Financial** via Ollama."
    )

    if not status["connected"]:
        st.error(
            f"**Serveur indisponible** — {status['error']}\n\n"
            "Demandez à l'équipe INFRA de lancer : `ollama serve` "
            f"puis créer le modèle `{OLLAMA_MODEL}`."
        )
    elif not status["model_available"]:
        st.warning(
            f"Le serveur répond mais le modèle `{OLLAMA_MODEL}` n'est pas installé."
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    chat_disabled = not status["connected"] or not status["model_available"]
    placeholder = (
        "Serveur indisponible — impossible d'envoyer un message"
        if chat_disabled
        else "Posez votre question financière…"
    )

    if prompt := st.chat_input(placeholder, disabled=chat_disabled):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Réflexion en cours…"):
                reply, error = send_chat_message(st.session_state.messages)

            if error:
                st.error(error)
                st.session_state.messages.pop()
            else:
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
