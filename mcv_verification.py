"""
MCV Verification Tool
Verifies results related to the Minimum Circuit Value problem.
"""

import itertools

def evaluate_circuit(circuit, inputs):
    """
    Evaluate a Boolean circuit on given inputs.
    
    Args:
        circuit: List of gates, each gate is (type, input1, input2)
        inputs: Dictionary mapping input names to values
        
    Returns:
        Output value of the circuit
    """
    values = dict(inputs)
    
    for gate in circuit:
        gate_type, in1, in2 = gate
        v1 = values[in1]
        v2 = values[in2]
        
        if gate_type == 'AND':
            values[f"g_{len(values)}"] = v1 & v2
        elif gate_type == 'OR':
            values[f"g_{len(values)}"] = v1 | v2
        elif gate_type == 'NOT':
            values[f"g_{len(values)}"] = 1 - v1
            
    return values[f"g_{len(values)-1}"]

def verify_mcv_formula(formula, expected_value):
    """
    Verify a formula by exhaustive search.
    
    Args:
        formula: CNF formula as list of clauses
        expected_value: Expected satisfiability
        
    Returns:
        True if formula matches expected value
    """
    # Find all variables
    vars_set = set()
    for clause in formula:
        for lit in clause:
            vars_set.add(abs(lit))
    
    n = len(vars_set)
    
    # Try all assignments
    for assignment in itertools.product([0, 1], repeat=n):
        sat = True
        for clause in formula:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit < 0:
                    val = 1 - val
                if val == 1:
                    clause_sat = True
                    break
            if not clause_sat:
                sat = False
                break
        
        if sat and expected_value == 'SAT':
            return True
        if sat and expected_value == 'UNSAT':
            return False
    
    return expected_value == 'UNSAT'

def main():
    """Run verification tests."""
    print("MCV Verification Tool")
    print("=" * 50)
    
    # Test 1: Simple satisfiable formula
    formula1 = [[1, 2], [-1, 2]]
    result1 = verify_mcv_formula(formula1, 'SAT')
    print(f"Test 1 (SAT): {'PASS' if result1 else 'FAIL'}")
    
    # Test 2: Simple unsatisfiable formula
    formula2 = [[1], [-1]]
    result2 = verify_mcv_formula(formula2, 'UNSAT')
    print(f"Test 2 (UNSAT): {'PASS' if result2 else 'FAIL'}")
    
    print("\nVerification complete.")

if __name__ == "__main__":
    main()
