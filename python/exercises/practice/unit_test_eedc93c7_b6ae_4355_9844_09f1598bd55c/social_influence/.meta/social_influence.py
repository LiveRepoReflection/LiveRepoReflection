import random
from collections import defaultdict, deque

def select_seed_users(edges, k, iterations):
    # Build the directed graph and the set of nodes.
    graph = defaultdict(list)
    nodes = set()
    for u, v, w in edges:
        graph[u].append((v, w))
        nodes.add(u)
        nodes.add(v)
    nodes = list(nodes)
    
    # If k is greater than or equal to the number of nodes, return all nodes.
    if k >= len(nodes):
        return nodes

    # Define a simulation function for influence spread.
    def simulate(seed_set):
        activated = set(seed_set)
        queue = deque(seed_set)
        while queue:
            current = queue.popleft()
            for neighbor, weight in graph.get(current, []):
                if neighbor not in activated and random.random() < weight:
                    activated.add(neighbor)
                    queue.append(neighbor)
        return len(activated)
    
    # Greedy algorithm to select seed nodes.
    seed_set = set()
    for _ in range(k):
        best_candidate = None
        best_increase = -1
        # Try adding each candidate node to the current seed set
        for candidate in nodes:
            if candidate in seed_set:
                continue
            current_seed = list(seed_set.union({candidate}))
            total_spread = 0
            for _ in range(iterations):
                total_spread += simulate(current_seed)
            avg_spread = total_spread / iterations
            if avg_spread > best_increase:
                best_increase = avg_spread
                best_candidate = candidate
        seed_set.add(best_candidate)
    return list(seed_set)