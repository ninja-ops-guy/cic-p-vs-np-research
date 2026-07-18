# Backbone Lemma Proof Attempt

## The Backbone Lemma
**Statement:** If F is an unsatisfiable CNF formula with backbone size b, then any resolution refutation of F requires width at least b/2.

## Proof Attempt

### Definitions
- **Backbone**: The set of literals that are true in every satisfying assignment (for satisfiable formulas) or the set of literals that lead to contradiction (for unsatisfiable formulas).
- **Width**: The maximum number of literals in any clause of the proof.

### Attempt 1: Direct Information Argument
1. Each backbone literal carries information about the formula's structure
2. Resolving on backbone literals requires wide intermediate clauses
3. Therefore width >= b/2

**Gap**: Step 2 is not rigorously established.

### Attempt 2: Induction on Backbone Size
1. Base case: b=1 is trivial
2. Inductive step: Adding a backbone literal increases width by at least 1/2

**Gap**: The inductive step fails for certain formula structures.

### Attempt 3: Connection to Treewidth
1. Backbone size relates to treewidth
2. Treewidth gives width lower bound
3. Combine to get the result

**Gap**: The relationship between backbone size and treewidth is not proven.

## Conclusion
The Backbone Lemma remains unproven. All attempts have gaps that require new insights to fill.
