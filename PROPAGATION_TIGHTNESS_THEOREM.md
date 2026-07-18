# Propagation Tightness Theorem

## Statement
**Theorem (Propagation Tightness):** For a CNF formula F with n variables, let pt(F) denote the propagation tightness. Then any resolution refutation of F requires size at least 2^(Omega(pt(F))).

## Definitions
- **Propagation Tightness**: The minimum number of clauses that must be activated during unit propagation to derive a contradiction.
- **Resolution Refutation**: A proof of unsatisfiability using only the resolution rule.

## Proof Sketch
1. Unit propagation can be viewed as information flow through the implication graph
2. Tight propagation implies many inference steps are necessary
3. Each inference step contributes to proof size
4. Lower bound follows from information-theoretic argument

## Implications
This theorem connects the structural property of propagation tightness to proof complexity lower bounds.

## Status: Partially Proved (under assumptions)
