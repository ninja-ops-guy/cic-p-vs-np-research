# Section 2: Problem Definition and Background

## The P vs NP Problem

### Statement
Does P = NP? That is, can every problem whose solution can be verified in polynomial time also be solved in polynomial time?

### Formal Definitions

**Definition 2.1** (P). The class P consists of all decision problems that can be solved by a deterministic Turing machine in time O(n^k) for some constant k.

**Definition 2.2** (NP). The class NP consists of all decision problems where a "yes" answer can be verified by a deterministic Turing machine in polynomial time given a certificate.

### The SAT Problem
Boolean Satisfiability (SAT) is the canonical NP-complete problem:
- **Input**: A Boolean formula in conjunctive normal form (CNF)
- **Question**: Is there an assignment of variables that makes the formula true?

**Theorem 2.1** (Cook-Levin). SAT is NP-complete.

### Implications of P = NP
If P = NP:
1. Cryptographic systems would be broken
2. Optimization would become easy
3. AI and machine learning would be revolutionized
4. Mathematics would be automated

### Implications of P != NP
If P != NP:
1. Cryptography remains secure (assuming average-case hardness)
2. Some optimization problems are inherently hard
3. Creative work cannot be fully automated
4. The universe has "computational friction"

## Historical Approaches

### Circuit Complexity
Attempts to prove NP requires superpolynomial circuits.

### Proof Complexity
Lower bounds on proof lengths in various proof systems.

### Algebraic Geometry
Geometric Complexity Theory (Mulmuley-Sohoni).

### Information Theory
Using entropy and information measures.

## The CIC Approach
We introduce Computational Information Complexity as a new lens for attacking P vs NP.
