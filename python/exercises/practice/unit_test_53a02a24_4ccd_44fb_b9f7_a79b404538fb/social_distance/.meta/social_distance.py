def analyze_network(start_uid, target_uids, Q, get_connections):
    if start_uid in target_uids:
        return 0

    query_count = 0
    from collections import deque
    queue = deque([(start_uid, 0)])
    visited = {start_uid}

    while queue and query_count < Q:
        current_uid, distance = queue.popleft()
        if query_count >= Q:
            break
        connections = get_connections(current_uid)
        query_count += 1
        for neighbor in connections:
            if neighbor not in visited:
                if neighbor in target_uids:
                    return distance + 1
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))
    return -1