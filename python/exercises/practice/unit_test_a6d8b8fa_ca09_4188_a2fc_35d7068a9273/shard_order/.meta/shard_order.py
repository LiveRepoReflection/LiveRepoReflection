from collections import deque, defaultdict

def schedule_transactions(transactions, N):
    # If no transactions, return empty list for each shard.
    if not transactions:
        return {shard: [] for shard in range(N)}
    
    # Build a dictionary mapping transaction id to transaction details.
    trans_map = {t["id"]: t for t in transactions}
    
    # Build the dependency graph and indegree dictionary.
    graph = defaultdict(list)
    indegree = {t["id"]: 0 for t in transactions}
    
    for t in transactions:
        for dep in t["dependencies"]:
            # Note: we assume all dependencies appear in transactions.
            # If a dependency is missing, we can either ignore or treat it as an error.
            if dep in trans_map:
                graph[dep].append(t["id"])
                indegree[t["id"]] += 1
    
    # Kahn's algorithm for topological sorting.
    queue = deque([tid for tid in indegree if indegree[tid] == 0])
    sorted_order = []
    
    while queue:
        current = queue.popleft()
        sorted_order.append(current)
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    
    # If sorted_order doesn't include all transactions, a cycle exists.
    if len(sorted_order) != len(transactions):
        return None
    
    # Build the per-shard schedule.
    shard_schedule = {shard: [] for shard in range(N)}
    for tid in sorted_order:
        t = trans_map[tid]
        for shard in t["shards"]:
            if 0 <= shard < N:
                shard_schedule[shard].append(tid)
    
    return shard_schedule