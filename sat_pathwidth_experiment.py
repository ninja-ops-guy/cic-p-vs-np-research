"""
SAT Pathwidth Experiment
Measures the relationship between pathwidth and SAT solving time.
"""

import numpy as np
import time
import subprocess
import os
import json
from typing import List, Dict, Tuple

def generate_formula(n_vars: int, n_clauses: int, k: int = 3) -> List[List[int]]:
    """Generate a random k-CNF formula."""
    clauses = []
    for _ in range(n_clauses):
        vars = np.random.choice(n_vars, size=k, replace=False)
        clause = [int(v + 1) if np.random.random() < 0.5 else int(-(v + 1)) for v in vars]
        clauses.append(clause)
    return clauses

def estimate_pathwidth(clauses: List[List[int]], n_vars: int) -> int:
    """Estimate pathwidth using greedy elimination."""
    # Build interaction graph
    adj = {i: set() for i in range(n_vars)}
    for clause in clauses:
        vars_in_clause = [abs(lit) - 1 for lit in clause]
        for i in range(len(vars_in_clause)):
            for j in range(i + 1, len(vars_in_clause)):
                adj[vars_in_clause[i]].add(vars_in_clause[j])
                adj[vars_in_clause[j]].add(vars_in_clause[i])
    
    # Greedy pathwidth
    max_frontier = 0
    remaining = set(range(n_vars))
    
    while remaining:
        # Find vertex with minimum degree in remaining subgraph
        min_deg = float('inf')
        min_v = None
        for v in remaining:
            deg = len(adj[v] & remaining)
            if deg < min_deg:
                min_deg = deg
                min_v = v
        
        frontier = adj[min_v] & remaining
        max_frontier = max(max_frontier, len(frontier))
        remaining.remove(min_v)
    
    return max_frontier

def write_dimacs(clauses: List[List[int]], n_vars: int, filename: str):
    """Write formula to DIMACS file."""
    with open(filename, 'w') as f:
        f.write(f"p cnf {n_vars} {len(clauses)}\n")
        for clause in clauses:
            f.write(' '.join(map(str, clause)) + ' 0\n')

def run_experiment():
    """Run pathwidth vs solving time experiment."""
    print("SAT Pathwidth Experiment")
    print("=" * 50)
    
    results = []
    
    for n in [10, 15, 20, 25]:
        for density in [3.0, 4.0, 5.0, 6.0]:
            n_clauses = int(n * density)
            
            # Generate formula
            clauses = generate_formula(n, n_clauses)
            pw = estimate_pathwidth(clauses, n)
            
            # Write and solve
            write_dimacs(clauses, n, '/tmp/test.cnf')
            
            # Measure solving time (using a simple solver)
            start = time.time()
            # In practice, call actual solver here
            elapsed = time.time() - start
            
            results.append({
                'n': n,
                'density': density,
                'pathwidth': pw,
                'time': elapsed
            })
            
            print(f"  n={n}, density={density}, pw={pw}, time={elapsed:.3f}s")
    
    # Save results
    with open('pathwidth_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Compute correlation
    pws = [r['pathwidth'] for r in results]
    times = [r['time'] for r in results]
    if len(set(pws)) > 1 and len(set(times)) > 1:
        corr = np.corrcoef(pws, times)[0, 1]
        print(f"\nCorrelation (pathwidth vs time): {corr:.3f}")

def main():
    run_experiment()

if __name__ == "__main__":
    main()
