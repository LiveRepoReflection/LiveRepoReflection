from collections import deque

def analyze_network(shards, queries):
    # Build the global graph and a set of all users.
    global_graph = {}
    global_users = set()
    
    # Collect all users
    for shard in shards:
        global_users.update(shard["users"])
    
    # Initialize graph nodes
    for user in global_users:
        global_graph[user] = set()
    
    # Add all connections from shards
    for shard in shards:
        for user_from, user_to in shard["connections"]:
            # Add edge if both users belong to the global user set
            if user_from in global_users and user_to in global_users:
                global_graph[user_from].add(user_to)
    
    results = []
    
    # Helper function for BFS between two users
    def bfs_reachability(start, target, max_hops):
        if start == target:
            return True
        visited = set([start])
        queue = deque([(start, 0)])
        while queue:
            current, hops = queue.popleft()
            if hops >= max_hops:
                continue
            for neighbor in global_graph.get(current, set()):
                if neighbor not in visited:
                    if neighbor == target:
                        return True
                    visited.add(neighbor)
                    queue.append((neighbor, hops + 1))
        return False
    
    # Helper function for BFS to compute influencer score (number of nodes reachable within hop_limit)
    def bfs_influencer(start, hop_limit):
        visited = set([start])
        queue = deque([(start, 0)])
        count = 0
        while queue:
            current, hops = queue.popleft()
            if hops == hop_limit:
                continue
            for neighbor in global_graph.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    count += 1
                    queue.append((neighbor, hops + 1))
        return count

    for query in queries:
        if query["type"] == "reachability":
            user_a = query["user_a"]
            user_b = query["user_b"]
            max_hops = query["max_hops"]
            if user_a not in global_users or user_b not in global_users:
                results.append(False)
            else:
                results.append(bfs_reachability(user_a, user_b, max_hops))
        elif query["type"] == "influencer_score":
            user = query["user"]
            hop_limit = query["hop_limit"]
            if user not in global_users:
                results.append(0)
            else:
                results.append(bfs_influencer(user, hop_limit))
        else:
            # For unknown query types, default to None (or could raise an error)
            results.append(None)
    
    return results