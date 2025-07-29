def optimize_circuit(dag):
    # If no nodes, return empty list.
    if not dag["nodes"]:
        return []
    
    nodes = dag["nodes"]
    edges = dag.get("edges", {})
    
    # Compute in-degree for each node.
    in_degree = {node: 0 for node in nodes}
    for src, dests in edges.items():
        for dest in dests:
            in_degree[dest] += 1
    
    # Initialize frontier with nodes with zero in-degree, sorted by id.
    frontier = [node for node in nodes if in_degree[node] == 0]
    frontier.sort()
    
    ordering = []
    last_cnot_qubits = None

    while frontier:
        candidate = None

        # Partition frontier into CNOT and SingleQubit candidates.
        cnot_candidates = []
        single_candidates = []
        for node_id in frontier:
            gate = nodes[node_id]
            if gate["type"] == "CNOT":
                cnot_candidates.append(node_id)
            else:
                single_candidates.append(node_id)

        if last_cnot_qubits is not None and cnot_candidates:
            # Among CNOT candidates, select those with common qubits with the last scheduled CNOT.
            common_candidates = []
            for node_id in cnot_candidates:
                gate = nodes[node_id]
                if gate["qubits"] & last_cnot_qubits:
                    common_candidates.append(node_id)
            if common_candidates:
                # Choose the candidate with the maximal intersection size; tie-break by id.
                best = None
                best_score = -1
                for node_id in common_candidates:
                    gate = nodes[node_id]
                    score = len(gate["qubits"] & last_cnot_qubits)
                    if score > best_score or (score == best_score and node_id < best):
                        best = node_id
                        best_score = score
                candidate = best
            elif cnot_candidates:
                # No candidate shares qubits with the last scheduled CNOT; choose the smallest id.
                candidate = sorted(cnot_candidates)[0]
        elif not last_cnot_qubits and cnot_candidates:
            # If no CNOT has been scheduled yet, start with a CNOT candidate.
            candidate = sorted(cnot_candidates)[0]

        if candidate is None:
            # If no CNOT candidates are available, choose from SingleQubit candidates.
            candidate = sorted(single_candidates)[0]

        # Remove candidate from frontier and add to ordering.
        frontier.remove(candidate)
        ordering.append(candidate)

        # Update the last scheduled CNOT qubits if applicable.
        if nodes[candidate]["type"] == "CNOT":
            last_cnot_qubits = nodes[candidate]["qubits"]

        # Decrease in-degree for neighbors; add any with zero in-degree to frontier.
        for neighbor in edges.get(candidate, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                frontier.append(neighbor)
        frontier.sort()
    return ordering

if __name__ == '__main__':
    # Example run with a sample DAG.
    sample_dag = {
        "nodes": {
            "G1": {"id": "G1", "type": "CNOT", "qubits": {0, 1}},
            "G2": {"id": "G2", "type": "CNOT", "qubits": {1, 2}},
            "G3": {"id": "G3", "type": "SingleQubit", "qubits": {2}},
        },
        "edges": {
            "G1": ["G2"],
            "G2": ["G3"],
            "G3": []
        }
    }
    order = optimize_circuit(sample_dag)
    print(order)