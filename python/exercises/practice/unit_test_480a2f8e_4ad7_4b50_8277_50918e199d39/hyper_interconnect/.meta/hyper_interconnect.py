from collections import deque, defaultdict

def route_data(N, hyperedges, requests):
    server_to_hyperedges = defaultdict(list)
    # Build mapping from each server to the indices of hyperedges that contain it,
    # deduplicating servers within each hyperedge.
    for idx, hedge in enumerate(hyperedges):
        unique_servers = set(hedge)
        for server in unique_servers:
            server_to_hyperedges[server].append(idx)

    results = []
    for source, target in requests:
        if source == target:
            results.append(0)
            continue

        # BFS in the bipartite graph: servers and hyperedges.
        # Starting from the source server, each traversal across a hyperedge counts as 1.
        queue = deque()
        queue.append((source, 0))
        visited_servers = [False] * N
        visited_servers[source] = True
        visited_hyperedges = [False] * len(hyperedges)
        found = -1

        while queue:
            current, hops = queue.popleft()
            for hedge_idx in server_to_hyperedges[current]:
                if not visited_hyperedges[hedge_idx]:
                    visited_hyperedges[hedge_idx] = True
                    # Traverse the hyperedge; each jump from the hyperedge to a server counts as one traversal.
                    for neighbor in set(hyperedges[hedge_idx]):
                        if not visited_servers[neighbor]:
                            if neighbor == target:
                                found = hops + 1
                                queue.clear()
                                break
                            visited_servers[neighbor] = True
                            queue.append((neighbor, hops + 1))
                    if found != -1:
                        break
            if found != -1:
                break

        results.append(found if found != -1 else -1)
    return results

if __name__ == '__main__':
    # Example usage
    N = 5
    hyperedges = [[0, 1, 2], [2, 3, 4]]
    requests = [(0, 4), (1, 3), (0, 0)]
    print(route_data(N, hyperedges, requests))