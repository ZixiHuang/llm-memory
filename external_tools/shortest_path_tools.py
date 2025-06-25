"""
Internal helpers for the recursive-graph task.

Only `inspect`, `move`, and `submit` are exposed as tools.
`load_graph` is called once from ShortestPathGame._on_start and is NOT listed
in tools_avail or tool_schemas.
"""
from graphs.recursive_graph import RecursiveGraphGenerator, Graph

G: Graph  # cached graph instance

def _load_graph(configs: dict) -> dict:
    global G
    G = RecursiveGraphGenerator(
        base_nodes=configs["base_nodes"],
        max_edges=configs["max_edges"],
        recursion_depth=configs["recursion_depth"],
        weight_range=tuple(configs["weight_range"]),
        seed=configs["seed"],
    ).build()
    G.current = G.start  # type: ignore[attr-defined]
    return {"start": G.start, "end": G.end, "optimal_cost": G.optimal_path_cost}


# ----------------------- public tool functions ----------------------- #
def inspect() -> list[tuple[int, float]]:
    """Return (neighbor, weight) list at current node."""
    return G.neighbors(G.current)  # type: ignore[attr-defined]


def move(v: int) -> list[tuple[int, float]]:
    """Move to neighbor v and return its neighbors."""
    if v not in [n for n, _ in G.neighbors(G.current)]:  # type: ignore[attr-defined]
        raise ValueError(f"{v} is not a neighbor of {G.current}")
    G.current = v  # type: ignore[attr-defined]
    return G.neighbors(v)


def submit(path: list[int]) -> bool:
    """Submit a candidate path; returns True if optimal."""
    return G.verify_shortest_path(path)
