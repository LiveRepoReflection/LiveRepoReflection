import random
from itertools import product

def quantum_simulator(n, initial_state, gates, num_samples):
    """
    Simulate a quantum computation.
    
    Args:
        n: Number of quantum registers
        initial_state: String of n characters, each '0' or '1', representing the initial state
        gates: List of tuples representing quantum gates
        num_samples: Number of times to run the simulation
    
    Returns:
        Dictionary mapping final states to counts
    """
    # Validate inputs
    if n < 1 or n > 30:
        raise ValueError("Number of registers must be between 1 and 30")
    
    if len(initial_state) != n:
        raise ValueError(f"Initial state must be a string of length {n}")
    
    if not all(bit in '01' for bit in initial_state):
        raise ValueError("Initial state must contain only '0' and '1'")
    
    if num_samples < 1 or num_samples > 100000:
        raise ValueError("Number of samples must be between 1 and 100000")
    
    # Initialize result dictionary with all possible states
    result = {''.join(bits): 0 for bits in product('01', repeat=n)}
    
    # Run the simulation num_samples times
    for _ in range(num_samples):
        # Start with the initial state for each sample
        state = list(initial_state)
        
        # Apply gates sequentially
        for gate in gates:
            if gate[0] == 'H':
                register = gate[1]
                if register < 0 or register >= n:
                    raise ValueError(f"Register index {register} out of range [0, {n-1}]")
                
                # Apply Hadamard gate (50% chance of 0, 50% chance of 1)
                state[register] = random.choice(['0', '1'])
                
            elif gate[0] == 'CNOT':
                control, target = gate[1], gate[2]
                if control < 0 or control >= n or target < 0 or target >= n:
                    raise ValueError(f"Register indices must be in range [0, {n-1}]")
                if control == target:
                    raise ValueError("Control and target registers must be different")
                
                # Apply CNOT gate
                if state[control] == '1':
                    # Flip the target bit if control bit is 1
                    state[target] = '1' if state[target] == '0' else '0'
            else:
                raise ValueError(f"Unknown gate type: {gate[0]}")
        
        # Convert state list back to string and increment count
        final_state = ''.join(state)
        result[final_state] += 1
    
    return result