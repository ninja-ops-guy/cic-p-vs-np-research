"""
CIC SAT Solver v2 - Portfolio with Automatic Selection
"""

import sys
import random
import time
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict

class CICSATv2:
    """SAT solver with portfolio selection."""
    
    def __init__(self):
        self.clauses: List[List[int]] = []
        self.n_vars = 0
        self.assignment: Dict[int, bool] = {}
        self.decision_level = 0
        self.learned_clauses: List[List[int]] = []
        
        # VSIDS
        self.var_scores: Dict[int, float] = defaultdict(float)
        self.var_inc = 1.0
        self.var_decay = 0.95
        
        # Strategy selection
        self.strategy = 'auto'
        self.detected_features = {}
        
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
    
    def detect_features(self):
        """Detect structural features of the formula."""
        n_clauses = len(self.clauses)
        density = n_clauses / max(1, self.n_vars)
        
        clause_lengths = [len(c) for c in self.clauses]
        avg_len = sum(clause_lengths) / max(1, len(clause_lengths))
        
        self.detected_features = {
            'n_vars': self.n_vars,
            'n_clauses': n_clauses,
            'density': density,
            'avg_clause_length': avg_len
        }
        
        # Select strategy
        if density < 2.0:
            self.strategy = 'cdcl_fast'
        elif self.n_vars > 10000:
            self.strategy = 'structure_aware'
        else:
            self.strategy = 'standard_cdcl'
    
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
    
    def vsids_branch(self) -> int:
        """VSIDS branching heuristic."""
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
        
        if self.var_scores.get(best_var, 0) >= self.var_scores.get(-best_var, 0):
            return best_var
        else:
            return -best_var
    
    def structure_branch(self) -> int:
        """Structure-aware branching."""
        # Prefer variables in many clauses
        var_count = defaultdict(int)
        for clause in self.clauses:
            for lit in clause:
                if abs(lit) not in self.assignment and abs(lit) not in [-v for v in self.assignment]:
                    var_count[abs(lit)] += 1
        
        if var_count:
            best_var = max(var_count.keys(), key=lambda v: var_count[v])
            return random.choice([best_var, -best_var])
        return 0
    
    def analyze_conflict(self, conflict: List[int]) -> Tuple[List[int], int]:
        """Analyze conflict and learn clause."""
        learned = list(conflict)
        
        for lit in conflict:
            self.var_scores[abs(lit)] += self.var_inc
        
        self.var_inc *= (1.0 / self.var_decay)
        
        return learned, max(0, self.decision_level - 1)
    
    def solve(self) -> Optional[Dict[int, bool]]:
        """Solve using selected strategy."""
        self.detect_features()
        
        # Initialize VSIDS
        for clause in self.clauses:
            for lit in clause:
                self.var_scores[abs(lit)] += 1.0
        
        decision_stack = []
        
        # Select branching function based on strategy
        if self.strategy == 'structure_aware':
            branch_fn = self.structure_branch
        else:
            branch_fn = self.vsids_branch
        
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
                branch_lit = branch_fn()
                if branch_lit == 0:
                    return self.assignment
                
                self.decision_level += 1
                self.assignment[branch_lit] = True
                self.assignment[-branch_lit] = False
                decision_stack.append(branch_lit)

def main():
    if len(sys.argv) < 2:
        print("Usage: python cic_sat_v2.py <cnf_file>")
        sys.exit(1)
    
    solver = CICSATv2()
    solver.read_dimacs(sys.argv[1])
    
    result = solver.solve()
    
    if result:
        print("SATISFIABLE")
    else:
        print("UNSATISFIABLE")

if __name__ == "__main__":
    main()
