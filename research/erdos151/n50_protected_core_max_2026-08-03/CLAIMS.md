# Claim boundary

## Proved in this packet

1. If `G` is `K4`-free, has 50 vertices, and `beta(G)<=10`, then
   `beta(G)=10` and every degree is 9 or 10.
2. No such `G` is itself an edge-minimal graph arrowing `(3,3)`.
3. Consequently, every hypothetical order-50 `K4`-free counterexample has
   a **proper** edge-minimal arrowing core.  The ambient/core slack may be a
   non-core ambient edge on the same vertex set; the claim does not force a
   vertex outside the core.
4. There is no 24-vertex `K4`-free graph in the balanced, nonreciprocal,
   uniform type-5 subclass defined and certified in
   `TYPE5_BALANCED_NONRECIPROCAL.md`.
5. Every order-50 `K4`-free graph with `beta<=10` contains an
   ambient-maximal edge (an edge lying in no triangle).  The audited
   Lovasz-partition/Brooks proof is in
   `PURE_TRIANGULAR_CHROMATIC_GATE.md`.
6. More strongly, the ambient-maximal-edge graph of every such graph has a
   matching of size at least three.  This follows from the nine-color-class
   remainder argument proved in the same audit note.

## Imported, hash-pinned dependencies

- the unconditional order-41 theorem `K4-free => beta>=10`;
- its independent audit;
- the uniform degree-saturation inequality;
- the direct ten-template link census, used as an independent finite replay
  of the order-ten link gate.

## Not claimed

- No order-50 counterexample has been found or excluded.
- The pure-core theorem alone does not exclude a proper protected core.
- The type-5 certificate does not exclude reciprocal or endpoint-imbalanced
  uniform type-5 cores, nor uniform type-5 cores of other orders.
- No local link-compatible graph is asserted to arrow `(3,3)` or to have
  ambient `beta<=10`.
- No novelty or literature-priority claim is made.
