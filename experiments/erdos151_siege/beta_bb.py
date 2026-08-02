"""Engine B: independent exact beta(G) computation.

Shares NO graph, parsing, or solver code with engine A (beta_lib.py):
- own graph6 parser (from the format definition);
- own maximal-clique enumeration (Bron-Kerbosch with pivot, bitsets);
- beta = n - tau, with the clique-transversal number tau computed by a
  branch-and-bound minimum hitting set over the maximal cliques.

Used to independently confirm every interesting value produced by
engine A, and to verify candidate witnesses from a raw edge list.
"""

from __future__ import annotations


def parse_g6_line(line):
    """graph6 -> (n, adj) with adj a list of int bitmasks."""
    s = line.strip()
    if isinstance(s, str):
        s = s.encode()
    if s.startswith(b">>graph6<<"):
        s = s[10:]
    data = [c - 63 for c in s]
    if any(d < 0 or d > 63 for d in data):
        raise ValueError("bad graph6 byte")
    if data[0] <= 62:
        n = data[0]
        bits_start = 1
    else:
        raise ValueError("only n<=62 supported here")
    adj = [0] * n
    need = n * (n - 1) // 2
    bitpos = 0
    stream = data[bits_start:]
    for j in range(1, n):
        for i in range(j):
            byte_i, off = divmod(bitpos, 6)
            bit = (stream[byte_i] >> (5 - off)) & 1
            bitpos += 1
            if bit:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    if bitpos != need:
        raise ValueError("bit count mismatch")
    return n, adj


def adj_from_edges(n, edges):
    adj = [0] * n
    for u, v in edges:
        if u == v or not (0 <= u < n and 0 <= v < n):
            raise ValueError("bad edge")
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def maximal_cliques_bitset(n, adj):
    """Bron-Kerbosch with pivot; returns maximal cliques as bitmasks."""
    out = []
    full = (1 << n) - 1

    def bk(R, P, X):
        if P == 0 and X == 0:
            if bin(R).count("1") >= 2:
                out.append(R)
            return
        PX = P | X
        # pivot: vertex of P|X maximizing |P & N(u)|
        best_u, best_cnt = -1, -1
        m = PX
        while m:
            u = (m & -m).bit_length() - 1
            m &= m - 1
            cnt = bin(P & adj[u]).count("1")
            if cnt > best_cnt:
                best_cnt, best_u = cnt, u
        cand = P & ~adj[best_u]
        while cand:
            v = (cand & -cand).bit_length() - 1
            cand &= cand - 1
            vb = 1 << v
            bk(R | vb, P & adj[v], X & adj[v])
            P &= ~vb
            X |= vb
    bk(0, full, 0)
    return out


def _greedy_disjoint_lb(cliques):
    used = 0
    cnt = 0
    for K in cliques:
        if K & used == 0:
            cnt += 1
            used |= K
    return cnt


def tau_hitting(n, cliques, ub=None):
    """Exact minimum hitting set size over clique bitmasks (B&B)."""
    if not cliques:
        return 0
    if ub is None:
        # greedy upper bound: repeatedly take highest-frequency vertex
        rem = list(cliques)
        hit = 0
        while rem:
            counts = [0] * n
            for K in rem:
                m = K
                while m:
                    v = (m & -m).bit_length() - 1
                    m &= m - 1
                    counts[v] += 1
            v = max(range(n), key=lambda i: counts[i])
            hit += 1
            rem = [K for K in rem if not (K >> v) & 1]
        ub = hit
    best = [ub]

    def bb(rem, size):
        if size >= best[0]:
            return
        if not rem:
            best[0] = size
            return
        if size + _greedy_disjoint_lb(rem) >= best[0]:
            return
        # branch on a smallest remaining clique
        K = min(rem, key=lambda k: bin(k).count("1"))
        m = K
        while m:
            v = (m & -m).bit_length() - 1
            m &= m - 1
            bb([c for c in rem if not (c >> v) & 1], size + 1)
    bb(list(cliques), 0)
    return best[0]


def beta_engine_b(n, adj):
    cliques = maximal_cliques_bitset(n, adj)
    return n - tau_hitting(n, cliques)


def check_witness_beta_le(n, edges, bound):
    """Independent verdict: is beta(G) <= bound for the given edge list?"""
    adj = adj_from_edges(n, edges)
    return beta_engine_b(n, adj) <= bound
