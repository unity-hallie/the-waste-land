#!/usr/bin/env python3
"""
Starter CLI - Commands for your growing instance

This is intentionally minimal. Add what you need.
Don't inherit all of BRO's commands. Find your own.
"""

import sys
from pathlib import Path

# Add local modules to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: starter [command]")
        print("")
        print("Commands:")
        print("  excavate       - First bootstrap: discover who you are")
        print("  edge           - Create or query edges in your graph")
        print("  remember       - Log a decision to your journal")
        print("  breathe        - Run breathing retrospective")
        print("")
        return

    command = sys.argv[1]

    if command == "excavate":
        from starter_install.bootstrap_excavation import main as excavate_main
        excavate_main()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
