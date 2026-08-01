# Sources

Accessed 2026-08-01 unless noted otherwise.

- Live problem statement and status: https://www.erdosproblems.com/167
- G. J. Puleo, *Tuza's Conjecture for Graphs of Maximum Average Degree Less
  Than 7*: https://arxiv.org/abs/1308.2211
- Brendan McKay, official simple-graph catalogues and counts:
  https://users.cecs.anu.edu.au/~bdm/data/graphs.html
- Exact order-ten catalogue used here:
  https://users.cecs.anu.edu.au/~bdm/data/graph10.g6.gz
- July 24 public through-order-nine report at frozen commit:
  https://github.com/txmy/ultra-mathematician/blob/d52f81ad64dfc77e9a89dee8ae97db983ac6d5f7/runs/run-2026-07-24-001/report.md
- July 24 public independent audit at frozen commit:
  https://github.com/txmy/ultra-mathematician/blob/d52f81ad64dfc77e9a89dee8ae97db983ac6d5f7/runs/run-2026-07-24-001/tasks/audit-tuza-order-nine/audit.md
- July 26 public order-ten feasibility discussion at frozen commit:
  https://github.com/txmy/ultra-mathematician/blob/d52f81ad64dfc77e9a89dee8ae97db983ac6d5f7/runs/run-2026-07-26-001/tasks/assess-cheap-discriminating-experiments/feasibility.md
- Public draft Lean statement (contains `sorry`, not a proof):
  https://github.com/ryantuck/erdos-ai/blob/c3de3e12ebee4ff540e806b909a2a8b07fe1983c/deepmind/167.lean

The draft Lean formulation quantifies over finite simple graphs, encodes
edge-disjoint triangles by pairwise vertex intersections of size at most one,
and asks for a triangle-free subgraph obtained by deleting at most `2*k`
edges.  It is faithful to the live informal statement, but its theorem body
and answer placeholder remain unproved.
