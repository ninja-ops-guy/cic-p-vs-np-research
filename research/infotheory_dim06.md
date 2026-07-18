# Information Theory Dimension 6: Channel Capacity of Formulas

## Overview
Viewing SAT formulas as communication channels and analyzing their capacity.

## Channel Model
- **Input**: Variable assignments
- **Channel**: The formula (maps assignments to satisfiability)
- **Output**: SAT/UNSAT

## Channel Capacity
The capacity of this channel is:
C = max_{p(x)} I(X; Y)

where X is the input distribution and Y is the output.

## Key Results

### Result 6.1
Random k-SAT at density alpha has channel capacity approaching 0 as n -> infinity.

### Result 6.2
Industrial formulas have higher channel capacity than random formulas.

### Result 6.3
Channel capacity correlates with the "interestingness" of the formula for solvers.

## Implications
Formulas with higher channel capacity are more "informative" and may be more interesting from a computational perspective.

## Status: Completed
