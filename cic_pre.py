"""
CIC Preprocessor - Formula Analysis and Transformation
"""

import sys
from typing import List, Tuple, Dict, Set
import numpy as np

class CICPreprocessor:
    """Preprocessor for SAT formulas with structural analysis."""
    
    def __init__(self):
        self.n_vars = 0
        self.n_clauses = 0
        self.clauses = []
        self.var_frequency = {}
        self.clause_lengths = []
        
    def read_dimacs(self, filename: str):
        """Read a CNF formula in DIMACS format."""
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('c'):
                    continue
                if line.startswith('p'):
                    parts = line.split()
                    self.n_vars = int(parts[2])
                    self.n_clauses = int(parts[3])
                else:
                    literals = list(map(int, line.split()))
                    if literals[-1] == 0:
                        literals = literals[:-1]
                    self.clauses.append(literals)
                    self.clause_lengths.append(len(literals))
        
        # Compute variable frequencies
        for clause in self.clauses:
            for lit in clause:
                var = abs(lit)
                self.var_frequency[var] = self.var_frequency.get(var, 0) + 1
    
    def compute_density(self) -> float:
        """Compute clause density (clauses/variables)."""
        if self.n_vars == 0:
            return 0.0
        return len(self.clauses) / self.n_vars
    
    def compute_stats(self) -> Dict:
        """Compute comprehensive formula statistics."""
        if not self.clauses:
            return {}
        
        return {
            'n_vars': self.n_vars,
            'n_clauses': len(self.clauses),
            'density': self.compute_density(),
            'avg_clause_length': np.mean(self.clause_lengths),
            'max_clause_length': max(self.clause_lengths),
            'min_clause_length': min(self.clause_lengths),
            'std_clause_length': np.std(self.clause_lengths),
            'total_literal_occurrences': sum(len(c) for c in self.clauses),
            'most_frequent_var': max(self.var_frequency.items(), key=lambda x: x[1]) if self.var_frequency else (0, 0),
            'n_unit_clauses': sum(1 for c in self.clauses if len(c) == 1),
            'n_binary_clauses': sum(1 for c in self.clauses if len(c) == 2),
        }
    
    def unit_propagation(self) -> Tuple[bool, List[int], List[List[int]]]:
        """
        Perform unit propagation.
        
        Returns:
            (satisfiable, assignments, simplified_clauses)
        """
        clauses = [list(c) for c in self.clauses]
        assignments = []
        
        changed = True
        while changed:
            changed = False
            unit_clauses = [c for c in clauses if len(c) == 1]
            
            for unit in unit_clauses:
                lit = unit[0]
                var = abs(lit)
                val = 1 if lit > 0 else 0
                assignments.append((var, val))
                
                # Remove satisfied clauses and falsified literals
                new_clauses = []
                for clause in clauses:
                    if lit in clause:
                        continue  # Clause satisfied
                    new_clause = [l for l in clause if l != -lit]
                    if not new_clause:
                        return False, [], []  # Conflict
                    new_clauses.append(new_clause)
                
                clauses = new_clauses
                changed = True
                break
        
        return True, assignments, clauses
    
    def analyze(self) -> Dict:
        """Full formula analysis."""
        stats = self.compute_stats()
        sat, assignments, simplified = self.unit_propagation()
        
        stats['unit_propagation_result'] = 'SAT' if sat else 'UNSAT'
        stats['unit_propagation_assignments'] = len(assignments)
        stats['simplified_n_clauses'] = len(simplified)
        
        return stats

def main():
    """CLI for CIC preprocessor."""
    if len(sys.argv) < 2:
        print("Usage: python cic_pre.py <cnf_file>")
        sys.exit(1)
    
    pre = CICPreprocessor()
    pre.read_dimacs(sys.argv[1])
    
    print("CIC Preprocessor")
    print("=" * 50)
    
    stats = pre.analyze()
    for key, value in stats.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
