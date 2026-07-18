# Programs Guide

## Overview
Guide to the programs and code developed during the CIC P vs NP research project.

## SAT Solvers

### cic_sat_solver.py (v1)
- Basic CDCL implementation
- Structural analysis features
- Command-line interface

### cic_sat_v2.py
- Portfolio solver with automatic selection
- Width estimation
- Improved heuristics

### cic_sat_v3.py
- GNN-based variable ordering
- Adaptive restart policy
- Advanced clause management

### cic_sat_v4.py
- Full-featured production solver
- Complete portfolio
- Machine learning integration

## Usage
```bash
python cic_sat_solver.py <input.cnf>
python cic_sat_v2.py <input.cnf> --portfolio
python cic_sat_v3.py <input.cnf> --gnn-ordering
python cic_sat_v4.py <input.cnf> --full
```

## Analysis Programs
- `sdp_treewidth.py` - SDP treewidth estimation
- `gnn_ordering.py` - GNN variable ordering
- `circuit_ic_framework.py` - Circuit complexity analysis
- `width_bounded_cdcl.py` - Width-bounded CDCL

## Benchmark Programs
- `fast_benchmark.py` - Quick benchmarks
- `run_benchmarks.py` - Full benchmark suite
- `satcomp_benchmark.py` - SAT Competition format
