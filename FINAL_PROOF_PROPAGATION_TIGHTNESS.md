# Final Proof: Propagation Tightness

## Final Attempt at Proving the Propagation Tightness Theorem

## Theorem (Propagation Tightness)
For a CNF formula F, let pt(F) be the propagation tightness. Then any resolution refutation of F requires size at least 2^(Omega(pt(F))).

## Definitions
- **Unit Propagation**: The process of repeatedly applying unit clause propagation
- **Propagation Tightness**: The minimum number of distinct clauses activated during unit propagation to reach a contradiction
- **Resolution Size**: The number of clauses in a resolution refutation

## Proof Strategy

### Step 1: Information Flow in Unit Propagation
During unit propagation, information flows from clauses to variable assignments. Each propagation step can be viewed as transmitting one bit of information.

### Step 2: Counting Information Paths
The number of distinct information paths in the propagation process is at least pt(F). Each path requires at least one resolution step to simulate.

### Step 3: Lower Bound from Information Theory
By Shannon's source coding theorem, representing pt(F) bits of information requires at least pt(F) / log(2) steps.

### Step 4: Exponential Size
Since each resolution step can process at most O(1) bits of information, the total number of steps is at least Omega(pt(F)). For width-bounded proofs, this translates to exponential size.

## Remaining Gap
Step 4 requires that the proof width is bounded, which is not established for all formulas.

## Conclusion
The theorem holds under the assumption of bounded-width proofs, which remains to be established in general.
