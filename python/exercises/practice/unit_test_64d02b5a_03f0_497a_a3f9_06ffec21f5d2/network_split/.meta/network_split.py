def split_network(N, edges, C, D, M):
    # Build graph as an adjacency list for quick neighbor lookup
    graph = {i: set() for i in range(N)}
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

    # Each node starts as its own partition.
    partitions = {}
    # Map each node to its partition id.
    node_to_partition = {}
    for i in range(N):
        partitions[i] = {
            "nodes": {i},
            "internal": 0,  # No internal edges in a singleton.
            "criticals": 1 if i in C else 0
        }
        node_to_partition[i] = i

    # Helper function to compute number of edges connecting two sets
    def count_cross_edges(nodes_a, nodes_b):
        count = 0
        for node in nodes_a:
            # Intersection of neighbors with nodes_b
            count += len(graph[node].intersection(nodes_b))
        return count

    # Greedy merging process: attempt to merge partitions using available edges.
    merged = True
    while merged:
        merged = False
        # Iterate over each edge to find a pair of partitions that can merge.
        for u, v in edges:
            pid_u = node_to_partition[u]
            pid_v = node_to_partition[v]
            if pid_u == pid_v:
                continue

            part1 = partitions[pid_u]
            part2 = partitions[pid_v]
            new_size = len(part1["nodes"]) + len(part2["nodes"])
            if new_size > M:
                continue

            # Count edges between these two partitions.
            cross_edges = count_cross_edges(part1["nodes"], part2["nodes"])
            new_internal = part1["internal"] + part2["internal"] + cross_edges
            if new_size > 1:
                max_possible = new_size * (new_size - 1) / 2
            else:
                max_possible = 1
            new_density = new_internal / max_possible

            if new_density < D:
                continue

            # Heuristic: avoid merging partitions if both contain at least one critical router.
            if part1["criticals"] > 0 and part2["criticals"] > 0:
                continue

            # Merge partitions: choose pid_u as the merged partition id.
            new_nodes = part1["nodes"].union(part2["nodes"])
            new_criticals = part1["criticals"] + part2["criticals"]

            # Update partition with merged result.
            partitions[pid_u] = {
                "nodes": new_nodes,
                "internal": new_internal,
                "criticals": new_criticals
            }
            # Update node_to_partition for nodes in part2.
            for node in part2["nodes"]:
                node_to_partition[node] = pid_u

            # Remove the merged partition.
            del partitions[pid_v]

            merged = True
            # Restart the scanning of edges from scratch.
            break

    # After greedy merging, partitions is a dict mapping id to partition info.
    # Validate that each partition meets the density and size constraints.
    result = []
    for part in partitions.values():
        size = len(part["nodes"])
        if size > M:
            return []
        if size > 1:
            max_possible = size * (size - 1) / 2
            density = part["internal"] / max_possible
        else:
            density = 1.0  # A single node is considered maximally dense.
        if density < D:
            return []
        result.append(part["nodes"])
    return result

if __name__ == "__main__":
    # Example usage:
    # N = 6, edges = [(0, 1), (0, 2), (1, 2), (3, 4), (4, 5)], C = {0, 3, 5}, D = 0.4, M = 4
    N = 6
    edges = [(0, 1), (0, 2), (1, 2), (3, 4), (4, 5)]
    C = {0, 3, 5}
    D = 0.4
    M = 4
    partitions = split_network(N, edges, C, D, M)
    print("Partitions:", partitions)