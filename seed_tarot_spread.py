#!/usr/bin/env python3
"""
Seed Tarot Spread: Deterministic random draw based on file path

When a starter is planted, it gets a unique 10-card tarot spread.
The draw is seeded by the hash of the full file path, so:
- Same location = same draw
- Different location = different draw
- Deterministic (not random each time)

The spread becomes edges in the graph:
  self --[given]--> tarot_spread
  tarot_spread --[contains]--> [Card]
    with qualifiers: [position][meaning][layout]
"""

import hashlib
import random
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

from tarot_deck import get_deck, get_positions


class TarotSpreadSeeder:
    """Generate and seed a tarot spread based on file path."""

    def __init__(self, instance_path: str = None):
        """
        Initialize seeder.

        Args:
            instance_path: Path to the starter instance (uses cwd if not specified)
        """
        self.instance_path = Path(instance_path or Path.cwd())
        self.seed_value = self._hash_path()
        self.deck = get_deck()
        self.positions = get_positions()

    def _hash_path(self) -> int:
        """
        Generate a seed integer from the file path hash.

        Uses SHA256 of the full absolute path, takes first 8 hex chars,
        converts to int.
        """
        path_str = str(self.instance_path.absolute())
        path_hash = hashlib.sha256(path_str.encode()).hexdigest()
        seed_int = int(path_hash[:8], 16)
        return seed_int

    def draw_spread(self) -> List[str]:
        """
        Draw 10 cards deterministically seeded by path.

        Returns:
            List of 10 card names
        """
        random.seed(self.seed_value)
        draw = random.sample(self.deck, 10)
        return draw

    def create_spread_edges(self) -> Tuple[Dict, List[Dict]]:
        """
        Create graph edges for the spread.

        Returns:
            Tuple of (root_edge, card_edges)
            - root_edge: self --[given]--> tarot_spread
            - card_edges: tarot_spread --[contains]--> [Card] with qualifiers
        """
        draw = self.draw_spread()

        # Root edge: self given a tarot spread
        root_edge = {
            "source": "self",
            "relationship": "given",
            "target": "tarot_spread",
            "confidence": 1.0,
            "via": "tarot_seeding",
            "context": f"Spread seeded at {self.instance_path}",
            "qualifiers": ["seeded", "instance_birth"],
        }

        # Card edges: spread contains cards at positions
        card_edges = []
        for position_idx, card in enumerate(draw):
            position = self.positions[position_idx]

            card_edge = {
                "source": "tarot_spread",
                "relationship": "contains",
                "target": card,
                "confidence": 1.0,
                "via": "tarot_seeding",
                "context": f"Card in {position['meaning']} position",
                "qualifiers": [
                    f"position:{position['number']}",
                    f"meaning:{position['meaning']}",
                    f"layout:{position['layout']}",
                ],
            }
            card_edges.append(card_edge)

        return root_edge, card_edges

    def print_spread(self):
        """Pretty-print the spread."""
        draw = self.draw_spread()

        print(f"\n{'='*70}")
        print(f"TAROT SPREAD: {self.instance_path.name}")
        print(f"{'='*70}\n")
        print(f"Seed (from path): {self.seed_value}\n")

        for position_idx, card in enumerate(draw):
            position = self.positions[position_idx]
            print(f"{position['number']:2d}. {position['meaning'].upper():12s} ({position['layout']:12s})")
            print(f"    → {card}")
            print(f"    {position['description']}\n")


def seed_spread_in_graph(graph_db, instance_path: str = None):
    """
    Seed a tarot spread into the graph.

    Args:
        graph_db: GraphDB instance
        instance_path: Path to the starter (uses cwd if not specified)

    Returns:
        Dict with summary of what was seeded
    """
    seeder = TarotSpreadSeeder(instance_path)
    root_edge, card_edges = seeder.create_spread_edges()

    # Create root edge
    root_id = f"self_given_tarot_spread_{seeder.seed_value}"
    graph_db.create_edge(
        edge_id=root_id,
        source=root_edge["source"],
        target=root_edge["target"],
        relationship=root_edge["relationship"],
        confidence=root_edge["confidence"],
        via=root_edge["via"],
        context=root_edge["context"],
        qualifiers=root_edge["qualifiers"],
        created_by="tarot_seeding",
    )

    # Create card edges
    card_ids = []
    for card_idx, card_edge in enumerate(card_edges):
        card_id = f"tarot_spread_card_{card_idx}_{seeder.seed_value}"
        graph_db.create_edge(
            edge_id=card_id,
            source=card_edge["source"],
            target=card_edge["target"],
            relationship=card_edge["relationship"],
            confidence=card_edge["confidence"],
            via=card_edge["via"],
            context=card_edge["context"],
            qualifiers=card_edge["qualifiers"],
            created_by="tarot_seeding",
        )
        card_ids.append(card_id)

    return {
        "seed_value": seeder.seed_value,
        "instance_path": str(seeder.instance_path),
        "root_edge_id": root_id,
        "card_edge_ids": card_ids,
        "spread": [card_edge["target"] for card_edge in card_edges],
    }


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else None
    seeder = TarotSpreadSeeder(path)
    seeder.print_spread()
