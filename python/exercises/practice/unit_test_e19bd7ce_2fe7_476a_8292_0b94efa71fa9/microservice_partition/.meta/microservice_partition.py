import heapq
from collections import defaultdict, deque

def partition_microservices(N, C, R, K, dependencies):
    """
    Partitions microservices into clusters to minimize inter-cluster communication.
    
    Args:
        N: Number of microservices
        C: Communication matrix where C[i][j] is the cost between microservice i and j
        R: Resource requirements for each microservice
        K: Maximum capacity of each cluster
        dependencies: List of tuples (a, b) where a depends on b
    
    Returns:
        A list of sets, where each set contains the microservices in a cluster,
        or None if no valid partitioning is possible.
    """
    # Check if any microservice exceeds the cluster capacity
    if max(R) > K:
        return None
    
    # Calculate the communication score between each pair of services
    # Higher score = more important to keep together
    edge_scores = []
    for i in range(N):
        for j in range(i+1, N):
            # Base score is the sum of bidirectional communication costs
            score = C[i][j] + C[j][i]
            
            # Add bonus for dependencies
            if (i, j) in dependencies or (j, i) in dependencies:
                score += 100  # Bonus for direct dependencies
            
            if score > 0:
                edge_scores.append((-score, i, j))  # Negative score for max-heap
    
    # Sort edges by score in descending order (max-heap)
    heapq.heapify(edge_scores)
    
    # Create a graph representation for Union-Find
    parent = list(range(N))
    rank = [0] * N
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        root_x = find(x)
        root_y = find(y)
        if root_x == root_y:
            return
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        else:
            parent[root_y] = root_x
            if rank[root_x] == rank[root_y]:
                rank[root_x] += 1
    
    # Track cluster resources
    cluster_resources = defaultdict(int)
    for i in range(N):
        cluster_resources[i] = R[i]
    
    # Process edges in order of descending score
    while edge_scores:
        _, i, j = heapq.heappop(edge_scores)
        
        root_i = find(i)
        root_j = find(j)
        
        if root_i != root_j:
            # Check if merging would exceed capacity
            if cluster_resources[root_i] + cluster_resources[root_j] <= K:
                union(root_i, root_j)
                cluster_resources[find(root_i)] = cluster_resources[root_i] + cluster_resources[root_j]
                # Since one cluster is now part of another, remove its separate resource tracking
                if find(root_j) != root_j:
                    del cluster_resources[root_j]
    
    # Build the final clusters
    clusters = defaultdict(set)
    for i in range(N):
        clusters[find(i)].add(i)
    
    return list(clusters.values())

def partition_microservices_simulated_annealing(N, C, R, K, dependencies):
    """
    Alternative implementation using simulated annealing.
    This can be used for larger problems or when the greedy approach doesn't produce optimal results.
    
    Args:
        N: Number of microservices
        C: Communication matrix where C[i][j] is the cost between microservice i and j
        R: Resource requirements for each microservice
        K: Maximum capacity of each cluster
        dependencies: List of tuples (a, b) where a depends on b
    
    Returns:
        A list of sets, where each set contains the microservices in a cluster,
        or None if no valid partitioning is possible.
    """
    import random
    import math
    
    # Check if any microservice exceeds the cluster capacity
    if max(R) > K:
        return None
    
    # Create dependency graph for quick lookup
    dependency_graph = defaultdict(set)
    for a, b in dependencies:
        dependency_graph[a].add(b)
        dependency_graph[b].add(a)
    
    # Initialize with each microservice in its own cluster
    current_solution = [{i} for i in range(N)]
    
    # Calculate the cost of a solution (lower is better)
    def solution_cost(solution):
        inter_cluster_cost = 0
        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                
                # Find clusters for i and j
                cluster_i = next(cluster for cluster in solution if i in cluster)
                cluster_j = next(cluster for cluster in solution if j in cluster)
                
                if cluster_i != cluster_j:
                    inter_cluster_cost += C[i][j]
        
        # Add penalty for separated dependencies
        dependency_penalty = 0
        for a, b in dependencies:
            cluster_a = next(cluster for cluster in solution if a in cluster)
            cluster_b = next(cluster for cluster in solution if b in cluster)
            if cluster_a != cluster_b:
                dependency_penalty += 50  # Penalty for separated dependencies
        
        return inter_cluster_cost + dependency_penalty
    
    # Check if a solution is valid (respects capacity)
    def is_valid_solution(solution):
        for cluster in solution:
            if sum(R[i] for i in cluster) > K:
                return False
        return True
    
    # Initialize variables for simulated annealing
    current_cost = solution_cost(current_solution)
    best_solution = current_solution.copy()
    best_cost = current_cost
    
    # Simulated annealing parameters
    temperature = 1000.0
    cooling_rate = 0.995
    iterations = 10000
    
    for iteration in range(iterations):
        # Create a neighbor solution by randomly moving a microservice
        neighbor_solution = [cluster.copy() for cluster in current_solution]
        
        # Randomly choose a microservice to move
        while True:
            source_cluster_idx = random.randint(0, len(neighbor_solution) - 1)
            if len(neighbor_solution[source_cluster_idx]) > 0:
                break
        
        service_to_move = random.choice(list(neighbor_solution[source_cluster_idx]))
        
        # Choose action: move to existing cluster or create new one
        if len(neighbor_solution) > 1 and random.random() < 0.8:
            # Move to another existing cluster
            target_cluster_idx = source_cluster_idx
            while target_cluster_idx == source_cluster_idx:
                target_cluster_idx = random.randint(0, len(neighbor_solution) - 1)
            
            # Move the service
            neighbor_solution[source_cluster_idx].remove(service_to_move)
            neighbor_solution[target_cluster_idx].add(service_to_move)
            
            # Remove empty clusters
            if len(neighbor_solution[source_cluster_idx]) == 0:
                del neighbor_solution[source_cluster_idx]
        else:
            # Create a new cluster
            neighbor_solution[source_cluster_idx].remove(service_to_move)
            neighbor_solution.append({service_to_move})
            
            # Remove empty clusters
            if len(neighbor_solution[source_cluster_idx]) == 0:
                del neighbor_solution[source_cluster_idx]
        
        # Check if the neighbor solution is valid
        if is_valid_solution(neighbor_solution):
            # Calculate new cost
            neighbor_cost = solution_cost(neighbor_solution)
            
            # Decide whether to accept the new solution
            if neighbor_cost < current_cost:
                current_solution = neighbor_solution
                current_cost = neighbor_cost
                
                # Update best solution if needed
                if current_cost < best_cost:
                    best_solution = [cluster.copy() for cluster in current_solution]
                    best_cost = current_cost
            else:
                # Accept worse solution with a probability that decreases with temperature
                probability = math.exp((current_cost - neighbor_cost) / temperature)
                if random.random() < probability:
                    current_solution = neighbor_solution
                    current_cost = neighbor_cost
        
        # Cool down the temperature
        temperature *= cooling_rate
    
    return best_solution

def partition_microservices_with_refinement(N, C, R, K, dependencies):
    """
    A combined approach that starts with the greedy method and refines with local search.
    
    Args:
        N: Number of microservices
        C: Communication matrix where C[i][j] is the cost between microservice i and j
        R: Resource requirements for each microservice
        K: Maximum capacity of each cluster
        dependencies: List of tuples (a, b) where a depends on b
    
    Returns:
        A list of sets, where each set contains the microservices in a cluster,
        or None if no valid partitioning is possible.
    """
    # Try the greedy approach first
    greedy_solution = partition_microservices(N, C, R, K, dependencies)
    
    if greedy_solution is None:
        return None
    
    # For small problems, return the greedy solution directly
    if N <= 20:
        return greedy_solution
    
    # For larger problems, try the simulated annealing approach
    simulated_annealing_solution = partition_microservices_simulated_annealing(N, C, R, K, dependencies)
    
    # Choose the better solution
    def total_cost(solution):
        total = 0
        for i in range(N):
            for j in range(N):
                if i != j:
                    cluster_i = next(cluster for cluster in solution if i in cluster)
                    cluster_j = next(cluster for cluster in solution if j in cluster)
                    if cluster_i != cluster_j:
                        total += C[i][j]
        return total
    
    greedy_cost = total_cost(greedy_solution)
    annealing_cost = total_cost(simulated_annealing_solution)
    
    return simulated_annealing_solution if annealing_cost < greedy_cost else greedy_solution