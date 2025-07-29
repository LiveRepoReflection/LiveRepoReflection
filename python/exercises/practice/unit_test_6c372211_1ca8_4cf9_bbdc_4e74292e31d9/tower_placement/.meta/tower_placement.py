from collections import deque
import itertools
import random

def optimal_tower_placement(graph, location_data, revenue_per_person, interference_distance, interference_penalty):
    # Precompute revenue and profit for each node
    nodes = list(graph.keys())
    revenue = {}
    profit_no_int = {}
    profit_with_int = {}
    for node in nodes:
        pop = location_data[node]['population']
        cost = location_data[node]['cost']
        rev = pop * revenue_per_person
        revenue[node] = rev
        profit_no_int[node] = rev - cost
        profit_with_int[node] = rev * (1 - interference_penalty) - cost

    # Precompute interference sets for each node (nodes within interference_distance, excluding self)
    interference = {}
    for node in nodes:
        visited = set()
        q = deque()
        q.append((node, 0))
        visited.add(node)
        interference[node] = set()
        while q:
            current, dist = q.popleft()
            if dist > 0:
                interference[node].add(current)
            if dist < interference_distance:
                for nei in graph.get(current, []):
                    if nei not in visited:
                        visited.add(nei)
                        q.append((nei, dist+1))
    # Objective function: Given a placement S, compute total profit, where each node in S:
    # if S intersects interference[node] is empty then profit_no_int, else profit_with_int.
    def evaluate(S):
        total = 0
        for node in S:
            # Check if any interfering tower exists in S
            if S & interference[node]:
                total += profit_with_int[node]
            else:
                total += profit_no_int[node]
        return total

    n = len(nodes)
    # If the graph is small, use brute force to get optimal solution
    if n <= 20:
        best_profit = float('-inf')
        best_solution = set()
        # Iterate over all subsets
        for r in range(n + 1):
            for combo in itertools.combinations(nodes, r):
                candidate = set(combo)
                current_profit = evaluate(candidate)
                if current_profit > best_profit:
                    best_profit = current_profit
                    best_solution = candidate
        return best_solution

    # For larger graphs, use local search greedy improvement
    # Initialize with a greedy solution: add nodes in order of descending profit_no_int if marginal gain is positive.
    current_S = set()
    for node in sorted(nodes, key=lambda x: profit_no_int[x], reverse=True):
        # Calculate marginal benefit if we add node
        new_S = current_S | {node}
        if evaluate(new_S) > evaluate(current_S):
            current_S = new_S

    # Local search: try flipping each node (either add or remove) if it improves the objective.
    improved = True
    iteration = 0
    while improved and iteration < 10000:
        improved = False
        iteration += 1
        for node in nodes:
            if node in current_S:
                candidate = current_S - {node}
            else:
                candidate = current_S | {node}
            if evaluate(candidate) > evaluate(current_S):
                current_S = candidate
                improved = True
        # Optionally, include random perturbations to escape local optima.
        if not improved:
            node = random.choice(nodes)
            if node in current_S:
                candidate = current_S - {node}
            else:
                candidate = current_S | {node}
            if evaluate(candidate) > evaluate(current_S):
                current_S = candidate
                improved = True

    return current_S