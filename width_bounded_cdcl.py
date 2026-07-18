"""
Width-Bounded CDCL SAT Solver
"""

import sys
import random
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict

class WidthBoundedCDCL:
    """CDCL SAT solver with width-bounded clause learning."""
    
    def __init__(self, max_clause_width: int = 20):
        self.max_width = max_clause_width
        self.clauses = []
        self.assignment = {}
        self.decision_level = 0
        self.decision_stack = []
        self.learned_clauses = []
        self.implication_graph = defaultdict(list)
        
    def read_dimacs(self, filename: str):
        """Read CNF in DIMACS format."""
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('c'):
                    continue
                if line.startswith('p'):
                    parts = line.split()
                    self.n_vars = int(parts[2])
                else:
                    literals = list(map(int, line.split()))[:-1]
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
                    return clause
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    self.assignment[lit] = True
                    self.assignment[-lit] = False
                    changed = True
        
        return None
    
    def analyze_conflict(self, conflict_clause: List[int]) -> List[int]:
        """Analyze conflict and learn a clause (width-bounded)."""
        learned = list(conflict_clause)
        
        # Simplify if too wide
        if len(learned) > self.max_width:
            learned = self._simplify_clause(learned)
        
        return learned
    
    def _simplify_clause(self, clause: List[int]) -> List[int]:
        """Simplify a clause to meet width bound."""
        # Keep the most "important" literals
        scored = [(lit, self._literal_score(lit)) for lit in clause]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [lit for lit, _ in scored[:self.max_width]]
    
    def _literal_score(self, lit: int) -> float:
        """Score a literal for importance."""
        # Higher score for recently assigned literals
        if lit in self.assignment:
            return 1.0
        return 0.5
    
    def branch(self) -> int:
        """Select a variable to branch on."""
        for var in range(1, self.n_vars + 1):
            if var not in self.assignment and -var not in self.assignment:
                return random.choice([var, -var])
        return 0
    
    def solve(self) -> Optional[Dict[int, bool]]:
        """Solve the SAT instance."""
        while True:
            conflict = self.unit_propagate()
            
            if conflict:
                if self.decision_level == 0:
                    return None
                
                learned = self.analyze_conflict(conflict)
                self.learned_clauses.append(learned)
                
                # Backtrack
                back_level = max(0, self.decision_level - 1)
                self._backtrack(back_level)
                self.decision_level = back_level
            else:
                branch_lit = self.branch()
                if branch_lit == 0:
                    return self.assignment
                
                self.decision_level += 1
                self.assignment[branch_lit] = True
                self.assignment[-branch_lit] = False
                self.decision_stack.append(branch_lit)
    
    def _backtrack(self, level: int):
        """Backtrack to given decision level."""
        while len(self.decision_stack) > level:
            lit = self.decision_stack.pop()
            del self.assignment[lit]
            if -lit in self.assignment:
                del self.assignment[-lit]

def main():
    if len(sys.argv) < 2:
        print("Usage: python width_bounded_cdcl.py <cnf_file> [max_width]")
        sys.exit(1)
    
    max_width = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    solver = WidthBoundedCDCL(max_width)
    solver.read_dimacs(sys.argv[1])
    
    result = solver.solve()
    
    if result:
        print("SATISFIABLE")
    else:
        print("UNSATISFIABLE")

if __name__ == "__main__":
    main()
