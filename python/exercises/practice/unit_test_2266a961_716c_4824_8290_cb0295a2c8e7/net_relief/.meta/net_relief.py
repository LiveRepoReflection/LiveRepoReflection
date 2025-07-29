from collections import deque

def mitigate_congestion(graph, affected_servers, congestion_threshold, communication_matrix, weights):
    # changes dictionary: key = (u, v), value = net change (positive means increased utilization)
    changes = {}

    # Helper function to get current adjusted utilization for an edge.
    def adjusted_util(u, v):
        return graph[u][v]["utilization"] + changes.get((u, v), 0)

    # Standard BFS to find a shortest path from src to dst.
    # The filter_func, if provided, takes arguments (u, v, weight) and returns True if the edge can be used.
    def bfs_path(src, dst, traffic, filter_func=None):
        queue = deque([src])
        parent = {src: None}
        while queue:
            curr = queue.popleft()
            if curr == dst:
                # Reconstruct the path as a list of nodes, then convert to list of edges.
                path_nodes = []
                while curr is not None:
                    path_nodes.append(curr)
                    curr = parent[curr]
                path_nodes.reverse()
                # Create list of edges
                path_edges = []
                for i in range(len(path_nodes)-1):
                    path_edges.append((path_nodes[i], path_nodes[i+1]))
                return path_edges
            for neighbor in graph.get(curr, {}):
                # If already visited, skip.
                if neighbor in parent:
                    continue
                # if filter_func is provided, check condition on the edge
                if filter_func is not None:
                    cap = graph[curr][neighbor]["capacity"]
                    # Check if adding traffic would keep the edge below the congestion threshold
                    if adjusted_util(curr, neighbor) + traffic > congestion_threshold * cap:
                        continue
                parent[neighbor] = curr
                queue.append(neighbor)
        return None

    # Function to determine if a given edge is congested.
    def is_congested(u, v):
        cap = graph[u][v]["capacity"]
        return adjusted_util(u, v) > congestion_threshold * cap

    # Process each communication pair if the source is in the affected_servers and destination is required.
    for (src, dst), traffic in weights.items():
        if src not in affected_servers:
            continue
        # Check communication_matrix: only process if dst is in communication targets for src.
        if src not in communication_matrix or dst not in communication_matrix[src]:
            continue
        # If source equals destination, no rerouting is needed.
        if src == dst:
            continue

        # Find the baseline route (shortest path ignoring congestion filtering).
        baseline_route = bfs_path(src, dst, traffic, filter_func=None)
        if baseline_route is None:
            continue

        # Check if baseline route contains at least one congested edge.
        baseline_congested = any(is_congested(u, v) for u, v in baseline_route)
        if not baseline_congested:
            # If the baseline route is not congested, no rerouting is required.
            continue

        # Try to find an alternative route that avoids congested edges.
        alternative_route = bfs_path(src, dst, traffic, filter_func=lambda u, v, t=traffic: (adjusted_util(u, v) + t) <= congestion_threshold * graph[u][v]["capacity"])
        
        # If a valid alternative route exists and is different from baseline, perform rerouting.
        if alternative_route is not None and alternative_route != baseline_route:
            # Subtract traffic from edges on the original baseline route.
            for edge in baseline_route:
                changes[edge] = changes.get(edge, 0) - traffic
            # Add traffic to edges on the alternative route.
            for edge in alternative_route:
                changes[edge] = changes.get(edge, 0) + traffic
        # If no suitable alternative route is found, do not reroute this communication.
        # The traffic remains on the original route.
    return changes