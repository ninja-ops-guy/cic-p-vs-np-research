"""
Circuit Information Complexity Framework
Analyzes circuit complexity using information-theoretic measures.
"""

import numpy as np
from typing import List, Tuple, Dict

class Circuit:
    """Represents a Boolean circuit."""
    
    def __init__(self, n_inputs: int):
        self.n_inputs = n_inputs
        self.gates = []
        self.wires = []
        
    def add_gate(self, gate_type: str, inputs: List[int]) -> int:
        """Add a gate to the circuit. Returns output wire index."""
        gate_id = len(self.gates)
        self.gates.append((gate_type, inputs))
        output_wire = self.n_inputs + gate_id
        self.wires.append(output_wire)
        return output_wire
    
    def size(self) -> int:
        """Return circuit size (number of gates)."""
        return len(self.gates)
    
    def depth(self) -> int:
        """Return circuit depth."""
        if not self.gates:
            return 0
        
        depths = [0] * self.n_inputs
        for gate_type, inputs in self.gates:
            gate_depth = max(depths[i] for i in inputs) + 1
            depths.append(gate_depth)
        
        return max(depths)
    
    def information_capacity(self) -> float:
        """
        Estimate information capacity of the circuit.
        
        Returns:
            Estimated bits of information processed
        """
        # Each gate processes information from its inputs
        total_capacity = 0.0
        
        for gate_type, inputs in self.gates:
            n_inputs = len(inputs)
            # Information capacity of a gate
            if gate_type in ['AND', 'OR']:
                gate_capacity = n_inputs  # Each input contributes 1 bit
            elif gate_type == 'NOT':
                gate_capacity = 1
            elif gate_type == 'XOR':
                gate_capacity = n_inputs
            else:
                gate_capacity = n_inputs
            
            total_capacity += gate_capacity
        
        return total_capacity

class CircuitAnalyzer:
    """Analyzes circuits using information complexity."""
    
    def __init__(self):
        self.results = []
    
    def analyze_circuit(self, circuit: Circuit) -> Dict:
        """Comprehensive circuit analysis."""
        return {
            'size': circuit.size(),
            'depth': circuit.depth(),
            'info_capacity': circuit.information_capacity(),
            'info_per_gate': circuit.information_capacity() / max(1, circuit.size()),
            'n_inputs': circuit.n_inputs
        }
    
    def compare_circuits(self, circuits: List[Circuit]) -> Dict:
        """Compare multiple circuits."""
        analyses = [self.analyze_circuit(c) for c in circuits]
        
        return {
            'sizes': [a['size'] for a in analyses],
            'depths': [a['depth'] for a in analyses],
            'capacities': [a['info_capacity'] for a in analyses],
            'min_size': min(a['size'] for a in analyses),
            'max_depth': max(a['depth'] for a in analyses)
        }
    
    def lower_bound_estimate(self, n_inputs: int, complexity_class: str) -> int:
        """
        Estimate circuit size lower bound for a complexity class.
        
        Args:
            n_inputs: Number of inputs
            complexity_class: 'P', 'NP', etc.
            
        Returns:
            Estimated minimum circuit size
        """
        if complexity_class == 'P':
            # Polynomial size
            return int(n_inputs ** 2)
        elif complexity_class == 'NP':
            # May require exponential size
            return int(2 ** (n_inputs / 2))
        else:
            return int(2 ** n_inputs / n_inputs)

def create_example_circuit() -> Circuit:
    """Create an example circuit computing parity."""
    circuit = Circuit(4)
    
    # Compute XOR of all inputs
    g1 = circuit.add_gate('XOR', [0, 1])
    g2 = circuit.add_gate('XOR', [2, 3])
    g3 = circuit.add_gate('XOR', [g1, g2])
    
    return circuit

def main():
    """Run circuit analysis examples."""
    print("Circuit Information Complexity Framework")
    print("=" * 50)
    
    # Create and analyze example circuit
    circuit = create_example_circuit()
    analyzer = CircuitAnalyzer()
    
    result = analyzer.analyze_circuit(circuit)
    print(f"\nParity Circuit Analysis:")
    print(f"  Size: {result['size']} gates")
    print(f"  Depth: {result['depth']}")
    print(f"  Information Capacity: {result['info_capacity']:.2f} bits")
    print(f"  Info per Gate: {result['info_per_gate']:.2f} bits")
    
    # Lower bound estimates
    for cls in ['P', 'NP']:
        lb = analyzer.lower_bound_estimate(10, cls)
        print(f"\n  Estimated {cls} lower bound (n=10): {lb} gates")

if __name__ == "__main__":
    main()
