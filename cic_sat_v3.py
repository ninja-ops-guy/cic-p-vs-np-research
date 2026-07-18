"""
CIC SAT Solver v3 - GNN-based Variable Ordering
"""

import sys
import random
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict

class CICSATv3:
    """SAT solver with GNN-inspired variable ordering."""
    
    def __init__(self):
        self.clauses: List[List[int]] = []
        self.n_vars = 0
        self.assignment: Dict[int, bool] = {}
        self.decision_level = 0
        self.learned_clauses: List[List[int]] = []
        
        # VSIDS scores
        self.var_scores: Dict[int, float] = defaultdict(float)
        self.var_inc = 1.0
        self.var_decay = 0.95
        
        # Graph features
        self.var_degree = defaultdict(int)
        self.clause_degree = defaultdict(int)
        self.var_community = {}
        
    def read_dimacs(self, filename: str):
        """Read CNF formula in DIMACS format."""
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('c'):
                    continue
                if line.startswith('p'):
                    parts = line.split()
                    self.n_vars = int(parts[2])
                else:
                    literals = list(map(int, line.split()))
                    if literals[-1] == 0:
                        literals = literals[:-1]
                    self.clauses.append(literals)
        
        # Compute graph features
        self._compute_graph_features()
    
    def _compute_graph_features(self):
        """Compute variable-clause graph features."""
        for ci, clause in enumerate(self.clauses):
            self.clause_degree[ci] = len(clause)
            for lit in clause:
                self.var_degree[abs(lit)] += 1
    
    def unit_propagate(self) -> Optional[List[int]]:
        """Perform unit propagation."""
        changed = True
        while changed:
            changed = False
            for clause in self.clauses + self.learned_clauses:
                unassigned = []
                satisfied = False
                
                for lit in clause:
                    if lit in self.assignment and self.assignment[lit]:
                        satisfied = True
                        break
                    if -lit not in self.assignment:
                        unassigned.append(lit)
                
                if satisfied:
                    continue
                if len(unassigned) == 0:
                    return clause
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    self.assignment[lit] = True
                    self.assignment[-lit] = False
                    changed = True
        
        return None
    
    def gnn_inspired_branch(self) -> int:
        """GNN-inspired variable selection."""
        best_var = None
        best_score = -1.0
        
        for var in range(1, self.n_vars + 1):
            if var not in self.assignment and -var not in self.assignment:
                # Combine VSIDS with graph features
                vsids_score = self.var_scores.get(var, 0) + self.var_scores.get(-var, 0)
                degree_score = self.var_degree.get(var, 0)
                
                # Simple "message passing": score neighbors
                neighbor_score = 0
                for clause in self.clauses:
                    if var in [abs(lit) for lit in clause]:
                        for lit in clause:
                            if abs(lit) != var:
                                neighbor_score += self.var_scores.get(abs(lit), 0)
                
                # Combined score
                score = vsids_score + 0.1 * degree_score + 0.01 * neighbor_score
                
                if score > best_score:
                    best_score = score
                    best_var = var
        
        if best_var is None:
            return 0
        
        if self.var_scores.get(best_var, 0) >= self.var_scores.get(-best_var, 0):
            return best_var
        else:
            return -best_var
    
    def analyze_conflict(self, conflict: List[int]) -> Tuple[List[int], int]:
        """Analyze conflict and learn clause."""
        learned = list(conflict)
        
        for lit in conflict:
            self.var_scores[abs(lit)] += self.var_inc
        
        self.var_inc *= (1.0 / self.var_decay)
        
        return learned, max(0, self.decision_level - 1)
    
    def solve(self) -> Optional[Dict[int, bool]]:
        """Solve using GNN-inspired CDCL."""
        # Initialize VSIDS scores
        for clause in self.clauses:
            for lit in clause:
                self.var_scores[abs(lit)] += 1.0
        
        decision_stack = []
        
        while True:
            conflict = self.unit_propagate()
            
            if conflict is not None:
                if self.decision_level == 0:
                    return None
                
                learned, back_level = self.analyze_conflict(conflict)
                self.learned_clauses.append(learned)
                
                while len(decision_stack) > back_level:
                    lit = decision_stack.pop()
                    if lit in self.assignment:
                        del self.assignment[lit]
                    if -lit in self.assignment:
                        del self.assignment[-lit]
                
                self.decision_level = back_level
            else:
                branch_lit = self.gnn_inspired_branch()
                if branch_lit == 0:
                    return self.assignment
                
                self.decision_level += 1
                self.assignment[branch_lit] = True
                self.assignment[-branch_lit] = False
                decision_stack.append(branch_lit)

def main():
    if len(sys.argv) < 2:
        print("Usage: python cic_sat_v3.py <cnf_file>")
        sys.exit(1)
    
    solver = CICSATv3()
    solver.read_dimacs(sys.argv[1])
    
    result = solver.solve()
    
    if result:
        print("SATISFIABLE")
    else:
        print("UNSATISFIABLE")

if __name__ == "__main__":
    main()
