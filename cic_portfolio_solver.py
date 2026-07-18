"""
CIC Portfolio Solver
Selects and combines multiple SAT solving strategies.
"""

import sys
import time
import subprocess
from typing import List, Dict, Tuple, Optional
import json

class PortfolioSolver:
    """Portfolio SAT solver that selects the best strategy."""
    
    def __init__(self):
        self.strategies = {
            'cdcl': {
                'cmd': ['python', 'cic_sat_solver.py'],
                'weight': 1.0,
                'good_for': ['general']
            },
            'structure': {
                'cmd': ['python', 'structuralsat.py'],
                'weight': 1.0,
                'good_for': ['structured', 'industrial']
            },
            'width_bounded': {
                'cmd': ['python', 'width_bounded_cdcl.py'],
                'weight': 0.8,
                'good_for': ['high_width']
            }
        }
        
        self.instance_features = {}
    
    def extract_features(self, filename: str) -> Dict:
        """Extract structural features from CNF file."""
        features = {
            'n_vars': 0,
            'n_clauses': 0,
            'density': 0.0,
            'avg_clause_len': 0.0,
            'estimated_tw': 0
        }
        
        clause_lengths = []
        
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('p'):
                    parts = line.split()
                    features['n_vars'] = int(parts[2])
                    features['n_clauses'] = int(parts[3])
                elif line and not line.startswith('c'):
                    literals = list(map(int, line.split()))
                    if literals[-1] == 0:
                        literals = literals[:-1]
                    clause_lengths.append(len(literals))
        
        if features['n_vars'] > 0:
            features['density'] = features['n_clauses'] / features['n_vars']
        
        if clause_lengths:
            features['avg_clause_len'] = sum(clause_lengths) / len(clause_lengths)
        
        # Simple treewidth estimate
        features['estimated_tw'] = min(
            features['n_vars'] // 2,
            int(features['density'] * 3)
        )
        
        return features
    
    def select_strategy(self, features: Dict) -> str:
        """Select best strategy based on features."""
        # Simple rule-based selection
        if features['density'] < 2.0:
            return 'cdcl'
        elif features['estimated_tw'] > 20:
            return 'width_bounded'
        elif features['n_vars'] > 1000:
            return 'structure'
        else:
            return 'cdcl'
    
    def run_strategy(self, strategy_name: str, filename: str, timeout: int = 300) -> Dict:
        """Run a single strategy."""
        strategy = self.strategies[strategy_name]
        
        start = time.time()
        try:
            result = subprocess.run(
                strategy['cmd'] + [filename],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            elapsed = time.time() - start
            
            output = result.stdout + result.stderr
            
            if 'SATISFIABLE' in output or 'SAT' in output:
                status = 'SAT'
            elif 'UNSATISFIABLE' in output or 'UNSAT' in output:
                status = 'UNSAT'
            else:
                status = 'UNKNOWN'
            
            return {
                'strategy': strategy_name,
                'status': status,
                'time': elapsed,
                'timeout': False
            }
        except subprocess.TimeoutExpired:
            return {
                'strategy': strategy_name,
                'status': 'TIMEOUT',
                'time': timeout,
                'timeout': True
            }
    
    def solve(self, filename: str, timeout: int = 300) -> Dict:
        """Solve using portfolio approach."""
        features = self.extract_features(filename)
        self.instance_features = features
        
        # Select primary strategy
        primary = self.select_strategy(features)
        
        # Run primary strategy
        result = self.run_strategy(primary, filename, timeout)
        
        if result['status'] in ['SAT', 'UNSAT']:
            return {
                'status': result['status'],
                'strategy_used': primary,
                'time': result['time'],
                'features': features
            }
        
        # If primary fails, try others
        for name in self.strategies:
            if name != primary:
                result = self.run_strategy(name, filename, timeout)
                if result['status'] in ['SAT', 'UNSAT']:
                    return {
                        'status': result['status'],
                        'strategy_used': name,
                        'time': result['time'],
                        'features': features
                    }
        
        return {
            'status': 'TIMEOUT',
            'strategy_used': 'all',
            'time': timeout,
            'features': features
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python cic_portfolio_solver.py <cnf_file>")
        sys.exit(1)
    
    solver = PortfolioSolver()
    result = solver.solve(sys.argv[1])
    
    print(f"Status: {result['status']}")
    print(f"Strategy: {result['strategy_used']}")
    print(f"Time: {result['time']:.2f}s")
    print(f"Features: {json.dumps(result['features'], indent=2)}")

if __name__ == "__main__":
    main()
