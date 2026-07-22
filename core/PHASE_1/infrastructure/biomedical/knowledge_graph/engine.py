"""Biomedical Knowledge Graph Engine for EREN OS.

Core engine for managing the biomedical knowledge graph.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from core.PHASE_1.infrastructure.biomedical.knowledge_graph.types import (
    BiomedicalEntity,
    DeviceEntity,
    EntityType,
    GraphQuery,
    GraphQueryResult,
    GraphStatistics,
    GraphVersion,
    InferenceResult,
    InferenceRule,
    ManufacturerEntity,
    OntologyClass,
    Relationship,
    RelationshipType,
    SensorEntity,
    HospitalEntity,
)


class BiomedicalKnowledgeGraph:
    """Knowledge graph for biomedical entities and relationships.

    Features:
    - Entity management (devices, manufacturers, hospitals, etc.)
    - Relationship management
    - Graph traversal (BFS, DFS)
    - Path finding
    - Inference engine
    - Versioning
    - Statistics
    """

    def __init__(self):
        """Initialize the knowledge graph."""
        self._entities: dict[str, BiomedicalEntity] = {}
        self._relationships: dict[str, Relationship] = {}
        self._adjacency: dict[str, dict[str, list[str]]] = defaultdict(lambda: {"in": [], "out": []})
        self._entities_by_type: dict[EntityType, set[str]] = defaultdict(set)
        self._ontology: dict[str, OntologyClass] = {}
        self._inference_rules: dict[str, InferenceRule] = {}
        self._versions: list[GraphVersion] = []

        self._lock = threading.RLock()

    # =========================================================================
    # Entity Management
    # =========================================================================

    def add_entity(self, entity: BiomedicalEntity) -> None:
        """Add an entity to the graph.

        Args:
            entity: Entity to add.
        """
        with self._lock:
            self._entities[entity.entity_id] = entity
            self._entities_by_type[entity.entity_type].add(entity.entity_id)
            self._adjacency[entity.entity_id] = {"in": [], "out": []}

    def get_entity(self, entity_id: str) -> BiomedicalEntity | None:
        """Get an entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            Entity or None.
        """
        return self._entities.get(entity_id)

    def get_entities_by_type(self, entity_type: EntityType) -> list[BiomedicalEntity]:
        """Get all entities of a type.

        Args:
            entity_type: Entity type.

        Returns:
            List of entities.
        """
        with self._lock:
            entity_ids = self._entities_by_type.get(entity_type, set())
            return [self._entities[eid] for eid in entity_ids if eid in self._entities]

    def update_entity(self, entity: BiomedicalEntity) -> None:
        """Update an entity.

        Args:
            entity: Updated entity.
        """
        with self._lock:
            if entity.entity_id in self._entities:
                entity.updated_at = datetime.now(UTC)
                self._entities[entity.entity_id] = entity

    def delete_entity(self, entity_id: str) -> None:
        """Delete an entity and its relationships.

        Args:
            entity_id: Entity ID.
        """
        with self._lock:
            if entity_id not in self._entities:
                return

            entity = self._entities[entity_id]
            self._entities_by_type[entity.entity_type].discard(entity_id)

            # Remove relationships
            for rel_id in list(self._relationships.keys()):
                rel = self._relationships[rel_id]
                if rel.source_id == entity_id or rel.target_id == entity_id:
                    self._remove_relationship_internal(rel_id)

            del self._entities[entity_id]
            del self._adjacency[entity_id]

    # =========================================================================
    # Relationship Management
    # =========================================================================

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the graph.

        Args:
            relationship: Relationship to add.
        """
        with self._lock:
            self._relationships[relationship.relationship_id] = relationship
            self._adjacency[relationship.source_id]["out"].append(relationship.relationship_id)
            self._adjacency[relationship.target_id]["in"].append(relationship.relationship_id)

    def get_relationship(self, relationship_id: str) -> Relationship | None:
        """Get a relationship by ID.

        Args:
            relationship_id: Relationship ID.

        Returns:
            Relationship or None.
        """
        return self._relationships.get(relationship_id)

    def get_relationships(
        self,
        entity_id: str,
        direction: str = "both",  # in, out, both
    ) -> list[Relationship]:
        """Get relationships for an entity.

        Args:
            entity_id: Entity ID.
            direction: Direction (in, out, both).

        Returns:
            List of relationships.
        """
        with self._lock:
            rel_ids = []
            if direction in ("out", "both"):
                rel_ids.extend(self._adjacency[entity_id]["out"])
            if direction in ("in", "both"):
                rel_ids.extend(self._adjacency[entity_id]["in"])

            return [self._relationships[rid] for rid in rel_ids if rid in self._relationships]

    def _remove_relationship_internal(self, relationship_id: str) -> None:
        """Internal method to remove a relationship."""
        rel = self._relationships[relationship_id]
        self._adjacency[rel.source_id]["out"].remove(relationship_id)
        self._adjacency[rel.target_id]["in"].remove(relationship_id)
        del self._relationships[relationship_id]

    def delete_relationship(self, relationship_id: str) -> None:
        """Delete a relationship.

        Args:
            relationship_id: Relationship ID.
        """
        with self._lock:
            if relationship_id in self._relationships:
                self._remove_relationship_internal(relationship_id)

    # =========================================================================
    # Graph Traversal
    # =========================================================================

    def traverse_bfs(
        self,
        start_id: str,
        max_depth: int = 3,
        relationship_types: list[RelationshipType] | None = None,
    ) -> GraphQueryResult:
        """Breadth-first traversal from a starting entity.

        Args:
            start_id: Starting entity ID.
            max_depth: Maximum traversal depth.
            relationship_types: Filter by relationship types.

        Returns:
            Query result with entities and relationships.
        """
        query_id = str(uuid.uuid4())
        visited: set[str] = {start_id}
        queue = [(start_id, 0)]
        result_entities: list[BiomedicalEntity] = []
        result_relationships: list[Relationship] = []

        with self._lock:
            if start_id not in self._entities:
                return GraphQueryResult(query_id=query_id)

            result_entities.append(self._entities[start_id])

            while queue:
                current_id, depth = queue.pop(0)

                if depth >= max_depth:
                    continue

                for rel in self.get_relationships(current_id, "out"):
                    if relationship_types and rel.relationship_type not in relationship_types:
                        continue

                    result_relationships.append(rel)

                    neighbor_id = rel.target_id
                    if neighbor_id not in visited and neighbor_id in self._entities:
                        visited.add(neighbor_id)
                        result_entities.append(self._entities[neighbor_id])
                        queue.append((neighbor_id, depth + 1))

        return GraphQueryResult(
            query_id=query_id,
            entities=result_entities,
            relationships=result_relationships,
            total_hops=max_depth,
        )

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
    ) -> list[list[str]]:
        """Find all paths between two entities.

        Args:
            source_id: Source entity ID.
            target_id: Target entity ID.
            max_depth: Maximum path depth.

        Returns:
            List of paths (each path is a list of entity IDs).
        """
        paths: list[list[str]] = []

        def dfs(current: str, target: str, path: list[str], visited: set[str]):
            if len(path) > max_depth:
                return

            if current == target:
                paths.append(path.copy())
                return

            for rel in self.get_relationships(current, "out"):
                neighbor = rel.target_id
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, target, path, visited)
                    path.pop()
                    visited.remove(neighbor)

        with self._lock:
            if source_id not in self._entities or target_id not in self._entities:
                return []

            visited = {source_id}
            dfs(source_id, target_id, [source_id], visited)

        return paths

    def find_connected(
        self,
        entity_id: str,
        relationship_type: RelationshipType | None = None,
        max_depth: int = 1,
    ) -> list[tuple[BiomedicalEntity, Relationship]]:
        """Find all entities connected to a given entity.

        Args:
            entity_id: Starting entity ID.
            relationship_type: Filter by relationship type.
            max_depth: Maximum depth.

        Returns:
            List of (entity, relationship) tuples.
        """
        results: list[tuple[BiomedicalEntity, Relationship]] = []

        def search(current_id: str, depth: int, visited: set[str]):
            if depth > max_depth or current_id in visited:
                return

            visited.add(current_id)

            for rel in self.get_relationships(current_id, "out"):
                if relationship_type and rel.relationship_type != relationship_type:
                    continue

                if rel.target_id in self._entities:
                    results.append((self._entities[rel.target_id], rel))
                    search(rel.target_id, depth + 1, visited)

        with self._lock:
            if entity_id in self._entities:
                search(entity_id, 0, set())

        return results

    # =========================================================================
    # Inference Engine
    # =========================================================================

    def add_inference_rule(self, rule: InferenceRule) -> None:
        """Add an inference rule.

        Args:
            rule: Inference rule to add.
        """
        with self._lock:
            self._inference_rules[rule.rule_id] = rule

    def infer(self) -> list[InferenceResult]:
        """Run inference and return new relationships.

        Returns:
            List of inference results.
        """
        results: list[InferenceResult] = []

        with self._lock:
            for rule_id, rule in self._inference_rules.items():
                if not rule.enabled:
                    continue

                inferred_rels = self._apply_rule(rule)
                if inferred_rels:
                    results.append(InferenceResult(
                        rule_id=rule_id,
                        inferred_relationships=inferred_rels,
                        confidence=rule.confidence,
                        explanation=f"Applied rule: {rule.name}",
                    ))

        return results

    def _apply_rule(self, rule: InferenceRule) -> list[Relationship]:
        """Apply an inference rule.

        Args:
            rule: Rule to apply.

        Returns:
            List of inferred relationships.
        """
        inferred: list[Relationship] = []

        # Simple pattern matching for conditions
        for entity_id, entity in self._entities.items():
            conditions_met = True

            for condition in rule.conditions:
                prop = condition.get("property")
                value = condition.get("value")
                op = condition.get("op", "eq")

                if prop and not hasattr(entity, prop):
                    conditions_met = False
                    break

                entity_value = getattr(entity, prop, None)
                if entity_value is None:
                    conditions_met = False
                    break

                if op == "eq" and entity_value != value:
                    conditions_met = False
                elif op == "ne" and entity_value == value:
                    conditions_met = False
                elif op == "contains" and value not in str(entity_value):
                    conditions_met = False

            if conditions_met:
                # Create inferred relationship
                rel = Relationship(
                    relationship_id=str(uuid.uuid4()),
                    source_id=entity_id,
                    target_id=rule.conclusion.get("target_id", ""),
                    relationship_type=RelationshipType(rule.conclusion.get("type", "")),
                    properties={"inferred": True, "rule_id": rule.rule_id},
                    weight=rule.confidence,
                )
                inferred.append(rel)

        return inferred

    # =========================================================================
    # Ontology
    # =========================================================================

    def add_ontology_class(self, ontology_class: OntologyClass) -> None:
        """Add an ontology class.

        Args:
            ontology_class: Ontology class to add.
        """
        with self._lock:
            self._ontology[ontology_class.class_id] = ontology_class

    def get_subclasses(self, class_id: str) -> list[str]:
        """Get all subclasses of a class.

        Args:
            class_id: Parent class ID.

        Returns:
            List of subclass IDs.
        """
        subclasses = []
        for cls_id, cls in self._ontology.items():
            if cls.parent == class_id:
                subclasses.append(cls_id)
                subclasses.extend(self.get_subclasses(cls_id))
        return subclasses

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_statistics(self) -> GraphStatistics:
        """Get graph statistics.

        Returns:
            Graph statistics.
        """
        with self._lock:
            stats = GraphStatistics()
            stats.total_entities = len(self._entities)
            stats.total_relationships = len(self._relationships)

            # Count by type
            for entity_type, entity_ids in self._entities_by_type.items():
                stats.entities_by_type[entity_type.value] = len(entity_ids)

            # Relationship counts
            rel_counts: dict[str, int] = defaultdict(int)
            for rel in self._relationships.values():
                rel_counts[rel.relationship_type.value] += 1
            stats.relationships_by_type = dict(rel_counts)

            # Degree calculation
            degrees = []
            for entity_id in self._entities:
                degree = len(self._adjacency[entity_id]["in"]) + len(self._adjacency[entity_id]["out"])
                degrees.append(degree)

            if degrees:
                stats.avg_degree = sum(degrees) / len(degrees)
                stats.max_degree = max(degrees)

            # Density
            n = len(self._entities)
            if n > 1:
                max_edges = n * (n - 1)
                stats.density = len(self._relationships) / max_edges

            return stats

    # =========================================================================
    # Versioning
    # =========================================================================

    def create_version(self, description: str = "") -> GraphVersion:
        """Create a new version snapshot.

        Args:
            description: Version description.

        Returns:
            Graph version.
        """
        stats = self.get_statistics()

        version = GraphVersion(
            version_id=str(uuid.uuid4()),
            version_number=f"{len(self._versions) + 1}.0",
            entities_added=stats.total_entities,
            relationships_added=stats.total_relationships,
            description=description,
        )

        self._versions.append(version)
        return version

    def get_versions(self) -> list[GraphVersion]:
        """Get all versions.

        Returns:
            List of versions.
        """
        return self._versions.copy()

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict:
        """Export graph to dictionary.

        Returns:
            Graph as dictionary.
        """
        with self._lock:
            return {
                "entities": {eid: e.to_dict() for eid, e in self._entities.items()},
                "relationships": {rid: r.to_dict() for rid, r in self._relationships.items()},
                "ontology": {cid: {"class_id": c.class_id, "name": c.name, "parent": c.parent}
                             for cid, c in self._ontology.items()},
                "statistics": self.get_statistics().__dict__,
            }

    @classmethod
    def from_dict(cls, data: dict) -> BiomedicalKnowledgeGraph:
        """Create graph from dictionary.

        Args:
            data: Dictionary representation.

        Returns:
            New graph instance.
        """
        graph = cls()

        # Load entities
        for eid, edata in data.get("entities", {}).items():
            entity_type = EntityType(edata["entity_type"])
            entity = BiomedicalEntity(
                entity_id=eid,
                entity_type=entity_type,
                name=edata["name"],
                description=edata.get("description", ""),
                properties=edata.get("properties", {}),
                metadata=edata.get("metadata", {}),
                tags=edata.get("tags", []),
            )
            graph.add_entity(entity)

        # Load relationships
        for rid, rdata in data.get("relationships", {}).items():
            rel = Relationship(
                relationship_id=rid,
                source_id=rdata["source_id"],
                target_id=rdata["target_id"],
                relationship_type=RelationshipType(rdata["relationship_type"]),
                properties=rdata.get("properties", {}),
                weight=rdata.get("weight", 1.0),
            )
            graph.add_relationship(rel)

        return graph


# =============================================================================
# Singleton
# =============================================================================

_global_graph: BiomedicalKnowledgeGraph | None = None
_graph_lock = threading.Lock()


def get_knowledge_graph() -> BiomedicalKnowledgeGraph:
    """Get the global knowledge graph instance.

    Returns:
        Global graph instance.
    """
    global _global_graph
    with _graph_lock:
        if _global_graph is None:
            _global_graph = BiomedicalKnowledgeGraph()
        return _global_graph


def reset_knowledge_graph() -> None:
    """Reset the global knowledge graph."""
    global _global_graph
    with _graph_lock:
        _global_graph = None
