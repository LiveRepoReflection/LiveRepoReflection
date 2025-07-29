from collections import deque

def calculate_influence_score(user_id, N, get_connections):
    visited = {user_id: 0}
    queue = deque([user_id])
    
    while queue:
        current = queue.popleft()
        # Get connections for the current user and remove duplicate entries by converting to set.
        neighbors = set(get_connections(current))
        # Remove self-loops.
        if current in neighbors:
            neighbors.remove(current)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited[neighbor] = visited[current] + 1
                queue.append(neighbor)
    
    influence = 0.0
    for node, depth in visited.items():
        if node == user_id:
            continue
        influence += 1 / (depth + 1)
    return influence