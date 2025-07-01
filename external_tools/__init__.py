"""
Tools exposed to the RSP agent.
"""
from typing import List, Tuple
from graphs.recursive_graph import Graph, RecursiveGraphGenerator

# These globals will be initialised once per episode by the Game handler
G: Graph | None = None
_current: int | None = None      # agent's current node
_path: List[int] = []            # growing path (for convenience)

# --------------------------------------------------------------------------- #
# Helper to build a fresh graph each game                                     #
# --------------------------------------------------------------------------- #
def _init_graph(**kw):
    global G, _current, _path
    G = RecursiveGraphGenerator(**kw).build()
    _current = G.start
    _path = [G.start]


# --------------------------------------------------------------------------- #
# TOOLS                                                                       #
# --------------------------------------------------------------------------- #
def observe() -> List[Tuple[int, float]]:
    """
    Returns a list of (neighbor_id, weight) pairs for the current node.
    """
    assert G is not None and _current is not None
    return G.neighbors(_current)


def move(v: int) -> str:
    """
    Move the agent to neighbor `v`. Returns a confirmation string.
    Raises if v is not an outgoing neighbor.
    """
    assert G is not None and _current is not None
    if v not in [dst for dst, _ in G.neighbors(_current)]:
        raise ValueError(f"{v} is not a neighbor of current node.")
    _path.append(v)
    globals()['_current'] = v
    return f"Moved to node {v}."


def submit_solution(path: list[int]) -> bool:
    """
    Agent submits a candidate start→end path.  Returns True if **optimal**.
    """
    assert G is not None
    return G.verify_shortest_path(path)
