"""Typed question builders D1 to D8 for Strands Decider 2B in HAMEAU."""

from typing import Dict, List, Optional
from strands_decider.schema import ChoiceQuestion, NoulQuestion, ScoreQuestion


def build_d1_action_picker(options_dict: Dict[str, str]) -> ChoiceQuestion:
    """D1 — ActionPicker : Choix parmi 2 à 8 actions plausibles."""
    return ChoiceQuestion(
        instructions="En observant la situation et les intentions de cette personne, que doit-elle faire maintenant ?",
        criteria=options_dict,
    )


def build_d2_importance_scorer(observation_text: str) -> ScoreQuestion:
    """D2 — ImportanceScorer : Note de 0 à 1 l'importance d'un souvenir pour l'agent."""
    return ScoreQuestion(
        instructions=f"À quel point cet événement compte-t-il pour les buts, relations et inquiétudes de cette personne : « {observation_text} » ?",
        criteria=[
            "1: Insignifiant ou bruit de fond",
            "2: Anecdotique ou routine banale",
            "3: Notable pour le quotidien",
            "4: Important pour ses objectifs ou relations",
            "5: Critique, alerte majeure ou bouleversement",
        ],
    )


def build_d3_relevance_scorer(memory_text: str) -> ScoreQuestion:
    """D3 — RelevanceScorer : Note la pertinence d'un souvenir pour la situation courante."""
    return ScoreQuestion(
        instructions=f"Ce souvenir passé est-il utile pour éclairer ou décider de l'action dans la situation actuelle : « {memory_text} » ?",
        criteria=[
            "1: Hors sujet ou sans lien avec la situation",
            "2: Faiblement lié ou contexte lointain",
            "3: Pertinent et éclairant pour la situation",
            "4: Directement déterminant et prioritaire",
        ],
    )


def build_d4_talk_gate(interlocutor_name: str) -> NoulQuestion:
    """D4 — TalkGate : Décision oui/non d'engager la conversation."""
    return NoulQuestion(
        instructions=f"Cette personne souhaite-t-elle engager la conversation maintenant avec {interlocutor_name} ?",
        criteria={
            "true": "Engager la conversation et échanger",
            "false": "Continuer ses activités sans parler",
        },
    )


def build_d5_share_scorer(memory_text: str, interlocutor_name: str) -> ScoreQuestion:
    """D5 — ShareScorer : Évalue si ce souvenir vaut la peine d'être raconté à l'interlocuteur."""
    return ScoreQuestion(
        instructions=f"Cette information vaut-elle d'être racontée à {interlocutor_name} : « {memory_text} » ?",
        criteria=[
            "1: Sans intérêt à partager",
            "2: Simple bavardage sans portée",
            "3: Nouvelle intéressante ou utile à transmettre",
            "4: Révélation majeure ou rumeur urgente à propager",
        ],
    )


def build_d6_reflect_gate() -> NoulQuestion:
    """D6 — ReflectGate : Décision de déclencher une réflexion profonde en fin de journée."""
    return NoulQuestion(
        instructions="Est-ce le bon moment pour cette personne de prendre du recul et de réfléchir sur les événements vécus ?",
        criteria={
            "true": "Prendre un temps calme de réflexion",
            "false": "Poursuivre sa soirée sans introspection",
        },
    )


def build_d7_continue_gate(turns_count: int) -> NoulQuestion:
    """D7 — ContinueGate : Décision de poursuivre la conversation après chaque réplique."""
    return NoulQuestion(
        instructions=f"Après {turns_count} échanges, la personne souhaite-t-elle poursuivre la discussion ?",
        criteria={
            "true": "Poursuivre l'échange et rebondir",
            "false": "Prendre congé poliment et terminer",
        },
    )


def build_d8_credibility_gate(claim_text: str, source_name: str) -> ScoreQuestion:
    """D8 — CredibilityGate : Évalue la crédibilité d'une information reçue d'un tiers."""
    return ScoreQuestion(
        instructions=f"Cette information rapportée par {source_name} est-elle crédible : « {claim_text} » ?",
        criteria=[
            "1: Invraisemblable, fausse rumeur ou commérage suspect",
            "2: Douteux ou non confirmé",
            "3: Plausible et digne d'intérêt",
            "4: Certain, officiel et digne de pleine confiance",
        ],
    )
