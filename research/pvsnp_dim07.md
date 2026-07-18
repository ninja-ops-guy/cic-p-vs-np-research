# P vs NP Dimension 7: Proof Complexity and Satisfiability

## Overview
Analysis of proof complexity lower bounds for SAT.

## Proof Systems for SAT

### Resolution
- Refutation-complete for CNF
- Studied extensively
- Exponential lower bounds known

### Extended Resolution
- Adds extension rules
- More powerful than resolution
- No superpolynomial lower bounds known

### Frege
- Propositionally complete
- Very powerful
- Lower bounds are major open problems

## Key Results

### Theorem 7.1 (Haken)
Pigeonhole principle requires exponential resolution proofs.

### Theorem 7.2 (Chvátal-Szemerédi)
Random 3-SAT at threshold requires exponential resolution proofs.

### Theorem 7.3 (Ben-Sasson-Wigderson)
Size-width tradeoff: size >= 2^(width^2/n).

## CIC Contributions

### Propagation Tightness
pt(F) = minimum number of clauses activated by unit propagation.

### Theorem 7.4 (CIC)
Resolution size >= 2^Omega(pt(F)) under bounded-width assumption.

## Implications
- Proof complexity lower bounds imply algorithmic lower bounds
- Understanding proof systems helps understand SAT solving
- Strong lower bounds would imply P != NP

## Status: Completed
