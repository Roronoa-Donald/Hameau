"""World graph model and location definitions for HAMEAU."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Location:
    id: str
    name: str
    category: str
    x: float  # Coordonnée relative X pour le viewer Canvas [0.0 - 1.0]
    y: float  # Coordonnée relative Y pour le viewer Canvas [0.0 - 1.0]
    capacity: int = 10
    default_routine: str = "vaquer à ses occupations"


@dataclass
class WorldGraph:
    locations: Dict[str, Location] = field(default_factory=dict)
    # Adjacence et coût de trajet en ticks (1 tick = 5 min)
    adjacency: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def add_location(self, loc: Location) -> None:
        self.locations[loc.id] = loc
        if loc.id not in self.adjacency:
            self.adjacency[loc.id] = {}

    def add_edge(self, u: str, v: str, travel_ticks: int = 1) -> None:
        """Ajoute une route bidirectionnelle entre deux lieux."""
        self.adjacency[u][v] = travel_ticks
        self.adjacency[v][u] = travel_ticks

    def travel_time(self, u: str, v: str) -> int:
        """Calcule le coût de trajet (plus court chemin Dijkstra si non direct)."""
        if u == v:
            return 0
        if v in self.adjacency.get(u, {}):
            return self.adjacency[u][v]
        
        # Dijkstra simple pour trouver le temps de trajet
        visited = set()
        distances = {u: 0}
        unvisited = set(self.locations.keys())
        
        while unvisited:
            curr = min(unvisited, key=lambda node: distances.get(node, float("inf")))
            curr_dist = distances.get(curr, float("inf"))
            if curr_dist == float("inf") or curr == v:
                break
            unvisited.remove(curr)
            visited.add(curr)
            
            for neighbor, weight in self.adjacency.get(curr, {}).items():
                if neighbor in visited:
                    continue
                new_dist = curr_dist + weight
                if new_dist < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_dist
                    
        return distances.get(v, 2)


def build_default_village() -> WorldGraph:
    """Construit le village canonique de Hameau (10 lieux publics + 5 maisons)."""
    world = WorldGraph()

    # 10 Lieux publics
    locs = [
        Location("marche", "Place du Marché", "commerce", 0.50, 0.45, default_routine="tenir son étal ou faire ses courses"),
        Location("boulangerie", "Boulangerie d'Awa", "artisanat", 0.38, 0.35, default_routine="pétrir et cuire le pain"),
        Location("mairie", "Mairie du Hameau", "civique", 0.50, 0.22, default_routine="administrer les affaires communales"),
        Location("ecole", "École communale", "education", 0.68, 0.28, default_routine="enseigner et corriger les cahiers"),
        Location("bibliotheque", "Bibliothèque municipale", "culture", 0.72, 0.48, default_routine="classer les livres et archives"),
        Location("atelier", "Atelier de forge", "artisanat", 0.26, 0.50, default_routine="forger et réparer les outils"),
        Location("medical", "Cabinet médical", "sante", 0.35, 0.62, default_routine="consulter et soigner les habitants"),
        Location("cafe", "Café de la Rivière", "social", 0.52, 0.68, default_routine="boire un verre et écouter les nouvelles"),
        Location("riviere", "Berges de la Rivière", "nature", 0.65, 0.78, default_routine="pêcher au calme ou se promener"),
        Location("ferme", "Ferme des Hauts", "agriculture", 0.18, 0.72, default_routine="soigner les bêtes et cultiver"),
        # Nœuds de résidences
        Location("maison_nord", "Maisons du Quartier Nord", "residence", 0.58, 0.14, default_routine="se reposer chez soi"),
        Location("maison_ouest", "Maisons des Artisans", "residence", 0.18, 0.38, default_routine="se reposer chez soi"),
        Location("maison_centre", "Maisons de la Place", "residence", 0.42, 0.52, default_routine="se reposer chez soi"),
        Location("maison_est", "Maisons de l'Est", "residence", 0.82, 0.38, default_routine="se reposer chez soi"),
        Location("maison_sud", "Maisons de la Rivière", "residence", 0.40, 0.82, default_routine="se reposer chez soi"),
    ]

    for loc in locs:
        world.add_location(loc)

    # Réseau de sentiers et rues (coût en ticks, 1 tick = 5 min)
    edges = [
        ("mairie", "marche", 1),
        ("mairie", "ecole", 1),
        ("mairie", "maison_nord", 1),
        ("marche", "boulangerie", 1),
        ("marche", "cafe", 1),
        ("marche", "bibliotheque", 1),
        ("marche", "maison_centre", 1),
        ("boulangerie", "atelier", 1),
        ("boulangerie", "maison_ouest", 1),
        ("atelier", "ferme", 2),
        ("atelier", "medical", 1),
        ("medical", "cafe", 1),
        ("medical", "maison_sud", 1),
        ("cafe", "riviere", 1),
        ("ecole", "bibliotheque", 1),
        ("ecole", "maison_est", 1),
        ("bibliotheque", "riviere", 2),
        ("ferme", "medical", 2),
    ]

    for u, v, ticks in edges:
        world.add_edge(u, v, ticks)

    return world
