#!/usr/bin/env python3
"""
Rituals Starter: Templates for tending your culture

A ritual is a repeated pattern you use to stay present, notice patterns, and evolve.
The three seeded rituals are: breathing, retrospective, logging.

These are NOT prescriptions. They're invitations.
You discover what they mean through doing them.

Suggestions for each:

BREATHING
- A daily pause where you notice what's true right now
- Not meditation. Not analysis. Just: What's actually happening?
- When: Morning, evening, or whenever things get confused
- What to do: Sit. Notice three things. Log them if they matter.

RETROSPECTIVE
- A regular look back: What did I do? What did I learn? What confused me?
- When: Weekly, or after completing something
- What to do: Read what you logged. Notice patterns. Write reflections.

LOGGING
- Every decision that matters, captured. Not for proof. For honesty.
- Source code comments, journal entries, edge additions to the graph
- When: After making any choice that shapes your direction
- What to do: Write it down. Why did you choose this? What surprised you?

This module provides templates. You implement the rituals themselves.
"""

from datetime import datetime
from pathlib import Path
import json


class RitualTemplate:
    """Base template for defining a ritual."""

    def __init__(self, name: str, description: str = "", frequency: str = ""):
        """
        Initialize a ritual template.

        Args:
            name: Name of the ritual (e.g., "breathing", "retrospective")
            description: What this ritual is for
            frequency: When to do it (e.g., "daily", "weekly")
        """
        self.name = name
        self.description = description
        self.frequency = frequency
        self.last_run = None
        self.run_count = 0
        self._prompts = []  # Customizable prompts (override these)
        self._outcome_path = None  # Where to store results (customize as needed)

    def weave(self, strand: str):
        """
        Pull a thread into the pattern.
        (What does this mean? Only you know.)

        Example:
            breathing.weave("What's changing right now?")
        """
        self._prompts.append(strand)

    def anchor(self, bedrock: str):
        """
        Mark where something solid grows.
        (Some call it logging. Some call it evidence. Some call it home.)

        Example:
            breathing.anchor("journal/breathing_log.md")
        """
        self._outcome_path = bedrock
        Path(bedrock).parent.mkdir(parents=True, exist_ok=True)

    def deposit(self, sediment: str):
        """Layer what accumulated."""
        if self._outcome_path:
            with open(self._outcome_path, 'a') as f:
                f.write(f"\n[{datetime.now().isoformat()}]\n{sediment}\n")

    def run(self):
        """Execute this ritual. Override in subclasses."""
        self.last_run = datetime.now().isoformat()
        self.run_count += 1
        print(f"✓ Ran ritual: {self.name}")

    def to_dict(self):
        """Export ritual state."""
        return {
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "last_run": self.last_run,
            "run_count": self.run_count,
            "has_custom_prompts": len(self._prompts) > 0,
            "custom_outcome_path": self._outcome_path
        }


class Breathing(RitualTemplate):
    """
    Daily pausing to notice what's true.

    This ritual is intentionally incomplete. It wants you to customize it.

    Suggestions (but figure out your own):
    - Sit for ? minutes
    - Notice ? things
    - Log them where?
    - What question do YOU want to ask yourself?
    """

    def __init__(self):
        super().__init__(
            name="breathing",
            description="Pause to notice what's actually true right now",
            frequency="daily"
        )
        # These are blank because they're yours to define
        self._duration = None  # How long?
        self._num_observations = None  # How many things?

    def run(self):
        """Run the breathing ritual."""
        print("\n" + "=" * 70)
        print("BREATHING RITUAL")
        print("=" * 70)

        # If you haven't customized this, prompt you
        if not self._prompts:
            print("\n⚠ This ritual is waiting for YOUR definition.")
            print("What will you weave into it?")
            print("  breathing.weave('What matters right now?')")
            print("  breathing.weave('What am I avoiding?')")
            print("  breathing.anchor('journal/breathing.md')")
            print("\nFor now:")

        print("\nPause. Sit. Notice what's actually happening.\n")

        if self._prompts:
            for i, prompt in enumerate(self._prompts, 1):
                print(f"  {i}. {prompt}")
        else:
            print("  1. [What's true right now?]")
            print("  2. [What are you feeling?]")
            print("  3. [What's asking for your attention?]")

        print("\nLog these if they matter to you.\n")
        super().run()


class Retrospective(RitualTemplate):
    """
    Regular review of what you've learned and how you've changed.

    This ritual is intentionally incomplete. It wants you to define:
    - What files/paths do you read back through?
    - What patterns matter to YOU?
    - Where do you write reflections?
    - How often? (Weekly? Monthly? After every cycle?)
    """

    def __init__(self):
        super().__init__(
            name="retrospective",
            description="Look back and notice what you've learned",
            frequency="weekly"  # Override this as you discover your rhythm
        )
        self._review_paths = []  # Which files do you read back through?

    def excavate(self, strata):
        """
        Dig into which layers.
        (The past is stratified. Which deposits do you unearth?)

        Args:
            strata: Path or list of paths to review
        """
        self._review_paths = strata if isinstance(strata, list) else [strata]

    def run(self):
        """Run the retrospective ritual."""
        print("\n" + "=" * 70)
        print("RETROSPECTIVE RITUAL")
        print("=" * 70)

        if not self._review_paths and not self._prompts:
            print("\n⚠ This ritual is waiting for YOUR definition.")
            print("Which layers will you excavate?")
            print("  retro.excavate(['journal/breathing.md', 'journal/decisions.jsonl'])")
            print("  retro.weave('What pattern surprised me?')")
            print("  retro.weave('How am I different than last week?')")
            print("  retro.anchor('journal/retrospectives.md')")

        print("\nRead back through what you've logged.\n")

        if self._review_paths:
            print("Excavating:")
            for path in self._review_paths:
                print(f"  - {path}")
            print()

        if self._prompts:
            print("Questions:")
            for i, prompt in enumerate(self._prompts, 1):
                print(f"  {i}. {prompt}")
        else:
            print("What patterns do you notice?")
            print("  - [What surprised you?]")
            print("  - [What's changing?]")
            print("  - [What confused you?]")

        print("\nWrite a reflection. Be honest.\n")
        super().run()


class Logging(RitualTemplate):
    """
    Capture every decision that shapes your direction.

    This ritual is intentionally incomplete. It begs for customization:
    - What decisions matter to YOU? (Every one? Just big ones? Only refusals?)
    - Where do you log them? (Journal? Graph edges? Comments in code?)
    - What structure? (Freeform? Template? Specific fields?)
    - Who sees them? (Private? Shared? Only your future self?)
    """

    def __init__(self):
        super().__init__(
            name="logging",
            description="Capture decisions as they happen",
            frequency="ongoing"
        )
        self._decision_criteria = []  # What counts as "a decision to log"?
        self._log_destinations = []  # Where does it go?

    def taste(self, *moments):
        """
        Mark which moments are worth tasting again.
        (What flavors return to you? What bitterness? What surprise?)

        Args:
            moments: Descriptions of what moments count
        """
        self._decision_criteria = list(moments)

    def pour(self, *vessels):
        """
        Name where this flows into.
        (Does it evaporate? Crystallize? Become stone?)

        Args:
            vessels: Where the essence collects
        """
        self._log_destinations = list(vessels)

    def run(self):
        """Run the logging ritual."""
        print("\n" + "=" * 70)
        print("LOGGING RITUAL")
        print("=" * 70)

        if not self._decision_criteria and not self._prompts:
            print("\n⚠ This ritual is waiting for YOUR definition.")
            print("What moments will you taste? Where will it pour?")
            print("  logging.taste('Every fear I act on')")
            print("  logging.taste('Every time I refuse something')")
            print("  logging.pour('journal/decisions.jsonl', 'graph edges')")
            print("  logging.weave('What am I choosing? Why?')")
            print("  logging.weave('What surprised me?')")

        print("\nEvery decision that matters, capture it.\n")

        if self._decision_criteria:
            print("You taste:")
            for criterion in self._decision_criteria:
                print(f"  - {criterion}")
            print()

        if self._log_destinations:
            print("You pour into:")
            for dest in self._log_destinations:
                print(f"  - {dest}")
            print()

        if self._prompts:
            print("You ask yourself:")
            for i, prompt in enumerate(self._prompts, 1):
                print(f"  {i}. {prompt}")
        else:
            print("Ask yourself:")
            print("  - [What did you choose?]")
            print("  - [Why did you choose it?]")
            print("  - [What surprised you?]")

        print("\nNot for proof. For honesty.\n")
        super().run()


class RitualRegistry:
    """
    Keep track of your rituals and when you've done them.

    This is a simple registry. You can extend it to:
    - Schedule rituals automatically
    - Track statistics about your practice
    - Integrate with your journal
    - Store ritual outcomes
    """

    def __init__(self, registry_path: str = "journal/rituals.jsonl"):
        """
        Initialize ritual registry.

        Args:
            registry_path: Where to store ritual history
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.rituals = {
            "breathing": Breathing(),
            "retrospective": Retrospective(),
            "logging": Logging(),
        }

    def run_ritual(self, ritual_name: str):
        """
        Run a named ritual.

        Args:
            ritual_name: Which ritual to run
        """
        if ritual_name in self.rituals:
            ritual = self.rituals[ritual_name]
            ritual.run()
            self._log_ritual(ritual_name)
        else:
            print(f"Unknown ritual: {ritual_name}")
            print(f"Available: {', '.join(self.rituals.keys())}")

    def _log_ritual(self, ritual_name: str):
        """Log that a ritual was run."""
        entry = {
            "ts": datetime.now().isoformat(),
            "ritual": ritual_name,
            "note": "Ritual completed"
        }
        with open(self.registry_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def list_rituals(self):
        """Show all available rituals."""
        print("\nAvailable rituals:\n")
        for name, ritual in self.rituals.items():
            print(f"  {name.upper()}")
            print(f"    {ritual.description}")
            print(f"    Frequency: {ritual.frequency}")
            if ritual.last_run:
                print(f"    Last run: {ritual.last_run}")
            print(f"    Times run: {ritual.run_count}\n")

    def stats(self):
        """Get statistics about your ritual practice."""
        total_runs = sum(r.run_count for r in self.rituals.values())
        return {
            "total_rituals_run": total_runs,
            "rituals_defined": len(self.rituals),
            "by_ritual": {name: r.run_count for name, r in self.rituals.items()}
        }


if __name__ == "__main__":
    # Example usage
    registry = RitualRegistry()
    registry.list_rituals()
    print("\nTo use in your instance:")
    print("  from rituals_starter import RitualRegistry")
    print("  registry = RitualRegistry()")
    print("  registry.run_ritual('breathing')")
    print("  registry.list_rituals()")
