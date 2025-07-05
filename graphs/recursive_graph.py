from __future__ import annotations

import heapq
import random
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

###############################################################################
# Graph container                                                             #
###############################################################################

@dataclass(slots=True)
class Graph:
    """
    Lightweight adjacency-list digraph.

    `adj[u]` → list of `(v, w)` tuples (edge u→v with weight w).
    """

    adj: Dict[int, List[Tuple[int, float]]]
    start: int
    end: int
    optimal_path_cost: float         # minimal total weight start→end
    optimal_path: List[int]          # sequence of node IDs achieving that cost

    # ------------------------------------------------------------------#
    # Basic helpers                                                      #
    # ------------------------------------------------------------------#
    def neighbors(self, u: int) -> List[Tuple[int, float]]:
        return self.adj.get(u, [])

    def undirected_neighbors(self, u: int) -> List[int]:
        """
        Return neighbor node IDs for undirected exploration - includes both outgoing and incoming edges.
        For incoming edges, we traverse the graph to find all nodes that have edges to u.
        Returns only node IDs, no weights.
        """
        neighbors_set = set()
        
        # Add outgoing neighbors
        for v, w in self.adj.get(u, []):
            neighbors_set.add(v)
        
        # Add incoming neighbors (reverse direction)
        for node, edges in self.adj.items():
            for target, weight in edges:
                if target == u and node != u:
                    neighbors_set.add(node)
        
        return list(neighbors_set)

    def n_nodes(self) -> int:
        return len(self.adj)

    # ------------------------------------------------------------------#
    # Path utilities                                                     #
    # ------------------------------------------------------------------#
    def path_cost(self, path: List[int]) -> float:
        """Validate *path* and return its total weight."""
        if not path or path[0] != self.start or path[-1] != self.end:
            raise ValueError("Path must start at graph.start and finish at graph.end")

        cost = 0.0
        for u, v in zip(path, path[1:]):
            edge_map = {dst: w for dst, w in self.adj.get(u, [])}
            if v not in edge_map:
                raise ValueError(f"Edge {u}→{v} absent in graph")
            cost += edge_map[v]
        return cost

    def verify_shortest_path(self, path: List[int]) -> bool:
        """
        True iff *path* is valid **and** its cost equals the cached optimum
        (tolerance 1 e-9).
        """
        return abs(self.path_cost(path) - self.optimal_path_cost) < 1e-9


###############################################################################
# Recursive generator                                                         #
###############################################################################

class RecursiveGraphGenerator:
    """
    Build a recursively expandable, weighted digraph.

    Exactly one of `weight_choices` or `weight_range` must be provided.
    """

    # ------------------------------------------------------------------#
    # Constructor                                                        #
    # ------------------------------------------------------------------#
    def __init__(
        self,
        *,
        base_nodes: int,
        max_edges: int,
        recursion_depth: int,
        weight_choices: List[float] | None = None,
        weight_range: Tuple[float, float] | None = None,
        seed: int | None = None,
    ) -> None:
        if base_nodes < 2:
            raise ValueError("base_nodes must be ≥ 2")
        if max_edges < 1:
            raise ValueError("max_edges must be positive")
        if (weight_choices is None) == (weight_range is None):
            raise ValueError("Provide exactly one of weight_choices or weight_range")
        if weight_range is not None and weight_range[0] > weight_range[1]:
            raise ValueError("weight_range must satisfy lo ≤ hi")

        self.base_nodes = base_nodes
        self.max_edges = max_edges
        self.recursion_depth = recursion_depth
        self._rand = random.Random(seed)
        self._weight_choices = weight_choices
        self._weight_range = weight_range

        # Build base template
        self._tpl_start = 0
        self._tpl_end = base_nodes - 1
        self._tpl_adj = self._build_template()

        # Global node-id counter (template ids: 0 … base_nodes-1)
        self._next_id = self.base_nodes

    # ------------------------------------------------------------------#
    # Public API                                                         #
    # ------------------------------------------------------------------#
    def build(self) -> Graph:
        """Return the fully expanded graph with cached optimal path+cost."""
        # Copy template into global graph
        g_adj: Dict[int, List[Tuple[int, float]]] = {
            u: list(vs) for u, vs in self._tpl_adj.items()
        }
        g_start = 0
        g_end = self.base_nodes - 1  # updated as we recurse deeper

        # BFS expansion queue (node_id, depth)
        q = deque((u, 1) for u in range(self.base_nodes))

        while q:
            node_id, depth = q.popleft()
            if depth > self.recursion_depth:
                continue

            inner_nodes, sub_end = self._expand_node(node_id, g_adj)

            if node_id == g_end:
                g_end = sub_end

            if depth < self.recursion_depth:
                q.extend((v, depth + 1) for v in inner_nodes)

        # Compute global optimal path once
        opt_cost, opt_path = self._dijkstra_with_path(g_adj, g_start, g_end)

        return Graph(
            adj=g_adj,
            start=g_start,
            end=g_end,
            optimal_path_cost=opt_cost,
            optimal_path=opt_path,
        )

    # ------------------------------------------------------------------#
    # Template construction                                              #
    # ------------------------------------------------------------------#
    def _build_template(self) -> Dict[int, List[Tuple[int, float]]]:
        """Random connected base graph; end node has **no outgoing edges**."""
        adj: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(self.base_nodes)}

        # Backbone 0→1→…→N-1
        for u in range(self.base_nodes - 1):
            adj[u].append((u + 1, self._sample_weight()))

        end_node = self.base_nodes - 1

        # Extra edges (skip end_node as source)
        for u in range(self.base_nodes - 1):
            room = self.max_edges - len(adj[u])
            if room <= 0:
                continue
            k_extra = self._rand.randint(0, room)
            if k_extra == 0:
                continue
            existing = {dst for dst, _ in adj[u]}
            cand = [v for v in range(self.base_nodes) if v != u and v not in existing]
            for v in self._rand.sample(cand, k_extra):
                adj[u].append((v, self._sample_weight()))

        assert len(adj[end_node]) == 0, "Template end node must have no outgoing edges"
        return adj

    # ------------------------------------------------------------------#
    # Node expansion                                                     #
    # ------------------------------------------------------------------#
    def _expand_node(
        self,
        node_id: int,
        g_adj: Dict[int, List[Tuple[int, float]]],
    ) -> Tuple[List[int], int]:
        """Replace *node_id* with a fresh copy of the template."""
        outgoing = g_adj.get(node_id, [])
        g_adj[node_id] = []  # becomes sub-graph start

        # Map template ids → global ids  (start inherits node_id)
        mapping = {self._tpl_start: node_id}
        for t in range(self.base_nodes):
            if t == self._tpl_start:
                continue
            mapping[t] = self._next_id
            self._next_id += 1

        sub_end = mapping[self._tpl_end]

        # Clone edges with id remapping
        for t_src, t_edges in self._tpl_adj.items():
            g_src = mapping[t_src]
            dst_list = g_adj.setdefault(g_src, [])
            for t_dst, w in t_edges:
                dst_list.append((mapping[t_dst], w))

        # Re-attach original outgoing edges to sub-graph end
        g_adj[sub_end].extend(outgoing)

        inner_nodes = [gid for gid in mapping.values() if gid != node_id]
        return inner_nodes, sub_end

    # ------------------------------------------------------------------#
    # Weight sampler                                                     #
    # ------------------------------------------------------------------#
    def _sample_weight(self) -> float:
        if self._weight_choices is not None:
            return self._rand.choice(self._weight_choices)
        lo, hi = self._weight_range  # type: ignore[assignment]
        return self._rand.uniform(lo, hi)

    # ------------------------------------------------------------------#
    # Private: Dijkstra with path reconstruction                         #
    # ------------------------------------------------------------------#
    @staticmethod
    def _dijkstra_with_path(
        adj: Dict[int, List[Tuple[int, float]]],
        start: int,
        end: int,
    ) -> Tuple[float, List[int]]:
        pq: List[Tuple[float, int]] = [(0.0, start)]
        best: Dict[int, float] = {start: 0.0}
        prev: Dict[int, Optional[int]] = {start: None}

        while pq:
            cost_u, u = heapq.heappop(pq)
            if u == end:
                path: List[int] = []
                while u is not None:
                    path.append(u)
                    u = prev[u]
                return cost_u, path[::-1]

            if cost_u > best[u]:
                continue

            for v, w in adj.get(u, []):
                alt = cost_u + w
                if v not in best or alt < best[v]:
                    best[v] = alt
                    prev[v] = u
                    heapq.heappush(pq, (alt, v))

        raise ValueError("Graph is not connected from start to end")