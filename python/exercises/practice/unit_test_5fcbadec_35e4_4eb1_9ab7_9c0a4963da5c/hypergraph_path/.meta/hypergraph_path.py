from collections import deque

def shortest_hypergraph_path(hypergraph, start_node, target_node):
    if start_node == target_node:
        return 0

    visited_nodes = set()
    visited_hyperedges = set()
    queue = deque()

    # Initialize with start node and path length 0
    queue.append((start_node, 0))
    visited_nodes.add(start_node)

    while queue:
        current_node, path_length = queue.popleft()

        # Explore all hyperedges containing current node
        for hyperedge in hypergraph.get(current_node, []):
            if id(hyperedge) in visited_hyperedges:
                continue

            visited_hyperedges.add(id(hyperedge))

            # Check all nodes in this hyperedge
            for neighbor in hyperedge:
                if neighbor == target_node:
                    return path_length + 1

                if neighbor not in visited_nodes:
                    visited_nodes.add(neighbor)
                    queue.append((neighbor, path_length + 1))

    return -1