"""
Comprehensive Benchmark Runner
"""

import sys
import os
import time
import json
import subprocess
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Optional

class BenchmarkRunner:
    """Manages comprehensive SAT solver benchmarks."""
    
    def __init__(self, output_dir: str = "benchmark_results"):
        self.output_dir = output_dir
        self.results = []
        os.makedirs(output_dir, exist_ok=True)
    
    def run_single(self, solver: str, instance: str, timeout: int = 300) -> Dict:
        """Run a single solver-instance pair."""
        start = time.time()
        
        try:
            result = subprocess.run(
                ['python', solver, instance],
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
            
            return {
                'solver': solver,
                'instance': os.path.basename(instance),
                'status': status,
                'time': elapsed,
                'timeout': False,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'solver': solver,
                'instance': os.path.basename(instance),
                'status': 'TIMEOUT',
                'time': timeout,
                'timeout': True,
                'returncode': -1
            }
        except Exception as e:
            return {
                'solver': solver,
                'instance': os.path.basename(instance),
                'status': 'ERROR',
                'time': 0,
                'timeout': False,
                'error': str(e),
                'returncode': -1
            }
    
    def run_suite(self, solvers: List[str], instances: List[str], 
                  timeout: int = 300, parallel: bool = True) -> List[Dict]:
        """Run a full benchmark suite."""
        tasks = [(s, i, timeout) for s in solvers for i in instances]
        
        if parallel and len(tasks) > 1:
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(self.run_single, s, i, t) for s, i, t in tasks]
                self.results = [f.result() for f in futures]
        else:
            self.results = [self.run_single(s, i, t) for s, i, t in tasks]
        
        return self.results
    
    def save_results(self, filename: str = "results.json"):
        """Save results to JSON file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to {filepath}")
    
    def generate_report(self) -> str:
        """Generate a markdown report."""
        report = "# Benchmark Report\n\n"
        
        # Summary statistics
        solvers = set(r['solver'] for r in self.results)
        
        for solver in sorted(solvers):
            solver_results = [r for r in self.results if r['solver'] == solver]
            total = len(solver_results)
            solved = sum(1 for r in solver_results if r['status'] in ['SAT', 'UNSAT'])
            timeouts = sum(1 for r in solver_results if r['status'] == 'TIMEOUT')
            avg_time = sum(r['time'] for r in solver_results if not r['timeout']) / max(1, total - timeouts)
            
            report += f"## {solver}\n"
            report += f"- Total: {total}\n"
            report += f"- Solved: {solved}\n"
            report += f"- Timeouts: {timeouts}\n"
            report += f"- Solve Rate: {solved/total:.1%}\n"
            report += f"- Avg Time: {avg_time:.2f}s\n\n"
        
        return report

def main():
    """CLI for benchmark runner."""
    runner = BenchmarkRunner()
    
    # Example usage
    solvers = ['cic_sat_solver.py', 'cic_sat_v2.py']
    instances = []
    
    if len(sys.argv) > 1:
        instance_dir = sys.argv[1]
        if os.path.isdir(instance_dir):
            instances = [os.path.join(instance_dir, f) 
                        for f in os.listdir(instance_dir) if f.endswith('.cnf')]
    
    if instances:
        print(f"Running benchmarks: {len(solvers)} solvers x {len(instances)} instances")
        runner.run_suite(solvers, instances, timeout=60)
        runner.save_results()
        
        report = runner.generate_report()
        print(report)
    else:
        print("Usage: python run_benchmarks.py <instance_directory>")

if __name__ == "__main__":
    main()
