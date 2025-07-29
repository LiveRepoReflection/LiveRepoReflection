import heapq
from collections import defaultdict

def minimum_migration_cost(N, M, T, ownership, size, bandwidth):
    """
    Calculate the minimum cost to migrate all data blocks to the target datacenter.
    
    Args:
        N: Number of datacenters
        M: Number of data blocks
        T: Target datacenter index
        ownership: Matrix indicating which datacenters own which blocks
        size: Array of block sizes
        bandwidth: Matrix of bandwidths between datacenters
    
    Returns:
        Minimum total cost (in seconds) to migrate all blocks to the target datacenter
    """
    # Preprocess: Find which datacenters have each block
    block_owners = [[] for _ in range(M)]
    for i in range(N):
        for j in range(M):
            if ownership[i][j]:
                block_owners[j].append(i)
    
    # If target datacenter already has all blocks, cost is 0
    if all(T in owners for owners in block_owners):
        return 0.0
    
    total_cost = 0.0
    
    # For each block, find the cheapest way to move it to the target
    for block_idx in range(M):
        # Skip if target already has this block
        if T in block_owners[block_idx]:
            continue
        
        block_size = size[block_idx]
        
        # Use Dijkstra's algorithm to find the shortest path from any datacenter 
        # that has the block to the target datacenter
        
        # Priority queue to track the best paths
        pq = []
        # Map to track visited nodes
        visited = set()
        # Track the best cost to each datacenter
        costs = [float('inf')] * N
        
        # Initialize with all datacenters that have the block
        for owner in block_owners[block_idx]:
            heapq.heappush(pq, (0, owner))  # (cost, datacenter_idx)
            costs[owner] = 0
        
        # Dijkstra's algorithm to find the cheapest path to target
        while pq:
            cost, current = heapq.heappop(pq)
            
            if current == T:
                # We've found the target datacenter
                total_cost += cost
                break
                
            if current in visited:
                continue
                
            visited.add(current)
            
            # Try transferring the block to each neighbor
            for next_dc in range(N):
                if next_dc != current and bandwidth[current][next_dc] > 0:
                    transfer_cost = block_size / bandwidth[current][next_dc]
                    new_cost = cost + transfer_cost
                    
                    if new_cost < costs[next_dc]:
                        costs[next_dc] = new_cost
                        heapq.heappush(pq, (new_cost, next_dc))
    
    return total_cost

def floyd_warshall_migration_cost(N, M, T, ownership, size, bandwidth):
    """
    Alternative approach using Floyd-Warshall algorithm to pre-compute all shortest paths.
    This can be more efficient for dense graphs with multiple blocks to transfer.
    """
    # Calculate the cost matrix between all pairs of datacenters
    cost_matrix = [[float('inf')] * N for _ in range(N)]
    
    # Initialize direct costs
    for i in range(N):
        cost_matrix[i][i] = 0
        for j in range(N):
            if i != j and bandwidth[i][j] > 0:
                cost_matrix[i][j] = 1 / bandwidth[i][j]  # Cost per GB
    
    # Floyd-Warshall algorithm to find all-pairs shortest paths
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if cost_matrix[i][j] > cost_matrix[i][k] + cost_matrix[k][j]:
                    cost_matrix[i][j] = cost_matrix[i][k] + cost_matrix[k][j]
    
    total_cost = 0.0
    
    # For each block, find the cheapest way to transfer it to the target
    for block_idx in range(M):
        block_size = size[block_idx]
        min_cost = float('inf')
        
        # If target already has the block, cost is 0
        if ownership[T][block_idx]:
            continue
        
        # Find the datacenter with the block that has the cheapest path to target
        for source in range(N):
            if ownership[source][block_idx]:
                cost = block_size * cost_matrix[source][T]
                min_cost = min(min_cost, cost)
        
        total_cost += min_cost
    
    return total_cost

def network_flow_migration_cost(N, M, T, ownership, size, bandwidth):
    """
    Another approach using min-cost flow concepts to optimize data movement.
    This is particularly useful when multiple paths could be used together.
    
    Note: This is a simpler approximation; a full min-cost flow algorithm would be more complex.
    """
    # First, create a graph that represents the network with transfer costs
    graph = defaultdict(list)
    
    # For each pair of datacenters, add an edge with bandwidth as capacity
    for i in range(N):
        for j in range(N):
            if i != j and bandwidth[i][j] > 0:
                # Edge represents (destination, cost_per_unit, bandwidth)
                graph[i].append((j, 1.0 / bandwidth[i][j], bandwidth[i][j]))
    
    total_cost = 0.0
    
    # For each block, find the cheapest path(s) to transfer it
    for block_idx in range(M):
        block_size = size[block_idx]
        
        # If target already has the block, no transfer needed
        if ownership[T][block_idx]:
            continue
        
        # Use Dijkstra's algorithm to find the cheapest path from any source to target
        pq = []
        visited = set()
        distances = [float('inf')] * N
        
        # Initialize with all datacenters that have the block
        for source in range(N):
            if ownership[source][block_idx]:
                heapq.heappush(pq, (0, source))
                distances[source] = 0
        
        # Dijkstra's algorithm
        while pq and T not in visited:
            cost, current = heapq.heappop(pq)
            
            if current in visited:
                continue
                
            visited.add(current)
            
            for next_dc, cost_per_unit, _ in graph[current]:
                new_cost = cost + cost_per_unit * block_size
                
                if new_cost < distances[next_dc]:
                    distances[next_dc] = new_cost
                    heapq.heappush(pq, (new_cost, next_dc))
        
        # Add the cost of transferring this block to the total
        total_cost += distances[T]
    
    return total_cost

# Use the most efficient algorithm based on the problem constraints
def optimal_migration_cost(N, M, T, ownership, size, bandwidth):
    """
    Choose the most appropriate algorithm based on problem characteristics.
    """
    if N <= 10:  # For small networks, Floyd-Warshall might be more efficient
        return floyd_warshall_migration_cost(N, M, T, ownership, size, bandwidth)
    else:  # For larger networks, use Dijkstra's for each block
        return minimum_migration_cost(N, M, T, ownership, size, bandwidth)

# Default to using the primary implementation
def minimum_migration_cost(N, M, T, ownership, size, bandwidth):
    # Calculate the cost matrix - cost[i][j] = cost to transfer 1GB from i to j
    cost_matrix = [[float('inf')] * N for _ in range(N)]
    
    # Initialize direct costs
    for i in range(N):
        cost_matrix[i][i] = 0
        for j in range(N):
            if i != j and bandwidth[i][j] > 0:
                cost_matrix[i][j] = 1 / bandwidth[i][j]  # Cost per GB
    
    # Floyd-Warshall algorithm to find all-pairs shortest paths
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if cost_matrix[i][j] > cost_matrix[i][k] + cost_matrix[k][j]:
                    cost_matrix[i][j] = cost_matrix[i][k] + cost_matrix[k][j]
    
    total_cost = 0.0
    
    # For each block, find the minimum cost to transfer it to the target
    for block_idx in range(M):
        block_size = size[block_idx]
        min_cost = float('inf')
        
        # If target already has the block, cost is 0
        if ownership[T][block_idx]:
            continue
        
        # Find the datacenter with the block that has the cheapest path to target
        for source in range(N):
            if ownership[source][block_idx]:
                cost = block_size * cost_matrix[source][T]
                min_cost = min(min_cost, cost)
        
        total_cost += min_cost
    
    return total_cost