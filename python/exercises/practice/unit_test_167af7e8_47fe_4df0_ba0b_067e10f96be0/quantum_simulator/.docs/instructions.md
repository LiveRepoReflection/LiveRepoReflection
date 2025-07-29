## The Quantum Supremacy Simulator

**Problem Description:**

You are tasked with building a simplified simulator for a quantum computer performing a specific calculation. While a real quantum computer operates on qubits, superposition, and entanglement, we will model its behavior using classical computation and probabilistic outcomes.

Specifically, you need to simulate the execution of a rudimentary quantum algorithm on a system of *n* "quantum registers." Each register can be in one of two states, represented by 0 or 1. The algorithm consists of a sequence of "quantum gates" applied to these registers.

**Gates:**

We will implement two types of quantum gates:

1.  **Hadamard Gate (H):** When applied to a register, it puts it into an equal superposition of 0 and 1. Classically, this means that the register has a 50% chance of becoming 0 and a 50% chance of becoming 1.

2.  **Controlled-NOT Gate (CNOT):** This gate takes two registers as input: a "control" register and a "target" register. If the control register is in state 1, the target register is flipped (0 becomes 1, and 1 becomes 0). If the control register is in state 0, the target register remains unchanged.

**Input:**

The input will consist of the following:

*   *n*: The number of quantum registers (1 <= *n* <= 30).
*   *initial_state*: A string of *n* characters, each being either '0' or '1', representing the initial state of the registers.
*   *gates*: A list of tuples, where each tuple represents a quantum gate.  A tuple can be one of the following forms:
    *   `('H', i)`:  Apply a Hadamard gate to register *i* (0 <= *i* < *n*).
    *   `('CNOT', c, t)`: Apply a CNOT gate with control register *c* and target register *t* (0 <= *c*, *t* < *n*; *c* != *t*).
*   *num_samples*: The number of times to run the simulation (1 <= *num_samples* <= 100000).

**Output:**

The output should be a dictionary where the keys are strings representing the final state of the *n* registers (e.g., "0101") and the values are the number of times that state was observed after running the simulation *num_samples* times. The dictionary should include all possible states, even if their counts are 0. The keys should be sorted lexicographically.

**Constraints:**

1.  **Probabilistic Nature:** The Hadamard gate introduces randomness. Your simulator *must* accurately reflect the probabilities involved.
2.  **Efficiency:**  Although this is a simulation, aim for reasonable efficiency.  Large values of *num_samples* will require optimized code.
3.  **Completeness:** Ensure that all possible states are accounted for in the final counts dictionary, regardless of whether they appear in the sampled states.
4.  **Edge Cases:** Handle cases where no gates are applied and cases where *n* is small or large within the specified range.
5.  **Correctness:** The simulation must accurately model the application of the specified quantum gates. The distribution of final states should be statistically correct given the gates applied.

**Example:**

```python
n = 2
initial_state = "00"
gates = [('H', 0), ('CNOT', 0, 1)]
num_samples = 1000

# Expected Output (approximate):
# {'00': 500, '01': 0, '10': 0, '11': 500}  #Due to hadamard gate on register 0, then CNOT operation

```

This problem combines understanding of basic quantum gate operations with the practical application of simulation techniques and efficient data structures. It requires careful consideration of probability and efficiency to produce accurate results for a large number of samples. Good luck!
