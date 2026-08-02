"""Finite arithmetic check for ORDER41_K5_DOUBLE_SATURATION.md.

This is not a graph search.  It checks the shared-w accounting identity on
small dummy values and the final inequality for the catalogue-conditional
edge range e(U) in {20,21,22}.
"""


DEGREE_BUDGET_U = 12 * 9
MIN_SPOKE_CUT = 19
CORE_EDGE_COUNTS = (20, 21, 22)
MAX_R = 7


def main():
    # If f_p and f_q count the U-to-four-fan edges, then the two five-spoke
    # cuts count the shared U-w edges once each.  The actual U-degree sum
    # counts those edges once, hence the correction by -r.
    identity_cases = 0
    for e_u in range(4):
        for f_p in range(4):
            for f_q in range(4):
                for f_3 in range(4):
                    for f_4 in range(4):
                        for f_5 in range(4):
                            for r in range(4):
                                sum_spoke_cuts = (
                                    (f_p + r) + (f_q + r)
                                    + f_3 + f_4 + f_5
                                )
                                direct = (
                                    2 * e_u + f_p + f_q
                                    + f_3 + f_4 + f_5 + r
                                )
                                corrected = 2 * e_u + sum_spoke_cuts - r
                                assert direct == corrected
                                identity_cases += 1

    minima = {}
    feasible_states = []
    for e_u in CORE_EDGE_COUNTS:
        values = []
        for r in range(MAX_R + 1):
            lower_degree_sum = 2 * e_u + 5 * MIN_SPOKE_CUT - r
            values.append(lower_degree_sum)
            if lower_degree_sum <= DEGREE_BUDGET_U:
                feasible_states.append((e_u, r, lower_degree_sum))
        minima[e_u] = min(values)

    assert minima == {20: 128, 21: 130, 22: 132}
    assert feasible_states == []

    print("status: CHECKED")
    print(f"shared_w_identity_cases: {identity_cases}")
    print("minimum_U_degree_sums: e20->128, e21->130, e22->132")
    print(f"available_U_degree_budget: {DEGREE_BUDGET_U}")
    print("feasible_states: 0")
    print("scope: arithmetic only; no graph or catalogue search")


if __name__ == "__main__":
    main()
