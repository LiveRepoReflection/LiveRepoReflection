def allocate_files(N, M, replication_factor, node_capacities, node_locations, file_sizes, file_popularities, client_location):
    # Helper function: Manhattan distance between two points.
    def manhattan_distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    
    # Keep track of remaining capacities for nodes.
    remaining_capacity = list(node_capacities)
    
    # Prepare sorted order of nodes based on distance from client.
    node_order = sorted(range(N), key=lambda i: manhattan_distance(client_location, node_locations[i]))
    
    # Process files in descending order of popularity.
    # For tie-breaking, use original index order.
    file_indices_sorted = sorted(range(M), key=lambda i: (-file_popularities[i], i))
    
    # Initialize an allocation dictionary mapping file index to selected nodes list.
    allocation_dict = {i: [] for i in range(M)}
    
    for file_idx in file_indices_sorted:
        file_size = file_sizes[file_idx]
        selected_nodes = []
        
        # Try to select replication_factor nodes from the pre-sorted order.
        for node in node_order:
            if remaining_capacity[node] >= file_size:
                selected_nodes.append(node)
                remaining_capacity[node] -= file_size
                if len(selected_nodes) == replication_factor:
                    break
        # If we couldn't allocate enough nodes, we need to backtrack (greedy fallback)
        # Here we try to reassign already allocated replicas if possible.
        if len(selected_nodes) < replication_factor:
            # Reset the capacity changes made for the current file.
            for node in selected_nodes:
                remaining_capacity[node] += file_size
            selected_nodes = []
            
            # Create a list of candidate nodes that have any chance to hold the file.
            candidates = [node for node in range(N) if remaining_capacity[node] >= file_size]
            # Sort candidates based on distance from client.
            candidates = sorted(candidates, key=lambda i: manhattan_distance(client_location, node_locations[i]))
            
            # If there are not enough candidate nodes, then allocation is infeasible.
            if len(candidates) < replication_factor:
                raise ValueError("Not enough capacity to allocate file {} with replication factor {}.".format(file_idx, replication_factor))
            # Otherwise, allocate the first replication_factor nodes.
            for node in candidates[:replication_factor]:
                selected_nodes.append(node)
                remaining_capacity[node] -= file_size
        
        allocation_dict[file_idx] = selected_nodes

    # Reorder the allocations to match the original file order.
    allocation = [allocation_dict[i] for i in range(M)]
    return allocation