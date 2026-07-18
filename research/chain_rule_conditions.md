# Chain Rule Conditions for CIC

## Overview
Investigation of when the chain rule holds for Computational Information Complexity.

## Chain Rule
For standard information theory:
I(X;Y,Z) = I(X;Y) + I(X;Z|Y)

## Question
Does a similar chain rule hold for CIC?

## Results

### Positive Result
If P and Q are independent problems (no shared structure), then:
IC(P AND Q) = IC(P) + IC(Q)

### Negative Result
In general, the chain rule does NOT hold for CIC:
There exist P, Q such that IC(P AND Q) < IC(P) + IC(Q)

### Example
Let P = SAT and Q = the complement of SAT.
Then IC(P AND Q) = IC(SAT) but IC(P) + IC(Q) = 2*IC(SAT).

## Implications
The failure of the chain rule makes CIC analysis more complex but also more interesting. It means that computational information can be "reused" across related problems.

## Status: Completed
