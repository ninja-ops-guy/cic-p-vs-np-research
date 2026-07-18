"""
StructuralSAT - SAT Solver with Structural Analysis
"""

import sys
import random
import heapq
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict

class StructuralSAT:
    """SAT solver that exploits formula structure."""
    
    def __init__(self):
        self.clauses = []
        self.n_vars = 0
        self.assignment = {}
        self.decision_level = 0
        self.scores = defaultdict(float)
        
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
    
    def compute_variable_graph(self) -> Dict[int, Set[int]]:
        """Build variable interaction graph."""
        graph = defaultdict(set)
        for clause in self.clauses:
            vars_in_clause = [abs(lit) for lit in clause]
            for i, v1 in enumerate(vars_in_clause):
                for v2 in vars_in_clause[i+1:]:
                    graph[v1].add(v2)
                    graph[v2].add(v1)
        return graph
    
    def estimate_treewidth_greedy(self) -> int:
        """Estimate treewidth using greedy elimination."""
        graph = self.compute_variable_graph()
        max_width = 0
        
        while graph:
            # Find minimum degree vertex
            min_vertex = min(graph.keys(), key=lambda v: len(graph[v]))
            neighbors = list(graph[min_vertex])
            
            width = len(neighbors)
            max_width = max(max_width, width)
            
            # Add edges between neighbors (elimination)
            for i, n1 in enumerate(neighbors):
                for n2 in neighbors[i+1:]:
                    graph[n1].add(n2)
                    graph[n2].add(n1)
            
            # Remove vertex
            for neighbor in neighbors:
                graph[neighbor].discard(min_vertex)
            del graph[min_vertex]
        
        return max_width
    
    def structure_based_branching(self) -> int:
        """Choose branching variable based on structure."""
        # Score variables by frequency and structural importance
        best_var = None
        best_score = -1
        
        for var in range(1, self.n_vars + 1):
            if var not in self.assignment and -var not in self.assignment:
                score = self.scores.get(var, 0) + self.scores.get(-var, 0)
                if score > best_score:
                    best_score = score
                    best_var = var
        
        if best_var:
            return random.choice([best_var, -best_var])
        return 0
    
    def unit_propagate(self) -> Optional[List[int]]:
        """Unit propagation."""
        changed = True
        while changed:
            changed = False
            for clause in self.clauses:
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
    
    def solve(self) -> Optional[Dict]:
        """Solve using structure-aware CDCL."""
        # Compute structural features
        tw_est = self.estimate_treewidth_greedy()
        
        # Initialize variable scores based on structure
        for clause in self.clauses:
            for lit in clause:
                self.scores[lit] += 1.0 / len(clause)
        
        return self._cdcl_search()
    
    def _cdcl_search(self) -> Optional[Dict]:
        """CDCL search with structure-aware branching."""
        decision_stack = []
        learned_clauses = []
        
        while True:
            conflict = self.unit_propagate()
            
            if conflict:
                if not decision_stack:
                    return None
                
                # Simple backtracking
                learned_clauses.append(conflict)
                
                # Backtrack one level
                if decision_stack:
                    lit = decision_stack.pop()
                    del self.assignment[lit]
                    if -lit in self.assignment:
                        del self.assignment[-lit]
            else:
                branch_lit = self.structure_based_branching()
                if branch_lit == 0:
                    return self.assignment
                
                self.assignment[branch_lit] = True
                self.assignment[-branch_lit] = False
                decision_stack.append(branch_lit)

def main():
    if len(sys.argv) < 2:
        print("Usage: python structuralsat.py <cnf_file>")
        sys.exit(1)
    
    solver = StructuralSAT()
    solver.read_dimacs(sys.argv[1])
    
    print(f"Estimated treewidth: {solver.estimate_treewidth_greedy()}")
    
    result = solver.solve()
    
    if result:
        print("SATISFIABLE")
    else:
        print("UNSATISFIABLE")

if __name__ == "__main__":
    main()
