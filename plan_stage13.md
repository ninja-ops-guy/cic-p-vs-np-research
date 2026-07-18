# Stage 13: Pebbling Formula Attack + Unconditional Depth Bounds

## The Pebbling Formula Idea

Pebbling formulas encode the pebbling game on directed acyclic graphs. They have:
- Strong proof complexity lower bounds (exponential in the pebbling number)
- Natural connection to circuit evaluation (pebbling = space-bounded computation)
- Well-studied graph families with known pebbling numbers

## Stage 13 Tracks

### Track AAA: Pebbling Formula Framework — ❌ Resolution width doesn't imply KW communication
### Track BBB: Restriction Argument — ❌ **Barrington's Theorem: bounded-pathwidth = NC¹ exactly**
### Track CCC: MUX-Based Alternative Path — ❌ Structural mismatch with SAT
### Track DDD: Unconditional ω(log n) — ❌ Scaling cancellation yields only constant bounds

## Key Discovery

**Barrington's Theorem (1986): NC¹ = pathwidth-O(1) circuits.**

This means the CIC framework has ZERO slack. Proving CIC_circuit(SAT) = ω(log n) IS proving P ⊄ NC¹.
