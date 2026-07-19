# CIC Security Tools Suite

Four production-grade security tools built directly on the CIC research framework.

## Tools

| Tool | Research Foundation | Security Application |
|------|--------------------|---------------------|
| **MINOTAUR** | NPT (Stage 18): N_φ is Galois closure | Minimal trigger / root-cause finding |
| **CLIFFHANGER** | ETC (Stage 17): Entropy trajectory complexity | Hidden catastrophic failure detection |
| **FORTRESS** | Theorem 1: Treewidth controls complexity | Structural security assessment |
| **CERBERUS** | Universal Tractability + BMC | Bounded exploit path discovery |

---

## MINOTAUR — Minimal Trigger Finder

Finds the **provably smallest** set of conditions that trigger a security violation.

Unlike gradient-based methods, MINOTAUR uses **logical necessity propagation** (N_φ)
to find triggers that are minimal by mathematical proof, not approximation.

```bash
python minotaur.py --policy policy.cnf --violation "-42" --max-size 5
```

**Use cases:**
- Configuration vulnerability: "What is the smallest set of flags that disables MFA?"
- Policy bypass: "What minimal permissions grant admin access?"
- Root cause: "What is the minimal input that crashes this parser?"

---

## CLIFFHANGER — Catastrophic Failure Detector

Identifies systems with **hidden catastrophic failure modes** — systems that appear
stable but have sudden, dramatic failures under specific conditions.

Based on ETC: systems with "entropy cliffs" have abrupt transitions from safe to unsafe.

```bash
python cliffhanger.py --system system.cnf --profile
```

**Use cases:**
- Pre-deployment: "Will this auth system suddenly fail under load?"
- Fuzzing guidance: "Target these specific input regions for maximum impact"
- Hardening validation: "Did our patches eliminate the cliff behavior?"

---

## FORTRESS — Structural Security Assessor

Assigns a **quantitative security score** to constraint-based systems based on
treewidth analysis. Low treewidth = structurally vulnerable.

```bash
python fortress.py --dimacs access_control.cnf --report
```

**Use cases:**
- Architecture review: "Is our RBAC system structurally secure?"
- Pre-acquisition: "Score the security of this third-party IAM"
- Defense validation: "Did our complexity additions actually raise the barrier?"

---

## CERBERUS — Bounded Exploit Path Discovery

Finds **concrete attack traces** that lead from an initial state to a violation
within a bounded number of steps. Leverages bounded treewidth for tractability.

```bash
python cerberus.py --transition tx.cnf --initial init.cnf --bad violation.cnf --bound 10
```

**Use cases:**
- Protocol audit: "Can an attacker escalate privileges in 5 steps?"
- Smart contract: "Is there a reentrancy path within 3 calls?"
- State machine: "Can we reach the error state from normal operation?"

---

## Installation

```bash
pip install networkx  # only dependency
python -m pytest tests/  # 32 tests
```

## Research Citations

| Tool | Stage | Key Theorem |
|------|-------|-------------|
| MINOTAUR | Stage 18 | N_φ is Galois closure operator |
| CLIFFHANGER | Stage 17 | ETC(φ) = O(w·n), cliff detection |
| FORTRESS | Stages 1-12 | width w → res-width ≤ max(w,k) |
| CERBERUS | Stages 1-8 | Universal Tractability (10 proof systems) |
