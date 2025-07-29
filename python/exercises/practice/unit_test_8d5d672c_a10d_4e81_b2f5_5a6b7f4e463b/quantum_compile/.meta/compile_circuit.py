import collections

def compile_circuit(architecture, circuit):
    num_qubits = len(architecture)
    # mapping: index represents the physical qubit and value is the logical qubit currently at that physical location.
    mapping = list(range(num_qubits))
    compiled = []
    
    def shortest_path(start, goal):
        # BFS to find the shortest path between start and goal in the architecture graph.
        queue = collections.deque()
        queue.append((start, [start]))
        visited = set([start])
        while queue:
            current, path = queue.popleft()
            if current == goal:
                return path
            for neighbor in architecture.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    for gate in circuit:
        gate_type, q1, q2 = gate
        if gate_type == "H":
            # For H gate, q2 is the logical qubit.
            physical = mapping.index(q2)
            compiled.append(("H", None, physical))
        elif gate_type == "CNOT":
            # For CNOT, q1 is control and q2 is target (logical qubits).
            control_physical = mapping.index(q1)
            target_physical = mapping.index(q2)
            # Check if control and target are adjacent in the architecture.
            if target_physical in architecture.get(control_physical, []):
                compiled.append(("CNOT", control_physical, target_physical))
            else:
                # Find a shortest path from control to target physical qubit.
                path = shortest_path(control_physical, target_physical)
                if not path or len(path) < 2:
                    raise ValueError("No valid path found between qubits")
                # If direct neighbors, len(path) would be 2.
                # Otherwise, we swap along the path to bring qubits adjacent.
                # This solution moves the control qubit along the path towards the target.
                swap_sequence = []
                for i in range(len(path) - 2):
                    p_current = path[i]
                    p_next = path[i+1]
                    # Append swap gate and update mapping.
                    compiled.append(("SWAP", p_current, p_next))
                    mapping[p_current], mapping[p_next] = mapping[p_next], mapping[p_current]
                    swap_sequence.append((p_current, p_next))
                # After swaps, the control qubit is at path[-2].
                new_control = path[-2]
                if target_physical not in architecture.get(new_control, []):
                    raise ValueError("SWAP sequence did not result in adjacent qubits")
                compiled.append(("CNOT", new_control, target_physical))
                # Reverse the swaps to restore original mapping.
                for p_current, p_next in reversed(swap_sequence):
                    compiled.append(("SWAP", p_current, p_next))
                    mapping[p_current], mapping[p_next] = mapping[p_next], mapping[p_current]
        else:
            raise ValueError(f"Unknown gate type: {gate_type}")
    return compiled