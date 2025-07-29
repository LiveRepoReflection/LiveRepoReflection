import heapq
from collections import defaultdict

def optimize_circuit(num_qubits, coupling_map, circuit):
    """Optimize a quantum circuit to satisfy qubit connectivity constraints."""
    optimized_circuit = []
    physical_to_logical = {i: i for i in range(num_qubits)}
    logical_to_physical = {i: i for i in range(num_qubits)}
    
    # Build adjacency list for the coupling map
    coupling_graph = defaultdict(list)
    for a, b in coupling_map:
        coupling_graph[a].append(b)
        coupling_graph[b].append(a)
    
    for gate in circuit:
        gate_name, qubits, params = gate
        
        if gate_name in ["H", "RZ"]:
            # Single-qubit gates can be applied directly
            physical_qubit = logical_to_physical[qubits[0]]
            optimized_circuit.append((gate_name, [physical_qubit], params))
        elif gate_name in ["CNOT", "SWAP"]:
            control, target = qubits
            physical_control = logical_to_physical[control]
            physical_target = logical_to_physical[target]
            
            if (physical_control, physical_target) in coupling_map or \
               (physical_target, physical_control) in coupling_map:
                # Directly connected, apply gate
                optimized_circuit.append((gate_name, [physical_control, physical_target], params))
                if gate_name == "SWAP":
                    # Update mappings
                    logical_to_physical[control], logical_to_physical[target] = \
                        logical_to_physical[target], logical_to_physical[control]
                    physical_to_logical[physical_control], physical_to_logical[physical_target] = \
                        physical_to_logical[physical_target], physical_to_logical[physical_control]
            else:
                # Need to route qubits together
                path = find_shortest_path(coupling_graph, physical_control, physical_target)
                if not path:
                    raise ValueError(f"No path found between qubits {physical_control} and {physical_target}")
                
                # Insert SWAPs to bring control and target adjacent
                for i in range(len(path) - 1):
                    a, b = path[i], path[i+1]
                    optimized_circuit.append(("SWAP", [a, b], []))
                    
                    # Update mappings after each SWAP
                    logical_a = physical_to_logical[a]
                    logical_b = physical_to_logical[b]
                    logical_to_physical[logical_a], logical_to_physical[logical_b] = \
                        logical_to_physical[logical_b], logical_to_physical[logical_a]
                    physical_to_logical[a], physical_to_logical[b] = \
                        physical_to_logical[b], physical_to_logical[a]
                
                # Apply the gate now that qubits are adjacent
                new_control = logical_to_physical[control]
                new_target = logical_to_physical[target]
                optimized_circuit.append((gate_name, [new_control, new_target], params))
                
                # Reverse the SWAPs to return qubits to original positions
                for i in range(len(path) - 1, 0, -1):
                    a, b = path[i-1], path[i]
                    optimized_circuit.append(("SWAP", [a, b], []))
                    
                    # Update mappings after each SWAP
                    logical_a = physical_to_logical[a]
                    logical_b = physical_to_logical[b]
                    logical_to_physical[logical_a], logical_to_physical[logical_b] = \
                        logical_to_physical[logical_b], logical_to_physical[logical_a]
                    physical_to_logical[a], physical_to_logical[b] = \
                        physical_to_logical[b], physical_to_logical[a]
    
    return optimized_circuit

def find_shortest_path(graph, start, end):
    """Find shortest path between two nodes using Dijkstra's algorithm."""
    heap = [(0, start, [])]
    visited = set()
    
    while heap:
        cost, node, path = heapq.heappop(heap)
        if node == end:
            return path + [node]
        
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                heapq.heappush(heap, (cost + 1, neighbor, path + [node]))
    
    return None