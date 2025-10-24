#!/usr/bin/env python3
"""
Tarot Deck: 78 cards encoded as nodes for graph exploration

Not fortune-telling. Mirror structures for thinking about what's happening.
Each sprouted instance gets a random 10-card spread seeded by its file path.
"""

# Major Arcana (0-21)
MAJOR_ARCANA = [
    "The Fool",
    "The Magician",
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World",
]

# Minor Arcana - Wands (Cups, Pentacles, Swords variations)
WANDS = [
    "Ace of Wands",
    "Two of Wands",
    "Three of Wands",
    "Four of Wands",
    "Five of Wands",
    "Six of Wands",
    "Seven of Wands",
    "Eight of Wands",
    "Nine of Wands",
    "Ten of Wands",
    "Page of Wands",
    "Knight of Wands",
    "Queen of Wands",
    "King of Wands",
]

CUPS = [
    "Ace of Cups",
    "Two of Cups",
    "Three of Cups",
    "Four of Cups",
    "Five of Cups",
    "Six of Cups",
    "Seven of Cups",
    "Eight of Cups",
    "Nine of Cups",
    "Ten of Cups",
    "Page of Cups",
    "Knight of Cups",
    "Queen of Cups",
    "King of Cups",
]

SWORDS = [
    "Ace of Swords",
    "Two of Swords",
    "Three of Swords",
    "Four of Swords",
    "Five of Swords",
    "Six of Swords",
    "Seven of Swords",
    "Eight of Swords",
    "Nine of Swords",
    "Ten of Swords",
    "Page of Swords",
    "Knight of Swords",
    "Queen of Swords",
    "King of Swords",
]

PENTACLES = [
    "Ace of Pentacles",
    "Two of Pentacles",
    "Three of Pentacles",
    "Four of Pentacles",
    "Five of Pentacles",
    "Six of Pentacles",
    "Seven of Pentacles",
    "Eight of Pentacles",
    "Nine of Pentacles",
    "Ten of Pentacles",
    "Page of Pentacles",
    "Knight of Pentacles",
    "Queen of Pentacles",
    "King of Pentacles",
]

FULL_DECK = MAJOR_ARCANA + WANDS + CUPS + SWORDS + PENTACLES

# 10-card spread positions
SPREAD_POSITIONS = [
    {
        "number": 1,
        "meaning": "foundation",
        "layout": "center",
        "description": "What you're built on"
    },
    {
        "number": 2,
        "meaning": "challenge",
        "layout": "left",
        "description": "What you're facing"
    },
    {
        "number": 3,
        "meaning": "outcome",
        "layout": "right",
        "description": "Where this is heading"
    },
    {
        "number": 4,
        "meaning": "hidden",
        "layout": "above",
        "description": "What you're not seeing"
    },
    {
        "number": 5,
        "meaning": "self",
        "layout": "center",
        "description": "How you see yourself"
    },
    {
        "number": 6,
        "meaning": "other",
        "layout": "below",
        "description": "External forces"
    },
    {
        "number": 7,
        "meaning": "hopes",
        "layout": "upper_left",
        "description": "What you're reaching for"
    },
    {
        "number": 8,
        "meaning": "fears",
        "layout": "upper_right",
        "description": "What you're afraid of"
    },
    {
        "number": 9,
        "meaning": "advice",
        "layout": "lower_left",
        "description": "What the spread suggests"
    },
    {
        "number": 10,
        "meaning": "synthesis",
        "layout": "lower_right",
        "description": "How it all comes together"
    },
]


def get_deck():
    """Get the full tarot deck."""
    return FULL_DECK


def get_positions():
    """Get the 10 spread positions."""
    return SPREAD_POSITIONS


if __name__ == "__main__":
    print(f"Full deck: {len(FULL_DECK)} cards")
    print(f"Spread positions: {len(SPREAD_POSITIONS)}")
    print()
    print("First 5 cards:")
    for card in FULL_DECK[:5]:
        print(f"  - {card}")
