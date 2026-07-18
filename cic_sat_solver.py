"""
CIC SAT Solver v1 - Basic CDCL with Structural Analysis
"""

import sys
import random
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict

class CICSATSolver:
    """Basic CDCL SAT solver with structural feature extraction."""
    
    def __init__(self):
        self.clauses: List[List[int]] = []
        self.n_vars = 0
        self.assignment: Dict[int, bool] = {}
        self.decision_level = 0
        self.learned_clauses: List[List[int]] = []
        
        # VSIDS scores
        self.var_scores: Dict[int, float] = defaultdict(float)
        self.var_inc = 1.0
        
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
    
    def unit_propagate(self) -> Optional[List[int]]:
        """Perform unit propagation. Returns conflict clause if any."""
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
                    return clause  # Conflict
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    self.assignment[lit] = True
                    self.assignment[-lit] = False
                    changed = True
        
        return None
    
    def vsids_branch(self) -> int:
        """Select branching variable using VSIDS heuristic."""
        best_var = None
        best_score = -1.0
        
        for var in range(1, self.n_vars + 1):
            if var not in self.assignment and -var not in self.assignment:
                score = self.var_scores.get(var, 0) + self.var_scores.get(-var, 0)
                if score > best_score:
                    best_score = score
                    best_var = var
        
        if best_var is None:
            return 0
        
        # Choose phase
        if self.var_scores.get(best_var, 0) >= self.var_scores.get(-best_var, 0):
            return best_var
        else:
            return -best_var
    
    def analyze_conflict(self, conflict: List[int]) -> Tuple[List[int], int]:
        """Analyze conflict and learn a clause (1-UIP)."""
        learned = list(conflict)
        
        # Simple learning: just use the conflict clause
        # In full implementation, this would compute the 1-UIP
        
        # Update VSIDS scores
        for lit in conflict:
            self.var_scores[abs(lit)] += self.var_inc
        
        return learned, max(0, self.decision_level - 1)
    
    def solve(self) -> Optional[Dict[int, bool]]:
        """Solve the SAT instance using CDCL."""
        # Initialize VSIDS scores
        for clause in self.clauses:
            for lit in clause:
                self.var_scores[abs(lit)] += 1.0
        
        decision_stack = []
        
        while True:
            conflict = self.unit_propagate()
            
            if conflict is not None:
                if self.decision_level == 0:
                    return None  # UNSAT
                
                learned, back_level = self.analyze_conflict(conflict)
                self.learned_clauses.append(learned)
                
                # Backtrack
                while len(decision_stack) > back_level:
                    lit = decision_stack.pop()
                    if lit in self.assignment:
                        del self.assignment[lit]
                    if -lit in self.assignment:
                        del self.assignment[-lit]
                
                self.decision_level = back_level
            else:
                branch_lit = self.vsids_branch()
                if branch_lit == 0:
                    return self.assignment  # SAT
                
                self.decision_level += 1
                self.assignment[branch_lit] = True
                self.assignment[-branch_lit] = False
                decision_stack.append(branch_lit)

def main():
    if len(sys.argv) < 2:
        print("Usage: python cic_sat_solver.py <cnf_file>")
        sys.exit(1)
    
    solver = CICSATSolver()
    solver.read_dimacs(sys.argv[1])
    
    result = solver.solve()
    
    if result:
        print("SATISFIABLE")
    else:
        print("UNSATISFIABLE")

if __name__ == "__main__":
    main()
