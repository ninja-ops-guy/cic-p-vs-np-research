# Track RR: Bounded-Width Circuit Classes

## Overview
Analysis of circuit complexity classes defined by width restrictions.

## Circuit Width Measures
- **Formula Size**: Number of gates in a formula (fanout 1)
- **Circuit Depth**: Longest path from input to output
- **Branching Program Width**: Width of oblivious branching programs

## Key Results

### Theorem RR-1
NC^1 (poly-size, log-depth circuits) is strictly contained in P.

### Theorem RR-2
Formula size lower bounds imply circuit size lower bounds.

### Theorem RR-3
If SAT has polynomial-size formulas, then P = NP.

## Bounded Width Classes
| Class | Size | Depth | Power |
|-------|------|-------|-------|
| NC^1 | poly | O(log n) | Weak |
| AC^0 | poly | constant | Very weak |
| NC | poly | poly(log n) | Moderate |
| P/poly | poly | unbounded | All of P |

## Status: Completed
