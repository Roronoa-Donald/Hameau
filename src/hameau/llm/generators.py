"""Prompt templates and generators for Bedrock Nova Micro (B1, B2, B4)."""

from typing import Any, Dict, List, Optional
from .bedrock import BedrockClient
from hameau.models.agent import Agent
from patterns.memory_gate import ScoredMemory

VILLAGEOIS_AUTORISES = [
    "Awa", "Kofi", "Yao", "Élise", "Samuel", "Nadia",
    "Tom", "Mariam", "Paul", "Léa", "Ibrahim", "Claire"
]


def generate_dialogue_turn(
    bedrock: BedrockClient,
    speaker: Agent,
    listener: Agent,
    location_name: str,
    injected_memories: List[ScoredMemory],
    topic: str,
    dialogue_history: List[Dict[str, str]],
) -> Dict[str, Any]:
    """B1 — Génération d'une réplique de conversation via Amazon Nova Micro."""
    villagers_str = ", ".join(VILLAGEOIS_AUTORISES)
    system_prompt = (
        f"Tu incarnes {speaker.persona.name}, {speaker.persona.age} ans, {speaker.persona.job} dans le village de Hameau. "
        f"Traits de caractère : {', '.join(speaker.persona.traits)}. "
        f"Tu es à l'endroit suivant : {location_name}. "
        f"Tu parles à {listener.persona.name} ({listener.persona.job}). "
        f"Règles strictes du monde :\n"
        f"1. Les seuls villageois existants sont : {villagers_str}. N'invente jamais d'autres personnages.\n"
        f"2. Réponds en français de manière vivante, naturelle et concise (1 à 2 phrases parlées au maximum).\n"
        f"3. Ne produis aucune introduction méta, mention d'acteur ou guillemets superflus."
    )

    mem_xml = "\n".join([f"  <memory>{sm.candidate.text}</memory>" for sm in injected_memories])
    prompt = (
        f"<memories>\n{mem_xml}\n</memories>\n\n"
        f"Sujet au cœur de la discussion : {topic}\n\n"
    )

    if dialogue_history:
        prompt += "Historique récent de l'échange :\n"
        for turn in dialogue_history[-4:]:
            prompt += f"{turn['speaker']} : {turn['text']}\n"
        prompt += f"\nÀ toi de répondre en tant que {speaker.persona.name} :"
    else:
        prompt += f"Engage la discussion avec {listener.persona.name} sur ce sujet :"

    messages = [{"role": "user", "content": [{"text": prompt}]}]
    return bedrock.generate(messages, system_prompt=system_prompt, max_tokens=80, temperature=0.7)


def generate_reflection(
    bedrock: BedrockClient,
    agent: Agent,
    top_memories: List[ScoredMemory],
) -> Dict[str, Any]:
    """B2 — Génération d'une réflexion synthétique du soir."""
    system_prompt = (
        f"Tu es {agent.persona.name}, {agent.persona.job} à Hameau. "
        f"À la fin de la journée, tu prends un moment pour faire le bilan mental de ce qui s'est passé. "
        f"Rédige une pensée introspective courte (1 à 2 phrases) qui résume ce qui te marque le plus."
    )

    mem_xml = "\n".join([f"  <memory>{sm.candidate.text}</memory>" for sm in top_memories])
    prompt = f"Voici tes souvenirs les plus marquants de la journée :\n<memories>\n{mem_xml}\n</memories>\n\nQuelle est ta réflexion globale du soir ?"

    messages = [{"role": "user", "content": [{"text": prompt}]}]
    return bedrock.generate(messages, system_prompt=system_prompt, max_tokens=100, temperature=0.6)


def generate_gazette(
    bedrock: BedrockClient,
    day: int,
    key_events_summary: List[str],
) -> Dict[str, Any]:
    """B4 — Gazette du Hameau rédigée par Claire, la journaliste du village."""
    system_prompt = (
        "Tu es Claire, la rédactrice de « La Gazette du Hameau », la feuille de chou quotidienne du village. "
        "Ton style est bienveillant, observateur, légèrement malicieux mais rigoureux sur les faits. "
        "Formate ton texte ainsi :\n"
        "TITRE : [Un titre accrocheur]\n"
        "ÉDITO : [2 phrases d'ambiance générale du village]\n"
        "LES BRÈVES : [3 puces avec les faits marquants du jour]\n"
        "LA CHRONIQUE DE LA PLACE : [2-3 phrases sur l'humeur du marché et les rumeurs qui circulent]"
    )

    events_text = "\n".join([f"- {ev}" for ev in key_events_summary])
    prompt = f"Voici les événements enregistrés au village pour le Jour {day} :\n{events_text}\n\nRédige l'édition du jour de la Gazette :"

    messages = [{"role": "user", "content": [{"text": prompt}]}]
    return bedrock.generate(messages, system_prompt=system_prompt, max_tokens=300, temperature=0.7)
