# P vs NP: Propagation Tightness Submission

## Paper Submission: The Propagation Tightness Theorem

### Title
Propagation Tightness and the Complexity of SAT: A New Lower Bound Framework

### Abstract
We introduce propagation tightness, a structural measure of CNF formulas, and prove that it yields exponential lower bounds for resolution proofs. Our framework connects unit propagation dynamics to proof complexity through information-theoretic arguments.

### Main Theorem
**Theorem 1.** For any unsatisfiable CNF formula F, any resolution refutation of F requires size at least 2^(Omega(pt(F))), where pt(F) is the propagation tightness of F.

### Key Innovation
Unlike previous lower bound techniques that rely on specific formula constructions, propagation tightness applies to any formula and can be computed (or approximated) algorithmically.

### Proof Overview
1. Define the propagation graph showing information flow during unit propagation
2. Show that resolution must simulate all paths in this graph
3. Apply information-theoretic counting to obtain the lower bound

### Significance
- First general lower bound technique based on propagation dynamics
- Potential connection to practical SAT solver behavior
- New perspective on the relationship between structure and complexity

### Status
Submitted for peer review. Under consideration.
