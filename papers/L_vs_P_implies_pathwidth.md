# L ≠ P Implies Super-Logarithmic Circuit Pathwidth for SAT

## A New Conditional Result in the CIC Framework

**Abstract.** We prove that if L ≠ P (logarithmic space differs from polynomial time), then the Boolean satisfiability problem SAT has no circuits of pathwidth O(log n). This is the first connection between space complexity separations and circuit pathwidth lower bounds. Combined with the Karchmer-Wigderson theorem, it yields L ≠ P → SAT ∉ NC¹.

---

## 1. Introduction

The separation of logarithmic space (L) from polynomial time (P) is a longstanding open problem. We show that under L ≠ P, SAT has no circuits of sub-logarithmic pathwidth.

## 2. Main Results

**Lemma 1 (Space-efficient evaluation).** A circuit C of pathwidth w and size s can be evaluated in space O(w + log s).

*Proof.* Use a path decomposition of width w. Process bags left to right, storing O(w) gate values and a pointer of O(log s) bits. ∎

**Corollary 1.** If f has a circuit of pathwidth O(log n) and size poly(n), then f ∈ L.

**Theorem 1 (L ≠ P → super-logarithmic pathwidth).** If L ≠ P, then CIC_circuit(SAT) = ω(log n).

*Proof.* Suppose CIC_circuit(SAT) = O(log n). Then SAT has a circuit of pathwidth O(log n) and size poly(n). By Corollary 1, SAT ∈ L. Since SAT is P-complete, L = P. Contradiction. ∎

**Corollary 2 (L ≠ P → SAT ∉ NC¹).** If L ≠ P, then SAT ∉ NC¹.

*Proof.* By Barrington's Theorem, NC¹ = pathwidth-O(1) circuits. Theorem 1 says SAT requires ω(log n) pathwidth. ∎

## 3. Discussion

This is the first connection between space complexity and circuit pathwidth. Whether L ≠ P can be pushed to P ≠ NP is open.
