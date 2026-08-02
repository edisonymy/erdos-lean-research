"""Engine A: exact beta(G) via maximal-clique enumeration + RC2 MaxSAT.

beta(G) = max |S| such that S contains no inclusion-maximal clique of G
having at least two vertices.  Equivalently n - tau(G) where tau is the
clique-transversal number.  This module is the primary search engine;
engine B (beta_bb.py) shares no graph or solver code and is used for
independent confirmation of any interesting value.
"""

from __future__ import annotations

import networkx as nx
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF


def graphs_from_g6_file(path, limit=None):
    with open(path, "rb") as fh:
        for i, line in enumerate(fh):
            if limit is not None and i >= limit:
                return
            line = line.strip()
            if line:
                yield nx.from_graph6_bytes(line)


def maximal_cliques_ge2(G):
    """Inclusion-maximal cliques of G with at least two vertices."""
    return [frozenset(c) for c in nx.find_cliques(G) if len(c) >= 2]


def beta_maxsat(G, cliques=None):
    """Exact beta via RC2: minimize excluded vertices hitting all cliques."""
    n = G.number_of_nodes()
    if cliques is None:
        cliques = maximal_cliques_ge2(G)
    if not cliques:
        return n, set()
    idx = {v: i + 1 for i, v in enumerate(G.nodes())}
    wcnf = WCNF()
    for K in cliques:
        wcnf.append([-idx[v] for v in K])
    for v in G.nodes():
        wcnf.append([idx[v]], weight=1)
    with RC2(wcnf) as rc2:
        model = rc2.compute()
        cost = rc2.cost
    kept = {v for v in G.nodes() if model[idx[v] - 1] > 0}
    beta = n - cost
    assert len(kept) == beta
    _assert_admissible(kept, cliques)
    return beta, kept


def _assert_admissible(S, cliques):
    for K in cliques:
        if K <= S:
            raise AssertionError(f"engine A returned non-admissible set: {sorted(K)}")


def beta_bruteforce(G):
    """Reference for selftest only: try subset sizes from n downward."""
    from itertools import combinations
    n = G.number_of_nodes()
    cliques = maximal_cliques_ge2(G)
    nodes = list(G.nodes())
    for size in range(n, 0, -1):
        for S in combinations(nodes, size):
            fs = set(S)
            if not any(K <= fs for K in cliques):
                return size
    return 0
