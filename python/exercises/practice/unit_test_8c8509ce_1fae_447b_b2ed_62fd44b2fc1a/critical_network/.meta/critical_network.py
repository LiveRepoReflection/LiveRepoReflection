import itertools
import copy
import sys
sys.setrecursionlimit(10000)

def maximize_resilience(n, k, importance, adj_list):
    # Build 0-indexed graph from adj_list (list of sets)
    original_graph = [set() for _ in range(n)]
    for i in range(n):
        for j in adj_list[i]:
            # Convert to 0-indexed
            original_graph[i].add(j - 1)
    # Build candidate redundant links: pairs (u, v) with u < v and edge not present already.
    candidates = []
    for u in range(n):
        for v in range(u+1, n):
            if v not in original_graph[u]:
                candidates.append((u, v))
    # Evaluate resilience for a graph given as list of sets (0-indexed)
    def evaluate_resilience(graph):
        def dfs(node, visited, fail, graph):
            stack = [node]
            comp_sum = 0
            while stack:
                curr = stack.pop()
                if curr in visited:
                    continue
                visited.add(curr)
                comp_sum += importance[curr]
                for nei in graph[curr]:
                    if nei == fail or nei in visited:
                        continue
                    stack.append(nei)
            return comp_sum

        overall = float('inf')
        for fail in range(n):
            visited = set()
            best_comp = 0
            for node in range(n):
                if node == fail or node in visited:
                    continue
                comp_val = dfs(node, visited, fail, graph)
                if comp_val > best_comp:
                    best_comp = comp_val
            overall = min(overall, best_comp)
        return overall

    # Start with no redundant links (empty set)
    best_resilience = evaluate_resilience(original_graph)

    # If no candidates or k == 0, return current resilience.
    if k <= 0 or not candidates:
        return best_resilience

    # For brute force search: try all combinations of candidate edges with 1 to min(k, len(candidates)) edges.
    # Note: In a realistic scenario, this optimization is NP-hard.
    max_edges_to_use = min(k, len(candidates))
    # To avoid heavy computation, if candidate set is large, limit search to combinations of size up to max_edges_to_use.
    # But given unit tests, graphs are small.
    # We consider all combinations of candidate edges of size r for r in 0..max_edges_to_use.
    for r in range(1, max_edges_to_use + 1):
        for extra_edges in itertools.combinations(candidates, r):
            # Create a new graph by copying original and adding extra edges.
            new_graph = [set(neis) for neis in original_graph]
            for (u, v) in extra_edges:
                new_graph[u].add(v)
                new_graph[v].add(u)
            cur_res = evaluate_resilience(new_graph)
            if cur_res > best_resilience:
                best_resilience = cur_res
            # Early exit if we've reached optimal theoretical resilience.
            # The optimal resilience is when the graph is 2-vertex-connected.
            # In that case, for any failure f, the component sum is total sum minus importance[f].
            # So the worst case is total - max(importance)
            opt = sum(importance) - max(importance)
            if best_resilience == opt:
                return best_resilience
    return best_resilience