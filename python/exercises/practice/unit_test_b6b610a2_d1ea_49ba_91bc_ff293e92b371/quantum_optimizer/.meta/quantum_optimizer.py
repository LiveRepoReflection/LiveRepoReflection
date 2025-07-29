import heapq
from collections import defaultdict, deque
import copy

def optimize_quantum_circuit(circuit_dag, qubit_adjacency_graph, allowed_gates, gate_dependencies):
    """
    Optimizes a quantum circuit for execution on a NISQ computer.
    
    Args:
        circuit_dag: Dictionary representing the DAG of the quantum circuit.
        qubit_adjacency_graph: Dictionary representing qubit connectivity.
        allowed_gates: Dictionary of allowed gate types for each qubit.
        gate_dependencies: Dictionary of temporal gate dependency constraints.
    
    Returns:
        Tuple containing (schedule, total_execution_time, overall_fidelity).
    """
    # Handle empty circuit case
    if not circuit_dag:
        return [], 0, 1.0
    
    # Validate architectural constraints
    validate_circuit(circuit_dag, qubit_adjacency_graph, allowed_gates)
    
    # Create a copy of the circuit DAG to work with
    dag = copy.deepcopy(circuit_dag)
    
    # Calculate in-degree for each node (number of dependencies)
    in_degree = {gate_id: len(info["dependencies"]) for gate_id, info in dag.items()}
    
    # Create a mapping from each gate to gates that depend on it
    dependents = defaultdict(list)
    for gate_id, info in dag.items():
        for dep in info["dependencies"]:
            dependents[dep].append(gate_id)
    
    # Find gates with no dependencies (in_degree = 0)
    ready_gates = [(0, gate_id) for gate_id, degree in in_degree.items() if degree == 0]
    heapq.heapify(ready_gates)  # Priority queue sorted by earliest possible start time
    
    # Track which qubits are busy and until when
    qubit_busy_until = defaultdict(int)
    
    # Track when each gate finishes execution
    gate_finish_time = {}
    
    # Create the schedule (gate_id, start_time)
    schedule = []
    
    # Track overall fidelity
    overall_fidelity = 1.0
    
    while ready_gates:
        earliest_time, gate_id = heapq.heappop(ready_gates)
        gate_info = dag[gate_id]
        
        # Find the earliest time this gate can start, considering:
        # 1. All dependencies must be completed
        # 2. All qubits must be available
        # 3. Temporal constraints must be satisfied
        
        # Check when qubits are available
        qubits_available_at = max([qubit_busy_until[q] for q in gate_info["qubits"]], default=0)
        
        # Calculate earliest possible start time
        start_time = max(earliest_time, qubits_available_at)
        
        # Check temporal dependencies
        if gate_id in gate_dependencies:
            for dep_gate, time_window in gate_dependencies[gate_id]:
                if dep_gate in gate_finish_time:
                    # The dependent gate must be scheduled within the time window
                    dep_finish_time = gate_finish_time[dep_gate]
                    if start_time > dep_finish_time + time_window - gate_info["execution_time"]:
                        # Cannot satisfy temporal constraint
                        raise ValueError(f"Cannot satisfy temporal constraint for {gate_id}: {dep_gate} within {time_window}")
                    start_time = min(start_time, dep_finish_time + time_window - gate_info["execution_time"])
        
        # Update schedule
        schedule.append((gate_id, start_time))
        
        # Update qubit busy times
        finish_time = start_time + gate_info["execution_time"]
        for qubit in gate_info["qubits"]:
            qubit_busy_until[qubit] = finish_time
        
        # Record when this gate finishes
        gate_finish_time[gate_id] = finish_time
        
        # Update fidelity
        overall_fidelity *= gate_info["fidelity"]
        
        # Update dependencies (reduce in-degree for dependent gates)
        for dependent in dependents[gate_id]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                # This gate is now ready to be scheduled
                # Its earliest possible start time is the finish time of the current gate
                heapq.heappush(ready_gates, (finish_time, dependent))
    
    # Calculate total execution time
    total_execution_time = max(gate_finish_time.values(), default=0)
    
    # Sort schedule by start time
    schedule.sort(key=lambda x: x[1])
    
    return schedule, total_execution_time, overall_fidelity

def validate_circuit(circuit_dag, qubit_adjacency_graph, allowed_gates):
    """
    Validates that the circuit satisfies architectural constraints.
    
    Args:
        circuit_dag: Dictionary representing the DAG of the quantum circuit.
        qubit_adjacency_graph: Dictionary representing qubit connectivity.
        allowed_gates: Dictionary of allowed gate types for each qubit.
    
    Raises:
        ValueError: If the circuit violates any architectural constraints.
    """
    # Check if the circuit DAG is valid
    if not is_dag_valid(circuit_dag):
        raise ValueError("Circuit DAG contains cycles or invalid dependencies")
    
    # Check architectural constraints for each gate
    for gate_id, gate_info in circuit_dag.items():
        qubits = gate_info["qubits"]
        gate_type = gate_info["gate_type"]
        
        # Check if the gate type is allowed for all qubits
        for qubit in qubits:
            if qubit not in allowed_gates:
                raise ValueError(f"Qubit {qubit} does not exist in the architecture")
            if gate_type not in allowed_gates[qubit]:
                raise ValueError(f"Gate type {gate_type} is not allowed for qubit {qubit}")
        
        # Check connectivity for multi-qubit gates
        if len(qubits) > 1:
            for i in range(len(qubits)):
                for j in range(i+1, len(qubits)):
                    q1, q2 = qubits[i], qubits[j]
                    if q2 not in qubit_adjacency_graph.get(q1, []) and q1 not in qubit_adjacency_graph.get(q2, []):
                        raise ValueError(f"Qubits {q1} and {q2} are not adjacent for gate {gate_id}")

def is_dag_valid(circuit_dag):
    """
    Checks if the circuit DAG is a valid DAG (no cycles).
    
    Args:
        circuit_dag: Dictionary representing the DAG of the quantum circuit.
    
    Returns:
        bool: True if the DAG is valid, False otherwise.
    """
    # Create a graph representation
    graph = defaultdict(list)
    for gate_id, gate_info in circuit_dag.items():
        for dep in gate_info["dependencies"]:
            if dep not in circuit_dag:
                return False  # Dependency doesn't exist
            graph[dep].append(gate_id)
    
    # Check for cycles using topological sort
    in_degree = defaultdict(int)
    for gate_id in circuit_dag:
        in_degree[gate_id] = 0
    
    for gate_id in circuit_dag:
        for neighbor in graph[gate_id]:
            in_degree[neighbor] += 1
    
    queue = deque([gate_id for gate_id in circuit_dag if in_degree[gate_id] == 0])
    visited_count = 0
    
    while queue:
        gate_id = queue.popleft()
        visited_count += 1
        
        for neighbor in graph[gate_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # If we visited all nodes, then the graph has no cycles
    return visited_count == len(circuit_dag)