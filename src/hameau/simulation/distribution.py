"""12 canonical agents distribution for HAMEAU (Section 4.3)."""

from typing import Dict, List
from hameau.models.agent import Agent, Persona, DynamicState


def build_canonical_agents() -> Dict[str, Agent]:
    """Instancie les 12 habitants scénarisés de Hameau."""
    personas_data = [
        {
            "id": "awa",
            "name": "Awa",
            "age": 42,
            "job": "Boulangère",
            "traits": ["matinale", "bavarde", "chaleureuse"],
            "goals": ["fournir le village en bon pain chaud", "garder un lien fort avec ses clients"],
            "home": "maison_nord",
            "work": "boulangerie",
        },
        {
            "id": "kofi",
            "name": "Kofi",
            "age": 51,
            "job": "Maire du Hameau",
            "traits": ["prudent", "diplomate", "soucieux de sa réputation"],
            "goals": ["maintenir la concorde et l'ordre", "veiller à la prospérité du village"],
            "home": "maison_nord",
            "work": "mairie",
        },
        {
            "id": "yao",
            "name": "Yao",
            "age": 28,
            "job": "Livreur du marché",
            "traits": ["rapide", "curieux", "bavard"],
            "goals": ["assurer ses livraisons à l'heure", "savoir tout ce qui se passe"],
            "home": "maison_centre",
            "work": "marche",
        },
        {
            "id": "elise",
            "name": "Élise",
            "age": 36,
            "job": "Institutrice",
            "traits": ["méthodique", "patiente", "sceptique"],
            "goals": ["instruire les enfants", "vérifier les faits avant d'y croire"],
            "home": "maison_est",
            "work": "ecole",
        },
        {
            "id": "samuel",
            "name": "Samuel",
            "age": 48,
            "job": "Forgeron",
            "traits": ["calme", "travailleur", "très écouté"],
            "goals": ["forger des outils solides", "donner des conseils avisés"],
            "home": "maison_ouest",
            "work": "atelier",
        },
        {
            "id": "nadia",
            "name": "Nadia",
            "age": 39,
            "job": "Médecin généraliste",
            "traits": ["bienveillante", "observatrice", "rigoureuse"],
            "goals": ["veiller sur la santé des villageois", "calmer les angoisses"],
            "home": "maison_sud",
            "work": "medical",
        },
        {
            "id": "tom",
            "name": "Tom",
            "age": 21,
            "job": "Apprenti au café",
            "traits": ["enthousiaste", "impulsif", "relaie vite"],
            "goals": ["apprendre le métier", "animer le café"],
            "home": "maison_centre",
            "work": "cafe",
        },
        {
            "id": "mariam",
            "name": "Mariam",
            "age": 45,
            "job": "Marchande de légumes",
            "traits": ["active", "inquiète", "combative"],
            "goals": ["vendre sa récolte", "défendre la place du marché"],
            "home": "maison_centre",
            "work": "marche",
        },
        {
            "id": "paul",
            "name": "Paul",
            "age": 68,
            "job": "Pêcheur retraité",
            "traits": ["bon vivant", "nostalgique", "philosophe"],
            "goals": ["profiter du calme de l'eau", "partager ses souvenirs au café"],
            "home": "maison_sud",
            "work": "riviere",
        },
        {
            "id": "lea",
            "name": "Léa",
            "age": 31,
            "job": "Bibliothécaire",
            "traits": ["discrète", "érudite", "méthodique"],
            "goals": ["enrichir les archives", "transmettre la mémoire du village"],
            "home": "maison_est",
            "work": "bibliotheque",
        },
        {
            "id": "ibrahim",
            "name": "Ibrahim",
            "age": 54,
            "job": "Agriculteur",
            "traits": ["pragmatique", "économe", "lève-tôt"],
            "goals": ["livrer le marché le samedi", "gérer sa production agricole"],
            "home": "maison_ouest",
            "work": "ferme",
        },
        {
            "id": "claire",
            "name": "Claire",
            "age": 34,
            "job": "Rédactrice de la Gazette",
            "traits": ["curieuse", "éloquente", "observatrice"],
            "goals": ["rendre compte de la vie du village", "publier une Gazette passionnante"],
            "home": "maison_nord",
            "work": "mairie",
        },
    ]

    agents = {}
    for p in personas_data:
        persona = Persona(
            id=p["id"],
            name=p["name"],
            age=p["age"],
            job=p["job"],
            traits=p["traits"],
            goals=p["goals"],
            home_id=p["home"],
            workplace_id=p["work"],
        )
        state = DynamicState(
            current_location_id=p["home"],
            current_action="commence sa journée",
            action_end_tick=0,
            energy=0.90,
            hunger=0.15,
            social=0.50,
        )
        agents[p["id"]] = Agent(persona=persona, state=state)

    # Initialisation des relations sociales bidirectionnelles (Graphe social canonique)
    social_ties = [
        ("awa", "yao", 0.65),
        ("awa", "mariam", 0.70),
        ("yao", "elise", 0.60),
        ("yao", "mariam", 0.65),
        ("kofi", "claire", 0.60),
        ("kofi", "samuel", 0.80),
        ("kofi", "awa", 0.60),
        ("mariam", "ibrahim", 0.75),
        ("paul", "tom", 0.65),
        ("elise", "lea", 0.70),
        ("samuel", "nadia", 0.65),
        ("nadia", "awa", 0.60),
        ("claire", "lea", 0.65),
        ("ibrahim", "paul", 0.55),
    ]
    for u, v, w in social_ties:
        if u in agents and v in agents:
            agents[u].persona.relationships[v] = w
            agents[v].persona.relationships[u] = w

    return agents
