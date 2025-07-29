from collections import defaultdict, deque
import heapq
from typing import Dict, List, Tuple, Optional, Set


def find_shortest_path(connectivity: List[Tuple[int, int]], start: int, end: int) -> Optional[List[int]]:
    """Find shortest path between two qubits using BFS."""
    graph = defaultdict(list)
    for q1, q2 in connectivity:
        graph[q1].append(q2)
        graph[q2].append(q1)

    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        vertex, path = queue.popleft()
        if vertex == end:
            return path

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None


def calculate_total_error(circuit: Dict) -> float:
    """Calculate total error rate of the circuit."""
    return sum(gate['error'] for gate in circuit.values())


def calculate_total_time(circuit: Dict) -> float:
    """Calculate total execution time of the circuit."""
    return sum(gate['time'] for gate in circuit.values())


def insert_swap_gates(circuit: Dict, path: List[int], swap_time: float, swap_error: float, 
                     max_gate_id: int) -> Tuple[Dict, int]:
    """Insert SWAP gates along the path."""
    new_circuit = circuit.copy()
    current_id = max_gate_id + 1

    for i in range(len(path) - 2):
        new_circuit[current_id] = {
            'type': 'SWAP',
            'qubits': [path[i], path[i + 1]],
            'time': swap_time,
            'error': swap_error
        }
        current_id += 1

    return new_circuit, current_id


def update_qubit_positions(mapping: Dict[int, int], swap_qubits: List[int]) -> Dict[int, int]:
    """Update qubit positions after SWAP operation."""
    new_mapping = mapping.copy()
    q1, q2 = swap_qubits
    
    # Find virtual qubits at physical positions q1 and q2
    v1 = None
    v2 = None
    for v, p in new_mapping.items():
        if p == q1:
            v1 = v
        elif p == q2:
            v2 = v

    # Swap their positions
    if v1 is not None and v2 is not None:
        new_mapping[v1] = q2
        new_mapping[v2] = q1

    return new_mapping


def optimize_circuit(circuit: Dict, connectivity: List[Tuple[int, int]], 
                    swap_time: float, swap_error: float, max_error: float,
                    initial_mapping: Dict[int, int]) -> Optional[Dict]:
    """
    Optimize quantum circuit by inserting SWAP gates while respecting constraints.
    """
    if not connectivity or not circuit:
        return None

    # Initialize variables
    current_mapping = initial_mapping.copy()
    optimized_circuit = {}
    max_gate_id = max(circuit.keys())
    current_time = 0
    executed_gates = set()
    ready_gates = []

    # Create dependency graph
    dependencies = defaultdict(set)
    dependents = defaultdict(set)
    for gate_id, gate in circuit.items():
        if len(gate['qubits']) == 2:  # Two-qubit gate
            q1, q2 = gate['qubits']
            # Find all gates that use these qubits and come before this gate
            for other_id, other_gate in circuit.items():
                if other_id < gate_id:
                    if q1 in other_gate['qubits'] or q2 in other_gate['qubits']:
                        dependencies[gate_id].add(other_id)
                        dependents[other_id].add(gate_id)

    # Initialize ready gates (gates with no dependencies)
    for gate_id in circuit:
        if not dependencies[gate_id]:
            heapq.heappush(ready_gates, (current_time, gate_id))

    while ready_gates:
        _, gate_id = heapq.heappop(ready_gates)
        if gate_id in executed_gates:
            continue

        gate = circuit[gate_id]
        new_circuit = optimized_circuit.copy()

        # For two-qubit gates, check if qubits are adjacent
        if len(gate['qubits']) == 2:
            q1, q2 = gate['qubits']
            p1 = current_mapping[q1]
            p2 = current_mapping[q2]

            # If qubits are not adjacent, find path and insert SWAP gates
            if (p1, p2) not in connectivity and (p2, p1) not in connectivity:
                path = find_shortest_path(connectivity, p1, p2)
                if not path:
                    return None

                # Insert SWAP gates
                new_circuit, new_max_id = insert_swap_gates(
                    new_circuit, path, swap_time, swap_error, max_gate_id
                )
                max_gate_id = new_max_id

                # Update qubit positions
                for i in range(len(path) - 2):
                    current_mapping = update_qubit_positions(
                        current_mapping, [path[i], path[i + 1]]
                    )

        # Add the original gate
        new_circuit[gate_id] = gate

        # Check if adding these gates would exceed max_error
        if calculate_total_error(new_circuit) > max_error:
            return None

        # Update the circuit and executed gates
        optimized_circuit = new_circuit
        executed_gates.add(gate_id)
        current_time = calculate_total_time(optimized_circuit)

        # Update ready gates
        for dependent in dependents[gate_id]:
            if dependencies[dependent].issubset(executed_gates):
                heapq.heappush(ready_gates, (current_time, dependent))

    return optimized_circuit