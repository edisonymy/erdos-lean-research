import LRATCatcher.Reflect

/-!
# Lean replay of the six Erdős #742 fixed-five CNFs

Each theorem below states that one exact generated DIMACS formula is
unsatisfiable.  The DIMACS text and LRAT proof are embedded at elaboration
time, and Lean's formally verified LRAT checker is run through
`native_decide` by LRAT-Catcher.

This file does **not** prove that the Python-generated CNFs faithfully encode
the graph-theoretic problem.  That correspondence remains in the separately
documented computational trust boundary.
-/

namespace Erdos742.Fixed5

lrat_reflect t2_path_unsat
  "../../../../.tmp/erdos742-order5-fixed5-lean/t2_path/case.cnf"
  "../../../../.tmp/erdos742-order5-fixed5-lean/t2_path/case.direct.lrat"

lrat_reflect t2_matching_unsat
  "../../../../.tmp/erdos742-order5-fixed5-lean/t2_matching/case.cnf"
  "../../../../.tmp/erdos742-order5-fixed5-lean/t2_matching/case.direct.lrat"

lrat_reflect t7_comp_triangle_unsat
  "../../../../.tmp/erdos742-order5-fixed5-lean/t7_comp_triangle/case.cnf"
  "../../../../.tmp/erdos742-order5-fixed5-lean/t7_comp_triangle/case.direct.lrat"

lrat_reflect t7_comp_star_unsat
  "../../../../.tmp/erdos742-order5-fixed5-lean/t7_comp_star/case.cnf"
  "../../../../.tmp/erdos742-order5-fixed5-lean/t7_comp_star/case.direct.lrat"

lrat_reflect t7_comp_path4_unsat
  "../../../../.tmp/erdos742-order5-fixed5-lean/t7_comp_path4/case.cnf"
  "../../../../.tmp/erdos742-order5-fixed5-lean/t7_comp_path4/case.direct.lrat"

lrat_reflect t7_comp_path3_edge_unsat
  "../../../../.tmp/erdos742-order5-fixed5-lean/t7_comp_path3_edge/case.cnf"
  "../../../../.tmp/erdos742-order5-fixed5-lean/t7_comp_path3_edge/case.direct.lrat"

#print axioms t2_path_unsat
#print axioms t2_matching_unsat
#print axioms t7_comp_triangle_unsat
#print axioms t7_comp_star_unsat
#print axioms t7_comp_path4_unsat
#print axioms t7_comp_path3_edge_unsat

end Erdos742.Fixed5
