"""
Fast Benchmark Suite for SAT Solvers
"""

import time
import subprocess
import os
import json
from typing import List, Dict

def run_solver(solver_path: str, cnf_path: str, timeout: int = 300) -> Dict:
    """
    Run a SAT solver on a CNF instance.
    
    Args:
        solver_path: Path to solver executable
        cnf_path: Path to CNF file
        timeout: Timeout in seconds
        
    Returns:
        Dictionary with results
    """
    start = time.time()
    try:
        result = subprocess.run(
            ['python', solver_path, cnf_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start
        
        output = result.stdout + result.stderr
        
        # Parse result
        if 'SATISFIABLE' in output or 'SAT' in output:
            status = 'SAT'
        elif 'UNSATISFIABLE' in output or 'UNSAT' in output:
            status = 'UNSAT'
        else:
            status = 'UNKNOWN'
        
        return {
            'instance': cnf_path,
            'solver': solver_path,
            'status': status,
            'time': elapsed,
            'timeout': False
        }
    except subprocess.TimeoutExpired:
        return {
            'instance': cnf_path,
            'solver': solver_path,
            'status': 'TIMEOUT',
            'time': timeout,
            'timeout': True
        }

def benchmark_suite(solver_path: str, instance_dir: str, timeout: int = 60) -> List[Dict]:
    """
    Run benchmark suite on a directory of instances.
    
    Args:
        solver_path: Path to solver
        instance_dir: Directory containing CNF files
        timeout: Timeout per instance
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    for filename in sorted(os.listdir(instance_dir)):
        if filename.endswith('.cnf'):
            cnf_path = os.path.join(instance_dir, filename)
            result = run_solver(solver_path, cnf_path, timeout)
            results.append(result)
            print(f"  {filename}: {result['status']} ({result['time']:.2f}s)")
    
    return results

def summarize_results(results: List[Dict]) -> Dict:
    """Summarize benchmark results."""
    total = len(results)
    solved = sum(1 for r in results if r['status'] in ['SAT', 'UNSAT'])
    timeouts = sum(1 for r in results if r['timeout'])
    sat = sum(1 for r in results if r['status'] == 'SAT')
    unsat = sum(1 for r in results if r['status'] == 'UNSAT')
    
    times = [r['time'] for r in results if not r['timeout']]
    avg_time = sum(times) / len(times) if times else 0
    
    return {
        'total': total,
        'solved': solved,
        'timeouts': timeouts,
        'sat': sat,
        'unsat': unsat,
        'solve_rate': solved / total if total > 0 else 0,
        'avg_time': avg_time
    }

def main():
    """Run fast benchmark."""
    print("Fast Benchmark Suite")
    print("=" * 50)
    
    # Example: benchmark a solver
    solver = 'cic_sat_solver.py'
    instances = 'instances/'
    
    if os.path.exists(instances):
        results = benchmark_suite(solver, instances, timeout=30)
        summary = summarize_results(results)
        
        print(f"\nSummary:")
        print(f"  Total: {summary['total']}")
        print(f"  Solved: {summary['solved']}")
        print(f"  Timeouts: {summary['timeouts']}")
        print(f"  Solve Rate: {summary['solve_rate']:.2%}")
        print(f"  Avg Time: {summary['avg_time']:.2f}s")

if __name__ == "__main__":
    main()
