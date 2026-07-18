"""
SAT Competition Benchmark Suite
Comprehensive benchmarking following SAT Competition rules.
"""

import os
import time
import subprocess
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    solver: str
    instance: str
    status: str
    time: float
    timeout: bool

def run_solver(solver_cmd: List[str], instance: str, timeout: int = 5000) -> BenchmarkResult:
    """Run a solver on an instance."""
    start = time.time()
    try:
        result = subprocess.run(
            solver_cmd + [instance],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start
        
        output = result.stdout + result.stderr
        
        if 'SATISFIABLE' in output or 's SATISFIABLE' in output:
            status = 'SAT'
        elif 'UNSATISFIABLE' in output or 's UNSATISFIABLE' in output:
            status = 'UNSAT'
        else:
            status = 'UNKNOWN'
        
        return BenchmarkResult(
            solver=' '.join(solver_cmd),
            instance=os.path.basename(instance),
            status=status,
            time=elapsed,
            timeout=False
        )
    except subprocess.TimeoutExpired:
        return BenchmarkResult(
            solver=' '.join(solver_cmd),
            instance=os.path.basename(instance),
            status='TIMEOUT',
            time=timeout,
            timeout=True
        )

def compute_par2(results: List[BenchmarkResult]) -> float:
    """Compute PAR2 score (SAT Competition scoring)."""
    par2 = 0.0
    for r in results:
        if r.status in ['SAT', 'UNSAT']:
            par2 += r.time
        else:
            par2 += 5000  # Penalty for timeout
    return par2

def run_benchmark_suite(solvers: Dict[str, List[str]], instances: List[str]) -> Dict:
    """Run full benchmark suite."""
    all_results = {}
    
    for solver_name, solver_cmd in solvers.items():
        print(f"Running {solver_name}...")
        results = []
        
        for instance in instances:
            result = run_solver(solver_cmd, instance)
            results.append(result)
            print(f"  {result.instance}: {result.status} ({result.time:.1f}s)")
        
        par2 = compute_par2(results)
        solved = sum(1 for r in results if r.status in ['SAT', 'UNSAT'])
        
        all_results[solver_name] = {
            'results': [
                {
                    'instance': r.instance,
                    'status': r.status,
                    'time': r.time
                }
                for r in results
            ],
            'par2': par2,
            'solved': solved,
            'total': len(results)
        }
    
    return all_results

def main():
    """Run SAT Competition benchmark."""
    print("SAT Competition Benchmark Suite")
    print("=" * 50)
    
    # Define solvers
    solvers = {
        'cic_v4': ['python', 'cic_sat_v4.py'],
        'cic_v3': ['python', 'cic_sat_v3.py'],
    }
    
    # Find instances
    instance_dir = 'instances/'
    if os.path.exists(instance_dir):
        instances = [
            os.path.join(instance_dir, f)
            for f in os.listdir(instance_dir)
            if f.endswith('.cnf')
        ]
        
        if instances:
            results = run_benchmark_suite(solvers, instances)
            
            # Save results
            with open('satcomp_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            
            # Print summary
            print("\nSummary:")
            for solver, data in results.items():
                print(f"  {solver}: {data['solved']}/{data['total']} solved, PAR2={data['par2']:.0f}")

if __name__ == "__main__":
    main()
