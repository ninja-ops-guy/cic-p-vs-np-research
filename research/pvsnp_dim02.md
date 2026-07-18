# P vs NP Dimension 2: Circuit Complexity

## Overview
Analysis of circuit complexity approaches to P vs NP.

## Circuit Complexity Basics

### Definition
A Boolean circuit is a directed acyclic graph where:
- Input nodes are labeled with variables
- Internal nodes are labeled with Boolean operations (AND, OR, NOT)
- One output node produces the result

### Size and Depth
- **Size**: Number of gates
- **Depth**: Longest path from input to output

## Key Results

### Theorem 2.1 (Shannon)
Almost all Boolean functions require circuits of size Omega(2^n / n).

### Theorem 2.2 (Lupanov)
Every Boolean function can be computed by circuits of size O(2^n / n).

### Theorem 2.3 (Razborov)
The clique function requires monotone circuits of size n^Omega(log n).

### Theorem 2.4 (Williams)
NEXP is not contained in ACC^0.

## P vs NP Connection

### Conjecture 2.1
NP requires superpolynomial circuit size.

### Implication
If proven, this would imply P != NP.

## The CIC Perspective

### Information Capacity of Circuits
The information capacity of a circuit C is:
IC(C) = sum over all gates of the information processed

### Theorem 2.5 (CIC)
If NP has polynomial-size circuits, then IC(SAT) <= poly(n).

## Barrier: Natural Proofs

### Theorem 2.6 (Razborov-Rudich)
Any natural proof that NP requires superpolynomial circuits would break pseudorandom generators.

## Status: Completed
