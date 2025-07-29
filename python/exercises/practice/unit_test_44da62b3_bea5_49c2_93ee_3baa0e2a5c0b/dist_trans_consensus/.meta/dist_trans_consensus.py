from collections import deque

def process_transaction(tx_id, participants, bandwidth_matrix, capacities, message_size):
    # Determine majority threshold
    n = len(participants)
    majority = (n // 2) + 1

    # Identify functional nodes: capacity > 0
    functional = [node for node in participants if capacities[node - 1] > 0]
    if not functional:
        return {'decision': 'abort', 'leader': None, 'messages_sent': 0}

    # Build graph for functional nodes based on bandwidth > 0 for communication (ignoring self loops)
    graph = {}
    for node in functional:
        graph[node] = []
        # Only consider other functional nodes that are directly connected
        for other in functional:
            if node != other and bandwidth_matrix[node - 1][other - 1] > 0:
                graph[node].append(other)

    # Choose leader: highest computational capacity among functional nodes
    leader = max(functional, key=lambda x: capacities[x - 1])

    # Check connectivity in the graph starting from leader
    visited = set()
    queue = deque()
    queue.append(leader)
    visited.add(leader)
    while queue:
        current = queue.popleft()
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    connectivity_count = len(visited)

    # Determine decision based on connectivity of functional nodes
    if connectivity_count >= majority:
        decision = 'commit'
    else:
        decision = 'abort'

    # Simulate message counts across three phases: leader election, vote collection, commit/abort dissemination.
    # Only functional nodes participate in messaging.
    functional_count = len(functional)
    if functional_count > 0:
        messages_election = functional_count - 1  # other nodes send election messages to leader
        messages_vote = functional_count - 1      # nodes send vote to leader
        messages_commit = functional_count - 1    # leader sends decision to functional nodes
        messages_sent = messages_election + messages_vote + messages_commit
    else:
        messages_sent = 0

    return {'decision': decision, 'leader': leader, 'messages_sent': messages_sent}