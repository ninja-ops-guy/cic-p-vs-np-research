# P vs NP Dimension 13: Descriptive Complexity

## Overview
Analysis of descriptive complexity and its connection to P vs NP.

## Descriptive Complexity

### Definition
Characterizes complexity classes in terms of logical definability.

### Key Result (Fagin)
NP = SO-E (second-order existential logic).

## Logical Characterizations

| Class | Logic |
|-------|-------|
| P | FO(LFP) - First-order with least fixed point |
| NP | SO-E - Second-order existential |
| PSPACE | FO(PFP) - First-order with partial fixed point |
| L | FO(DTC) - First-order with deterministic transitive closure |

## Implications for P vs NP

### Observation
P = NP iff every SO-E definable property is also FO(LFP) definable.

### Consequence
Proving P != NP requires showing some SO-E property is not FO(LFP).

## The CIC Perspective

### Information in Logic
The complexity of a logical formula relates to the information it can express.

### Conjecture
IC(SO-E) > IC(FO(LFP)), explaining the separation.

## Status: Completed
