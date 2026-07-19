"""CIC Red Team Harness — Shared Utilities

Three utility modules:
- sat_utils: DPLL solver, unit propagation, backbone extraction
- graph_utils: Primal graph construction and analysis
- width_utils: MinFill treewidth estimation
"""

from .sat_utils import (
    dpll_solve,
    is_satisfiable,
    get_backbone,
    make_small_example,
    parse_dimacs,
    to_dimacs,
    unit_propagate,
    pure_literal_eliminate,
    eval_clause,
)

from .graph_utils import (
    build_primal_graph,
    build_incidence_graph,
    build_variable_graph,
    get_connected_components,
    graph_stats,
)

from .width_utils import (
    minfill_ordering,
    eliminate_node,
    get_width,
    random_ordering,
    estimate_difficulty,
)

__all__ = [
    # sat_utils
    "dpll_solve",
    "is_satisfiable",
    "get_backbone",
    "make_small_example",
    "parse_dimacs",
    "to_dimacs",
    "unit_propagate",
    "pure_literal_eliminate",
    "eval_clause",
    # graph_utils
    "build_primal_graph",
    "build_incidence_graph",
    "build_variable_graph",
    "get_connected_components",
    "graph_stats",
    # width_utils
    "minfill_ordering",
    "eliminate_node",
    "get_width",
    "random_ordering",
    "estimate_difficulty",
]
