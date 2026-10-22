"""Unit tests for HAMEAU data models."""

from hameau.models import build_default_village, Location, Persona, DynamicState, Agent, MemoryRecord


def test_village_graph_construction():
    world = build_default_village()
    assert len(world.locations) == 19
    assert "marche" in world.locations
    assert "mairie" in world.locations
    assert "place_fetes" in world.locations
    assert "village_voisin" in world.locations
    assert world.travel_time("marche", "mairie") == 1
    assert world.travel_time("marche", "marche") == 0
    # Travel between marche and ferme (requires multiple hops)
    assert world.travel_time("marche", "ferme") >= 2


def test_agent_memory_and_belief():
    persona = Persona(
        id="yao",
        name="Yao",
        age=32,
        job="Livreur du marché",
        traits=["rapide", "curieux", "sociable"],
        goals=["gagner sa vie", "garder le contact avec le village"],
        home_id="maison_centre",
        workplace_id="marche",
    )
    state = DynamicState(current_location_id="marche")
    agent = Agent(persona=persona, state=state)

    assert agent.is_available() is True
    assert agent.persona.did_stock_provisions is False

    # Simulate rumor belief
    agent.set_believed_fact("R1_fermeture_marche", 0.75)
    assert agent.persona.did_stock_provisions is True

    # Simulate mayor's debunk
    agent.set_believed_fact("R2_dementi_maire", 0.85)
    assert agent.persona.did_stock_provisions is False
