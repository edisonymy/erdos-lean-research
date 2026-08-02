#!/usr/bin/env python3
"""Small, dependency-free graph6 and (3,3)-Ramsey helpers.

The routines here deliberately target the small graphs used in the Erdos 151
catalogue audit.  They nevertheless implement all three graph6 order headers.
"""

from __future__ import annotations

import gzip
import hashlib
from pathlib import Path
from typing import Iterator, Sequence


GRAPH6_HEADER = b">>graph6<<"


def open_maybe_gzip(path: Path, mode: str = "rb"):
    if path.suffix.lower() == ".gz":
        return gzip.open(path, mode)
    return path.open(mode)


def iter_graph6(path: Path) -> Iterator[tuple[int, bytes, tuple[int, ...]]]:
    """Yield (one-based data-line index, graph6 record, adjacency masks)."""

    data_index = 0
    with open_maybe_gzip(path, "rb") as stream:
        for physical_line, line in enumerate(stream, 1):
            record = line.strip()
            if not record:
                continue
            if record == GRAPH6_HEADER:
                continue
            if record.startswith(GRAPH6_HEADER):
                record = record[len(GRAPH6_HEADER) :]
            try:
                adjacency = decode_graph6(record)
            except ValueError as exc:
                raise ValueError(f"{path}:{physical_line}: {exc}") from exc
            data_index += 1
            yield data_index, record, adjacency


def _decode_order(values: Sequence[int]) -> tuple[int, int]:
    if not values:
        raise ValueError("empty graph6 record")
    if values[0] != 63:
        return values[0], 1
    if len(values) < 4:
        raise ValueError("truncated extended graph6 order")
    if values[1] != 63:
        return (values[1] << 12) | (values[2] << 6) | values[3], 4
    if len(values) < 8:
        raise ValueError("truncated long graph6 order")
    order = 0
    for value in values[2:8]:
        order = (order << 6) | value
    return order, 8


def decode_graph6(record: bytes | str) -> tuple[int, ...]:
    """Decode one unlabelled graph6 record into integer adjacency masks."""

    if isinstance(record, str):
        record = record.encode("ascii")
    if record.startswith(GRAPH6_HEADER):
        record = record[len(GRAPH6_HEADER) :]
    try:
        values = [byte - 63 for byte in record]
    except TypeError as exc:
        raise ValueError("graph6 record must be ASCII bytes") from exc
    if any(value < 0 or value > 63 for value in values):
        raise ValueError("graph6 byte outside the printable 63..126 range")
    order, position = _decode_order(values)
    required_bits = order * (order - 1) // 2
    payload = values[position:]
    if len(payload) * 6 < required_bits:
        raise ValueError(
            f"truncated graph6 payload for order {order}: "
            f"need {required_bits} bits, have {len(payload) * 6}"
        )

    adjacency = [0] * order
    bit_index = 0
    for upper in range(1, order):
        for lower in range(upper):
            value = payload[bit_index // 6]
            bit = (value >> (5 - bit_index % 6)) & 1
            bit_index += 1
            if bit:
                adjacency[lower] |= 1 << upper
                adjacency[upper] |= 1 << lower
    return tuple(adjacency)


def _encode_order(order: int) -> list[int]:
    if order < 0 or order >= 1 << 36:
        raise ValueError("graph6 order must be in 0..2^36-1")
    if order <= 62:
        return [order]
    if order <= 258047:
        return [63, (order >> 12) & 63, (order >> 6) & 63, order & 63]
    return [63, 63] + [(order >> shift) & 63 for shift in range(30, -1, -6)]


def encode_graph6(adjacency: Sequence[int]) -> bytes:
    """Encode adjacency masks as one graph6 record (without newline)."""

    order = len(adjacency)
    values = _encode_order(order)
    payload: list[int] = []
    accumulator = 0
    used = 0
    for upper in range(1, order):
        for lower in range(upper):
            accumulator = (accumulator << 1) | ((adjacency[lower] >> upper) & 1)
            used += 1
            if used == 6:
                payload.append(accumulator)
                accumulator = 0
                used = 0
    if used:
        payload.append(accumulator << (6 - used))
    return bytes(value + 63 for value in values + payload)


def complement(adjacency: Sequence[int]) -> tuple[int, ...]:
    order = len(adjacency)
    all_vertices = (1 << order) - 1
    return tuple((~adjacency[v]) & (all_vertices ^ (1 << v)) for v in range(order))


def delete_edge(adjacency: Sequence[int], u: int, v: int) -> tuple[int, ...]:
    changed = list(adjacency)
    changed[u] &= ~(1 << v)
    changed[v] &= ~(1 << u)
    return tuple(changed)


def edges(adjacency: Sequence[int]) -> list[tuple[int, int]]:
    return [
        (u, v)
        for v in range(1, len(adjacency))
        for u in range(v)
        if (adjacency[u] >> v) & 1
    ]


def maximum_clique_size(adjacency: Sequence[int]) -> int:
    """Return omega(G) using a bitset branch-and-bound clique search."""

    best = 0

    def expand(candidates: int, size: int) -> None:
        nonlocal best
        while candidates:
            if size + candidates.bit_count() <= best:
                return
            bit = candidates & -candidates
            candidates ^= bit
            vertex = bit.bit_length() - 1
            expand(candidates & adjacency[vertex], size + 1)
        if size > best:
            best = size

    expand((1 << len(adjacency)) - 1, 0)
    return best


def independence_number(adjacency: Sequence[int]) -> int:
    return maximum_clique_size(complement(adjacency))


def triangle_edge_constraints(
    adjacency: Sequence[int],
) -> tuple[list[tuple[int, int]], list[tuple[int, int, int]]]:
    edge_list = edges(adjacency)
    edge_number = {edge: index for index, edge in enumerate(edge_list)}
    triangles: list[tuple[int, int, int]] = []
    order = len(adjacency)
    for c in range(2, order):
        for b in range(1, c):
            if not ((adjacency[b] >> c) & 1):
                continue
            for a in range(b):
                if ((adjacency[a] >> b) & 1) and ((adjacency[a] >> c) & 1):
                    triangles.append(
                        (
                            edge_number[(a, b)],
                            edge_number[(a, c)],
                            edge_number[(b, c)],
                        )
                    )
    return edge_list, triangles


def good_edge_coloring(adjacency: Sequence[int]) -> tuple[int, ...] | None:
    """Return a red/blue edge coloring with no monochromatic triangle, if any.

    This is a compact DPLL solver for the NAE-3-SAT instance whose variables are
    edges and whose constraints are triangles.  Global color-complement symmetry
    is removed by fixing the first edge to color zero.
    """

    edge_list, constraints = triangle_edge_constraints(adjacency)
    variable_count = len(edge_list)
    if not constraints:
        return tuple(0 for _ in edge_list)

    constraint_masks = [sum(1 << variable for variable in item) for item in constraints]
    incidence: list[list[int]] = [[] for _ in range(variable_count)]
    for constraint_index, constraint in enumerate(constraints):
        for variable in constraint:
            incidence[variable].append(constraint_index)
    incidence_masks = [
        sum(1 << constraint_index for constraint_index in items) for items in incidence
    ]
    all_active = (1 << len(constraints)) - 1

    def propagate(
        red: int,
        blue: int,
        red_touch: int,
        blue_touch: int,
        active: int,
        variable: int,
        color: int,
    ) -> tuple[int, int, int, int, int] | None:
        pending = [(variable, color)]
        while pending:
            current, value = pending.pop()
            bit = 1 << current
            if bit & (red | blue):
                if bool(bit & blue) != bool(value):
                    return None
                continue
            incident = incidence_masks[current]
            if value:
                blue |= bit
                blue_touch |= incident
                active &= ~(incident & red_touch)
            else:
                red |= bit
                red_touch |= incident
                active &= ~(incident & blue_touch)
            affected = incident & active
            while affected:
                constraint_bit = affected & -affected
                constraint_index = constraint_bit.bit_length() - 1
                affected ^= constraint_bit
                mask = constraint_masks[constraint_index]
                red_part = mask & red
                blue_part = mask & blue
                colored = red_part | blue_part
                if colored == mask:
                    return None
                if colored.bit_count() == 2:
                    missing = mask ^ colored
                    missing_variable = missing.bit_length() - 1
                    pending.append((missing_variable, 0 if blue_part else 1))
        return red, blue, red_touch, blue_touch, active

    def choose_variable(
        red: int, blue: int, red_touch: int, blue_touch: int, active: int
    ) -> int | None:
        if not active:
            return None
        assigned = red | blue
        touched_active = active & (red_touch | blue_touch)
        best = -1
        best_score = -1
        for variable, incident in enumerate(incidence_masks):
            if (assigned >> variable) & 1:
                continue
            # This is the earlier dynamic score without per-constraint loops:
            # unresolved triangles with one assigned edge get weight four,
            # while completely unassigned triangles get weight one.
            score = (incident & active).bit_count() + 3 * (
                incident & touched_active
            ).bit_count()
            if score > best_score:
                best = variable
                best_score = score
        return best

    def search(
        red: int, blue: int, red_touch: int, blue_touch: int, active: int
    ) -> tuple[int, int, int, int, int] | None:
        variable = choose_variable(red, blue, red_touch, blue_touch, active)
        if variable is None:
            return red, blue, red_touch, blue_touch, active
        for color in (0, 1):
            propagated = propagate(
                red, blue, red_touch, blue_touch, active, variable, color
            )
            if propagated is not None:
                result = search(*propagated)
                if result is not None:
                    return result
        return None

    initial = propagate(0, 0, 0, 0, all_active, constraints[0][0], 0)
    if initial is None:
        return None
    result = search(*initial)
    if result is None:
        return None
    _red, blue, _red_touch, _blue_touch, _active = result
    return tuple((blue >> variable) & 1 for variable in range(variable_count))


def arrows_33(adjacency: Sequence[int]) -> bool:
    return good_edge_coloring(adjacency) is None


def is_minimal_ramsey_33(adjacency: Sequence[int]) -> bool:
    if not arrows_33(adjacency):
        return False
    return all(not arrows_33(delete_edge(adjacency, u, v)) for u, v in edges(adjacency))


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_decompressed(path: Path) -> str:
    digest = hashlib.sha256()
    with open_maybe_gzip(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()
