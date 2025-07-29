import heapq
from collections import defaultdict, deque


def validate_transaction(N, graph, latency, timeout, transaction, conflicting_keys=None):
    """
    Validate if a transaction can be successfully committed across a network of databases.
    
    Args:
        N: Number of databases
        graph: Adjacency list representing network topology
        latency: NxN matrix with latency between databases (-1 if no direct connection)
        timeout: Timeout value in milliseconds
        transaction: List of (database_id, key, value) operations
        conflicting_keys: Optional dict {db_id: [keys]} for simulating conflicts
    
    Returns:
        bool: True if transaction can be committed, False otherwise
    """
    # If there are no operations, the transaction is trivially valid
    if not transaction:
        return True
    
    # Preprocess the transaction to find participating databases
    participating_dbs = set(op[0] for op in transaction)
    
    # If only coordinator is involved, no need for 2PC
    if len(participating_dbs) == 1 and 0 in participating_dbs:
        return True
    
    # Compute shortest paths from coordinator to all databases
    shortest_paths = compute_all_shortest_paths(N, graph, latency)
    
    # Check if all participating databases are reachable from coordinator
    for db_id in participating_dbs:
        if db_id != 0 and shortest_paths[0][db_id] == float('inf'):
            return False  # Coordinator can't reach a participating database
    
    # Initialize conflict tracking if not provided
    if conflicting_keys is None:
        conflicting_keys = defaultdict(list)
    
    # Extract keys by database for checking conflicts
    db_keys = defaultdict(list)
    for db_id, key, _ in transaction:
        db_keys[db_id].append(key)
    
    # Check for conflicts
    for db_id, keys in db_keys.items():
        for key in keys:
            if key in conflicting_keys.get(db_id, []):
                return False  # Conflict detected
    
    # Simulate Two-Phase Commit protocol
    # Phase 1: Send prepare messages and collect responses
    prepare_phase_success = simulate_prepare_phase(N, participating_dbs, shortest_paths, timeout, conflicting_keys, db_keys)
    
    if not prepare_phase_success:
        return False  # Abort if any database voted "no" or timed out
    
    # Phase 2: Send commit messages
    commit_phase_success = simulate_commit_phase(N, participating_dbs, shortest_paths, timeout)
    
    return commit_phase_success


def compute_all_shortest_paths(N, graph, latency):
    """
    Computes shortest paths from each database to all other databases using Dijkstra's algorithm.
    
    Returns:
        dict: Dictionary mapping (source, target) to shortest distance
    """
    shortest_paths = [[float('inf')] * N for _ in range(N)]
    
    for src in range(N):
        # Use Dijkstra's algorithm for each source node
        shortest_paths[src][src] = 0
        pq = [(0, src)]  # (distance, vertex)
        visited = set()
        
        while pq:
            dist, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)
            
            for v in graph[u]:
                if latency[u][v] != -1 and v not in visited:
                    new_dist = dist + latency[u][v]
                    if new_dist < shortest_paths[src][v]:
                        shortest_paths[src][v] = new_dist
                        heapq.heappush(pq, (new_dist, v))
    
    return shortest_paths


def simulate_prepare_phase(N, participating_dbs, shortest_paths, timeout, conflicting_keys, db_keys):
    """
    Simulates the prepare phase of 2PC.
    
    Returns:
        bool: True if all databases voted "yes", False otherwise
    """
    # Track the response time for each database
    responses = {}
    
    for db_id in participating_dbs:
        if db_id == 0:  # Coordinator
            continue
        
        # Calculate round trip time: coordinator to db and back
        round_trip_time = shortest_paths[0][db_id] + shortest_paths[db_id][0]
        
        # Check if round trip exceeds timeout
        if round_trip_time > timeout:
            return False  # Database will time out
        
        # Check for conflicts
        has_conflict = any(key in conflicting_keys.get(db_id, []) for key in db_keys[db_id])
        if has_conflict:
            return False  # Database votes "no" due to conflict
        
        # Record successful response
        responses[db_id] = "yes"
    
    # All databases responded with "yes"
    return len(responses) == len(participating_dbs) - (1 if 0 in participating_dbs else 0)


def simulate_commit_phase(N, participating_dbs, shortest_paths, timeout):
    """
    Simulates the commit phase of 2PC.
    
    Returns:
        bool: True if all databases successfully commit, False otherwise
    """
    # For each participating database, check if commit message can arrive within timeout
    for db_id in participating_dbs:
        if db_id == 0:  # Coordinator
            continue
        
        # Time for commit message to reach from coordinator to database
        commit_time = shortest_paths[0][db_id]
        
        if commit_time > timeout:
            return False  # Database will time out before receiving commit
    
    # All databases received commit message within timeout
    return True