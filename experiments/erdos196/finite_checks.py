#!/usr/bin/env python3
"""Small exact finite checks retained from the negative Erdős 196 attempt.

These checks can falsify a proposed finite ordering, but no finite prefix can
prove or disprove the quantified statement about every infinite permutation.
Only the Python standard library is used.
"""

from __future__ import annotations

from itertools import permutations


def first_monotone_4ap(sequence: list[int]) -> dict[str, object] | None:
    if len(sequence) != len(set(sequence)):
        raise ValueError("the sequence must not repeat a value")
    if any(value < 0 for value in sequence):
        raise ValueError("the sequence must contain natural numbers")
    positions = {value: index for index, value in enumerate(sequence)}
    if not positions:
        return None
    maximum = max(positions)
    for start in range(maximum + 1):
        for difference in range(1, (maximum - start) // 3 + 1):
            values = [start + offset * difference for offset in range(4)]
            if not all(value in positions for value in values):
                continue
            indices = [positions[value] for value in values]
            if indices == sorted(indices) or indices == sorted(indices, reverse=True):
                return {
                    "start": start,
                    "difference": difference,
                    "values": values,
                    "indices": indices,
                }
    return None


def next_block_zero(block: list[int]) -> list[int]:
    return [2 * value for value in reversed(block)] + [
        2 * value + 1 for value in reversed(block)
    ]


def next_block_one(block: list[int]) -> list[int]:
    return [2 * value + 1 for value in reversed(block)] + [
        2 * value for value in reversed(block)
    ]


def dyadic_blocks(maximum_level: int) -> list[list[int]]:
    result = [[1]]
    for level in range(maximum_level):
        result.append((next_block_zero if level % 2 == 0 else next_block_one)(result[-1]))
    return result


def good_block_order_counts(maximum_level_count: int) -> list[int]:
    counts: list[int] = []
    for level_count in range(1, maximum_level_count + 1):
        blocks = dyadic_blocks(level_count - 1)
        good = 0
        for level_order in permutations(range(level_count)):
            sequence = [value for level in level_order for value in blocks[level]]
            if first_monotone_4ap(sequence) is None:
                good += 1
        counts.append(good)
    return counts


def append_largest_survivor_counts(maximum_level_count: int) -> list[int]:
    paths = [(0,)]
    blocks = dyadic_blocks(maximum_level_count - 1)
    counts = [1]
    for new_level in range(1, maximum_level_count):
        next_paths = []
        for path in paths:
            candidate = path + (new_level,)
            sequence = [value for level in candidate for value in blocks[level]]
            if first_monotone_4ap(sequence) is None:
                next_paths.append(candidate)
        paths = next_paths
        counts.append(len(paths))
    return counts


def safe_to_append(value: int, sequence: list[int], positions: dict[int, int]) -> bool:
    if value < 0 or any(item < 0 for item in sequence) or any(item < 0 for item in positions):
        raise ValueError("values must be natural numbers")
    if value in positions:
        return False
    maximum_used = max(sequence, default=0)

    # At the newest position, an increasing-value AP must end at `value`.
    for difference in range(1, value // 3 + 1):
        earlier = [value - 3 * difference, value - 2 * difference, value - difference]
        if all(item in positions for item in earlier):
            indices = [positions[item] for item in earlier]
            if indices[0] < indices[1] < indices[2]:
                return False

    # At the newest position, a decreasing-value AP must end at `value`.
    for difference in range(1, (maximum_used - value) // 3 + 1):
        earlier = [value + 3 * difference, value + 2 * difference, value + difference]
        if all(item in positions for item in earlier):
            indices = [positions[item] for item in earlier]
            if indices[0] < indices[1] < indices[2]:
                return False
    return True


def increasing_greedy(length: int) -> tuple[list[int], list[int]]:
    sequence: list[int] = []
    positions: dict[int, int] = {}
    permanently_blocked: list[int] = []
    candidate = 1
    while len(sequence) < length:
        while not safe_to_append(candidate, sequence, positions):
            permanently_blocked.append(candidate)
            candidate += 1
        positions[candidate] = len(sequence)
        sequence.append(candidate)
        candidate += 1
    return sequence, permanently_blocked


def main() -> None:
    zero_witness = first_monotone_4ap([0, 1, 2, 3])
    assert zero_witness == {
        "start": 0,
        "difference": 1,
        "values": [0, 1, 2, 3],
        "indices": [0, 1, 2, 3],
    }
    assert not safe_to_append(3, [0, 1, 2], {0: 0, 1: 1, 2: 2})

    blocks = dyadic_blocks(12)
    concatenated = [value for block in blocks for value in block]
    left = [value for level in range(2, len(blocks), 2) for value in reversed(blocks[level])]
    right = [value for level in range(1, len(blocks), 2) for value in blocks[level]]
    alternating = [blocks[0][0]]
    for index in range(max(len(left), len(right))):
        if index < len(right):
            alternating.append(right[index])
        if index < len(left):
            alternating.append(left[index])

    concatenated_witness = first_monotone_4ap(concatenated)
    alternating_witness = first_monotone_4ap(alternating)
    assert concatenated_witness == {
        "start": 1,
        "difference": 1,
        "values": [1, 2, 3, 4],
        "indices": [0, 1, 2, 6],
    }
    assert alternating_witness == {
        "start": 1,
        "difference": 2,
        "values": [1, 3, 5, 7],
        "indices": [0, 3, 6, 8],
    }

    order_counts = good_block_order_counts(8)
    append_counts = append_largest_survivor_counts(10)
    assert order_counts == [1, 2, 4, 6, 8, 10, 12, 14]
    assert append_counts == [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

    greedy, blocked = increasing_greedy(200)
    assert first_monotone_4ap(greedy) is None
    assert min(set(range(1, max(greedy) + 1)) - set(greedy)) == 4
    assert len(blocked) == max(greedy) - len(greedy) == 753

    print("zero-based witness:", zero_witness)
    print("concatenated dyadic witness:", concatenated_witness)
    print("alternating dyadic witness:", alternating_witness)
    print("good block-order counts for 1..8 levels:", order_counts)
    print("append-largest survivor counts for 1..10 levels:", append_counts)
    print(
        "increasing greedy length/max/least-missing/missing-count:",
        len(greedy),
        max(greedy),
        4,
        len(blocked),
    )
    print("finite checks: PASS; none addresses infinite surjectivity/global linkage")


if __name__ == "__main__":
    main()
