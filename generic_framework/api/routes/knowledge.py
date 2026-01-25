#
# Copyright 2025 ExFrame Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Knowledge graph routes for Generic Framework.

Provides endpoints for querying and managing the knowledge graph.
Migrated from Expertise Scanner.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import json
from pathlib import Path

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class GraphNode(BaseModel):
    """Knowledge graph node."""
    id: str
    label: str
    type: str
    domain: str
    metadata: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    """Knowledge graph edge."""
    source: str
    target: str
    relationship: str  # "related", "prerequisite", "alternative"
    weight: float = 1.0


class GraphQuery(BaseModel):
    """Knowledge graph query."""
    start_node: str
    max_depth: int = 3
    relationship_types: Optional[List[str]] = None


# Knowledge graph storage
KNOWLEDGE_GRAPH_DIR = Path("data/knowledge_graph")


def load_graph() -> Dict[str, Any]:
    """Load knowledge graph from disk."""
    graph_file = KNOWLEDGE_GRAPH_DIR / "graph.json"
    
    if not graph_file.exists():
        return {"nodes": [], "edges": []}
    
    with open(graph_file) as f:
        return json.load(f)


def save_graph(graph: Dict[str, Any]) -> None:
    """Save knowledge graph to disk."""
    KNOWLEDGE_GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    
    graph_file = KNOWLEDGE_GRAPH_DIR / "graph.json"
    with open(graph_file, 'w') as f:
        json.dump(graph, f, indent=2)


def build_graph_from_patterns() -> Dict[str, Any]:
    """Build knowledge graph from patterns."""
    graph = {"nodes": [], "edges": []}
    patterns_dir = Path("data/patterns")
    
    if not patterns_dir.exists():
        return graph
    
    # Load all patterns and create nodes
    node_ids = set()
    for domain_dir in patterns_dir.glob("*/"):
        if not domain_dir.is_dir():
            continue
        
        domain = domain_dir.name
        
        for pattern_file in domain_dir.glob("*.json"):
            try:
                with open(pattern_file) as f:
                    pattern = json.load(f)
                
                pattern_id = pattern.get("id", pattern_file.stem)
                
                if pattern_id not in node_ids:
                    node = {
                        "id": pattern_id,
                        "label": pattern.get("name", "Unknown"),
                        "type": "pattern",
                        "domain": domain,
                        "metadata": {
                            "pattern_type": pattern.get("pattern_type"),
                            "confidence": pattern.get("confidence", 0.5),
                            "category": pattern.get("category"),
                        },
                    }
                    graph["nodes"].append(node)
                    node_ids.add(pattern_id)
                
                # Create edges for relationships
                for related_id in pattern.get("related_patterns", []):
                    edge = {
                        "source": pattern_id,
                        "target": related_id,
                        "relationship": "related",
                        "weight": 1.0,
                    }
                    graph["edges"].append(edge)
                
                for prereq_id in pattern.get("prerequisites", []):
                    edge = {
                        "source": prereq_id,
                        "target": pattern_id,
                        "relationship": "prerequisite",
                        "weight": 1.0,
                    }
                    graph["edges"].append(edge)
                
                for alt_id in pattern.get("alternatives", []):
                    edge = {
                        "source": pattern_id,
                        "target": alt_id,
                        "relationship": "alternative",
                        "weight": 0.5,
                    }
                    graph["edges"].append(edge)
            except Exception:
                continue
    
    return graph


@router.get("/graph", response_model=Dict[str, Any])
async def get_graph(
    domain: Optional[str] = Query(None),
    rebuild: bool = Query(False),
):
    """Get the knowledge graph."""
    if rebuild:
        # Rebuild from patterns
        graph = build_graph_from_patterns()
        save_graph(graph)
    else:
        # Load from disk
        graph = load_graph()
        
        # If empty, build from patterns
        if not graph["nodes"]:
            graph = build_graph_from_patterns()
            save_graph(graph)
    
    # Filter by domain if specified
    if domain:
        filtered_nodes = [n for n in graph["nodes"] if n.get("domain") == domain]
        node_ids = {n["id"] for n in filtered_nodes}
        filtered_edges = [e for e in graph["edges"] if e["source"] in node_ids and e["target"] in node_ids]
        
        return {
            "nodes": filtered_nodes,
            "edges": filtered_edges,
        }
    
    return graph


@router.get("/graph/nodes", response_model=List[GraphNode])
async def get_graph_nodes(
    domain: Optional[str] = Query(None),
    node_type: Optional[str] = Query(None),
):
    """Get all nodes in the knowledge graph."""
    graph = load_graph()
    
    if not graph["nodes"]:
        graph = build_graph_from_patterns()
    
    nodes = graph["nodes"]
    
    # Filter by domain
    if domain:
        nodes = [n for n in nodes if n.get("domain") == domain]
    
    # Filter by type
    if node_type:
        nodes = [n for n in nodes if n.get("type") == node_type]
    
    return [GraphNode(**n) for n in nodes]


@router.get("/graph/edges", response_model=List[GraphEdge])
async def get_graph_edges(
    relationship: Optional[str] = Query(None),
):
    """Get all edges in the knowledge graph."""
    graph = load_graph()
    
    if not graph["edges"]:
        graph = build_graph_from_patterns()
    
    edges = graph["edges"]
    
    # Filter by relationship type
    if relationship:
        edges = [e for e in edges if e.get("relationship") == relationship]
    
    return [GraphEdge(**e) for e in edges]


@router.post("/graph/query", response_model=Dict[str, Any])
async def query_graph(query: GraphQuery):
    """Query the knowledge graph."""
    graph = load_graph()
    
    if not graph["nodes"]:
        graph = build_graph_from_patterns()
    
    # Find start node
    start_node = None
    for node in graph["nodes"]:
        if node["id"] == query.start_node:
            start_node = node
            break
    
    if not start_node:
        raise HTTPException(status_code=404, detail=f"Node {query.start_node} not found")
    
    # BFS to find connected nodes
    visited = set()
    queue = [(query.start_node, 0)]
    result_nodes = [start_node]
    result_edges = []
    
    while queue:
        current_id, depth = queue.pop(0)
        
        if current_id in visited or depth >= query.max_depth:
            continue
        
        visited.add(current_id)
        
        # Find connected edges
        for edge in graph["edges"]:
            # Check relationship type filter
            if query.relationship_types and edge["relationship"] not in query.relationship_types:
                continue
            
            if edge["source"] == current_id:
                target_id = edge["target"]
                
                if target_id not in visited:
                    # Find target node
                    for node in graph["nodes"]:
                        if node["id"] == target_id:
                            result_nodes.append(node)
                            result_edges.append(edge)
                            queue.append((target_id, depth + 1))
                            break
            
            elif edge["target"] == current_id:
                source_id = edge["source"]
                
                if source_id not in visited:
                    # Find source node
                    for node in graph["nodes"]:
                        if node["id"] == source_id:
                            result_nodes.append(node)
                            result_edges.append(edge)
                            queue.append((source_id, depth + 1))
                            break
    
    return {
        "start_node": query.start_node,
        "nodes": result_nodes,
        "edges": result_edges,
        "depth": query.max_depth,
    }


@router.post("/graph/rebuild", response_model=Dict[str, Any])
async def rebuild_graph():
    """Rebuild the knowledge graph from patterns."""
    try:
        graph = build_graph_from_patterns()
        save_graph(graph)
        
        return {
            "status": "rebuilt",
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/stats", response_model=Dict[str, Any])
async def get_graph_stats():
    """Get statistics about the knowledge graph."""
    graph = load_graph()
    
    if not graph["nodes"]:
        graph = build_graph_from_patterns()
    
    # Calculate statistics
    nodes = graph["nodes"]
    edges = graph["edges"]
    
    domains = {}
    for node in nodes:
        domain = node.get("domain", "unknown")
        domains[domain] = domains.get(domain, 0) + 1
    
    relationships = {}
    for edge in edges:
        rel_type = edge.get("relationship", "unknown")
        relationships[rel_type] = relationships.get(rel_type, 0) + 1
    
    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "domains": domains,
        "relationships": relationships,
        "avg_degree": len(edges) * 2 / len(nodes) if nodes else 0,
    }
