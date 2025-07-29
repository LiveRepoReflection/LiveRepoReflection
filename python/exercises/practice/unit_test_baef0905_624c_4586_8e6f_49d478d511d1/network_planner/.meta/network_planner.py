import itertools
from collections import defaultdict

def optimal_network_plan(N, M, links, L, B):
    if N == 0 or M == 0:
        return []

    # Generate all possible subsets of links that are within budget
    possible_networks = []
    for k in range(N-1, min(M, N*(N-1)//2) + 1):
        for subset in itertools.combinations(links, k):
            total_cost = sum(link[2] for link in subset)
            if total_cost <= B:
                possible_networks.append(subset)

    valid_networks = []
    for network in possible_networks:
        if is_network_valid(N, network, L):
            valid_networks.append(network)

    if not valid_networks:
        return []

    # Find the network with minimum average latency
    best_network = min(valid_networks, key=lambda net: calculate_average_latency(N, net))
    return list(best_network)

def is_network_valid(N, network, max_latency):
    # Build adjacency list
    adj = defaultdict(list)
    for u, v, _, lat in network:
        adj[u].append((v, lat))
        adj[v].append((u, lat))

    # Check connectivity and latency constraints
    for i in range(N):
        distances = {node: float('inf') for node in range(N)}
        distances[i] = 0
        visited = set()

        while len(visited) < N:
            current = min(
                (node for node in range(N) if node not in visited),
                key=lambda x: distances[x]
            )
            visited.add(current)

            for neighbor, lat in adj[current]:
                if neighbor not in visited:
                    new_dist = distances[current] + lat
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist

        for j in range(N):
            if i != j and (distances[j] == float('inf') or distances[j] > max_latency):
                return False

    return True

def calculate_average_latency(N, network):
    if not network:
        return float('inf')

    # Build adjacency list
    adj = defaultdict(list)
    for u, v, _, lat in network:
        adj[u].append((v, lat))
        adj[v].append((u, lat))

    total_latency = 0
    pair_count = 0

    for i in range(N):
        distances = {node: float('inf') for node in range(N)}
        distances[i] = 0
        visited = set()

        while len(visited) < N:
            current = min(
                (node for node in range(N) if node not in visited),
                key=lambda x: distances[x]
            )
            visited.add(current)

            for neighbor, lat in adj[current]:
                if neighbor not in visited:
                    new_dist = distances[current] + lat
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist

        for j in range(i+1, N):
            if distances[j] != float('inf'):
                total_latency += distances[j]
                pair_count += 1

    return total_latency / pair_count if pair_count > 0 else float('inf')