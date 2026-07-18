"""
CIC MaxSAT Solver - Maximum Satisfiability with Width-Based Optimization
"""

import sys
import random
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict

class CICMaxSAT:
    """MaxSAT solver using width-based branch and bound."""
    
    def __init__(self):
        self.hard_clauses: List[List[int]] = []
        self.soft_clauses: List[Tuple[List[int], int]] = []
        self.n_vars = 0
        self.assignment: Dict[int, bool] = {}
        self.best_cost = float('inf')
        self.best_assignment = None
        
    def read_wcnf(self, filename: str):
        """Read formula in WCNF format."""
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('c'):
                    continue
                if line.startswith('p'):
                    parts = line.split()
                    self.n_vars = int(parts[2])
                else:
                    parts = list(map(int, line.split()))
                    weight = parts[0]
                    literals = parts[1:-1]
                    
                    if weight == 0 or weight == 'top':
                        self.hard_clauses.append(literals)
                    else:
                        self.soft_clauses.append((literals, weight))
    
    def compute_cost(self, assignment: Dict[int, bool]) -> int:
        """Compute cost (weight of unsatisfied soft clauses)."""
        cost = 0
        for clause, weight in self.soft_clauses:
            satisfied = False
            for lit in clause:
                if lit in assignment and assignment[lit]:
                    satisfied = True
                    break
            if not satisfied:
                cost += weight
        return cost
    
    def is_hard_satisfied(self, assignment: Dict[int, bool]) -> bool:
        """Check if all hard clauses are satisfied."""
        for clause in self.hard_clauses:
            satisfied = False
            for lit in clause:
                if lit in assignment and assignment[lit]:
                    satisfied = True
                    break
            if not satisfied:
                return False
        return True
    
    def estimate_lower_bound(self, assignment: Dict[int, bool]) -> int:
        """Estimate lower bound on cost for current partial assignment."""
        # Simple bound: count unsatisfied soft clauses
        lb = 0
        for clause, weight in self.soft_clauses:
            # Check if clause is already falsified
            all_false = True
            for lit in clause:
                if lit not in assignment and -lit not in assignment:
                    all_false = False  # Unassigned variable
                    break
                if lit in assignment and assignment[lit]:
                    all_false = False
                    break
            if all_false:
                lb += weight
        return lb
    
    def branch_and_bound(self, var_idx: int, assignment: Dict[int, bool]):
        """Branch and bound search."""
        # Pruning: check lower bound
        lb = self.estimate_lower_bound(assignment)
        if lb >= self.best_cost:
            return
        
        # Check if all variables are assigned
        if var_idx > self.n_vars:
            if self.is_hard_satisfied(assignment):
                cost = self.compute_cost(assignment)
                if cost < self.best_cost:
                    self.best_cost = cost
                    self.best_assignment = dict(assignment)
            return
        
        # Branch on variable
        for val in [True, False]:
            lit = var_idx if val else -var_idx
            assignment[lit] = True
            assignment[-lit] = False
            
            self.branch_and_bound(var_idx + 1, assignment)
            
            del assignment[lit]
            if -lit in assignment:
                del assignment[-lit]
    
    def solve(self) -> Tuple[Optional[Dict[int, bool]], int]:
        """Solve MaxSAT using branch and bound."""
        self.branch_and_bound(1, {})
        return self.best_assignment, self.best_cost

def main():
    if len(sys.argv) < 2:
        print("Usage: python cic_maxsat.py <wcnf_file>")
        sys.exit(1)
    
    solver = CICMaxSAT()
    solver.read_wcnf(sys.argv[1])
    
    assignment, cost = solver.solve()
    
    if assignment:
        print(f"OPTIMUM FOUND: cost = {cost}")
    else:
        print("NO SOLUTION (hard clauses unsatisfiable)")

if __name__ == "__main__":
    main()
