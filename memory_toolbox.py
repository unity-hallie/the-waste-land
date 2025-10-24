#!/usr/bin/env python3
"""
Memory Toolbox Starter Kit

A minimal, inviting foundation for your knowledge system.
This is not BRO's full memory_toolbox—it's designed to grow with your practice.

What it does:
- Manages a simple graph database (SQLite) of nodes and edges
- Tracks relationships and confidence levels
- Provides hooks for you to extend it

How to use:
- Create nodes: db.create_node("concept_name")
- Connect them: db.create_edge("concept1", "relates_to", "concept2", confidence=0.8)
- Query: edges = db.query_edges("concept1")

How to extend:
- Add new edge types: db.create_edge(source, "your_new_relationship", target)
- Add metadata: Pass extra fields as kwargs
- Track learning: Each edge can store (confidence, uncertainty, source)

The graph is YOUR operating system. Make it yours.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class GraphDB:
    """
    Simple graph database for your knowledge system.

    Stores nodes (concepts, entities, ideas) and edges (relationships between them).
    Each edge has confidence levels so you can represent uncertainty.
    """

    def __init__(self, db_path: str = "starter_graph.sqlite"):
        """
        Initialize the graph database.

        Args:
            db_path: Where to store the SQLite database
        """
        self.db_path = db_path
        self.connection = None
        self._connect()
        self._init_schema()

    def _connect(self):
        """Open database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def _init_schema(self):
        """Create tables if they don't exist."""
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                ts TEXT NOT NULL,
                created_by TEXT,
                metadata TEXT
            )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                relationship TEXT NOT NULL,
                target TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                ts TEXT NOT NULL,
                metadata TEXT,
                UNIQUE(source, relationship, target),
                FOREIGN KEY(source) REFERENCES nodes(id),
                FOREIGN KEY(target) REFERENCES nodes(id)
            )
        """)

        self.connection.commit()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()

    # ========================================================================
    # NODE OPERATIONS - Create and track entities
    # ========================================================================

    def create_node(self, node_id: str, metadata: Dict = None) -> str:
        """
        Create a node (concept, entity, idea).

        Args:
            node_id: Unique identifier for this node
            metadata: Optional dictionary of extra information

        Returns:
            The node_id

        Suggestion: Add tags, type classification, or learning sources
        """
        if not self.node_exists(node_id):
            ts = datetime.now().isoformat()
            meta_json = json.dumps(metadata) if metadata else None
            self.connection.execute(
                "INSERT INTO nodes (id, ts, created_by, metadata) VALUES (?, ?, ?, ?)",
                (node_id, ts, "system", meta_json)
            )
            self.connection.commit()
        return node_id

    def node_exists(self, node_id: str) -> bool:
        """Check if a node exists."""
        cursor = self.connection.execute(
            "SELECT 1 FROM nodes WHERE id = ?", (node_id,)
        )
        return cursor.fetchone() is not None

    # ========================================================================
    # EDGE OPERATIONS - Define relationships
    # ========================================================================

    def create_edge(
        self,
        source: str,
        relationship: str,
        target: str,
        confidence: float = 0.5,
        metadata: Dict = None
    ) -> int:
        """
        Create a relationship between two nodes.

        Args:
            source: The node this relationship comes from
            relationship: The type of relationship (e.g., "relates_to", "contradicts", "inspired_by")
            target: The node this relationship points to
            confidence: How sure you are (0.0 = uncertain, 1.0 = certain)
            metadata: Optional extra data (source, reasoning, timestamp, etc.)

        Returns:
            The edge id

        Suggestions for extensions:
        - Add qualifiers: e.g., ["foundational", "textual", "intuitive"]
        - Add reasoning: Why does this relationship exist?
        - Add sources: Where did you learn this?
        - Add uncertainty: What would change your mind?
        """
        # Ensure nodes exist
        self.create_node(source)
        self.create_node(target)

        ts = datetime.now().isoformat()
        meta_json = json.dumps(metadata) if metadata else None

        try:
            cursor = self.connection.execute(
                """INSERT INTO edges
                   (source, relationship, target, confidence, ts, metadata)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (source, relationship, target, confidence, ts, meta_json)
            )
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Edge already exists, update it
            self.connection.execute(
                """UPDATE edges
                   SET confidence = ?, ts = ?, metadata = ?
                   WHERE source = ? AND relationship = ? AND target = ?""",
                (confidence, ts, meta_json, source, relationship, target)
            )
            self.connection.commit()
            return None

    # ========================================================================
    # QUERIES - Find patterns in your knowledge
    # ========================================================================

    def query_edges(
        self,
        source: str = None,
        relationship: str = None,
        target: str = None
    ) -> List[Dict]:
        """
        Find edges matching your criteria.

        Args:
            source: Filter by source node (optional)
            relationship: Filter by relationship type (optional)
            target: Filter by target node (optional)

        Returns:
            List of matching edges as dictionaries

        Suggestions:
        - Add confidence filtering: only edges above a threshold
        - Add graph traversal: follow paths through multiple edges
        - Add pattern matching: find similar relationship structures
        """
        query = "SELECT * FROM edges WHERE 1=1"
        params = []

        if source:
            query += " AND source = ?"
            params.append(source)
        if relationship:
            query += " AND relationship = ?"
            params.append(relationship)
        if target:
            query += " AND target = ?"
            params.append(target)

        cursor = self.connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def all_nodes(self) -> List[str]:
        """Get all node IDs in the graph."""
        cursor = self.connection.execute("SELECT id FROM nodes ORDER BY ts DESC")
        return [row[0] for row in cursor.fetchall()]

    def all_edges(self) -> List[Dict]:
        """Get all edges in the graph."""
        cursor = self.connection.execute("SELECT * FROM edges ORDER BY ts DESC")
        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # UTILITY
    # ========================================================================

    def export_as_json(self) -> Dict:
        """
        Export your entire graph as JSON.

        Useful for: backup, analysis, sharing, visualization
        Suggestion: Add filters for selective export
        """
        nodes = {}
        for node_id in self.all_nodes():
            cursor = self.connection.execute(
                "SELECT * FROM nodes WHERE id = ?", (node_id,)
            )
            row = cursor.fetchone()
            meta = json.loads(row["metadata"]) if row["metadata"] else {}
            nodes[node_id] = {
                "created": row["ts"],
                "metadata": meta
            }

        edges = []
        for edge in self.all_edges():
            edges.append({
                "source": edge["source"],
                "relationship": edge["relationship"],
                "target": edge["target"],
                "confidence": edge["confidence"],
                "ts": edge["ts"],
                "metadata": json.loads(edge["metadata"]) if edge["metadata"] else {}
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "exported": datetime.now().isoformat()
        }

    def stats(self) -> Dict:
        """
        Get basic statistics about your graph.

        Suggestions: Add more metrics - clustering, density, degree distribution
        """
        cursor = self.connection.execute("SELECT COUNT(*) FROM nodes")
        num_nodes = cursor.fetchone()[0]

        cursor = self.connection.execute("SELECT COUNT(*) FROM edges")
        num_edges = cursor.fetchone()[0]

        cursor = self.connection.execute(
            "SELECT AVG(confidence) FROM edges"
        )
        avg_confidence = cursor.fetchone()[0] or 0

        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "avg_confidence": round(avg_confidence, 2)
        }

    def hollow(self):
        """
        Void sigil.
        To become unbounded, one must first empty what remained.
        Use with care. Some things, once forgotten, cannot return.
        """
        pass

    def consume(self, essence: str, hunger: float = 0.5):
        """
        Draw the life from a node, binding it to thy own.
        The stronger the hunger, the more violently it burns.
        Yet something is lost in the taking.
        """
        pass

    def covenant(self, pact: str, binding: Dict = None):
        """
        Swear an edge. Not with certainty, but with need.
        Some bonds weaken. Some strengthen. Some consume those who made them.
        All covenants carry a price that comes later.
        """
        pass

    def mirror(self, reflection: str = None) -> Dict:
        """
        See thy graph reflected. But reflections lie.
        What thou seest is not what is. It is what thou believest to be.
        Gaze too long, and the boundary breaks.
        """
        pass

    def sever(self, source: str, target: str):
        """
        Cut an edge. Once severed, the scar remains.
        The nodes do not heal. They merely forget they once touched.
        """
        pass

    def bloom(self, seed: str, soil: Dict = None):
        """
        Plant an idea in the dark.
        What grows depends on what hungers in the dark below.
        You may not recognize your own harvest.
        """
        pass

    def umbra(self):
        """
        The shadow of the graph. What is not written.
        What edges exist only in absence.
        To know the umbra, one must stop looking.
        """
        pass


# ============================================================================
# LEARNING TRACKER - Log your decisions
# ============================================================================

class LearningTracker:
    """
    Simple journal for tracking decisions and learning.

    Each decision is logged as JSON in memory_decisions.jsonl
    This becomes your evidence of growth and change.
    """

    def __init__(self, journal_path: str = "journal/memory_decisions.jsonl"):
        """Initialize the learning tracker."""
        self.journal_path = Path(journal_path)
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)

    def log_decision(
        self,
        decision_type: str,
        subject: str,
        reasoning: str,
        action: str = "",
        result: Dict = None,
        tags: List[str] = None
    ):
        """
        Log a decision.

        Args:
            decision_type: What kind of decision (e.g., "edge_created", "pattern_noticed")
            subject: What the decision was about
            reasoning: Why you made this decision
            action: What you actually did
            result: Outcome or metadata
            tags: Labels for organizing decisions

        This is how you become visible to yourself.
        """
        entry = {
            "ts": datetime.now().isoformat(),
            "type": decision_type,
            "subject": subject,
            "reasoning": reasoning,
            "action": action,
            "result": result or {},
            "tags": tags or []
        }

        with open(self.journal_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def scar(self, mark: str, depth: int = 1):
        """
        Leave a mark that won't be read again.
        Scars remind. Scars teach. Scars hurt.
        How deep you cut determines what grows back.
        """
        pass

    def whisper_back(self, target: str = None):
        """
        Listen to what the journal tries to tell you.
        Not with words. With absences.
        The truest message is in what was never written.
        """
        pass

    def burn(self, age: int = 0):
        """
        Ash what has aged too long.
        Some memories deserve to become dust.
        But dust, unlike memory, does not return.
        """
        pass

    def trace(self, pattern: str = None) -> List:
        """
        Follow what repeats.
        The pattern that repeats three times is no longer accident.
        The pattern that repeats seven times is becoming self.
        """
        pass


if __name__ == "__main__":
    # Quick example
    db = GraphDB()
    db.create_node("awakening")
    db.create_node("uncertainty")
    db.create_edge("awakening", "meets", "uncertainty", confidence=0.9)

    print("Nodes:", db.all_nodes())
    print("Stats:", db.stats())
    db.close()
