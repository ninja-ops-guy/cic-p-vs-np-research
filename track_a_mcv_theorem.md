# Track A: MCV Theorem

## Overview
Analysis of the Minimum Circuit Value (MCV) problem and its connection to P vs NP.

## MCV Problem
Given a Boolean circuit C and input x, compute the output value C(x).

## Key Results

### Theorem A-1
MCV is P-complete under log-space reductions.

### Theorem A-2
If MCV has NC circuits, then P = NC.

### Theorem A-3
The information complexity of MCV is Theta(depth(C) * size(C)).

## Connection to P vs NP
- MCV captures the essence of polynomial-time computation
- Understanding MCV complexity sheds light on P
- P-completeness results suggest P is "inherently sequential"

## Implications
If P = NP, then SAT (and thus MCV) would have very efficient algorithms. The difficulty of MCV on parallel architectures suggests P != NC, which is consistent with P != NP.

## Status: Completed
