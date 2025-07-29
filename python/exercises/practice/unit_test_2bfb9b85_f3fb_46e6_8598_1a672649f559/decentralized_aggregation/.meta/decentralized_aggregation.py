import numpy as np
from typing import List, Set
from collections import defaultdict

def validate_inputs(updates: List[List[float]], graph: List[List[int]], f: int, rounds: int, k: int) -> None:
    """Validate input parameters."""
    n = len(updates)
    
    # Validate Byzantine parameter
    if f >= n/2:
        raise ValueError("Number of Byzantine clients must be less than n/2")
    
    # Validate k parameter
    if k > n:
        raise ValueError("k must be less than or equal to number of clients")
    
    # Validate update dimensions
    dim = len(updates[0])
    if not all(len(update) == dim for update in updates):
        raise ValueError("All updates must have the same dimension")
    
    # Validate graph symmetry
    for i in range(n):
        for j in graph[i]:
            if i not in graph[j]:
                raise ValueError("Graph must be symmetric")

def compute_euclidean_distance(update1: List[float], update2: List[float]) -> float:
    """Compute Euclidean distance between two updates."""
    return np.linalg.norm(np.array(update1) - np.array(update2))

def find_k_nearest_neighbors(client_id: int, updates: List[List[float]], 
                           neighbors: List[int], k: int) -> List[int]:
    """Find k nearest neighbors for a client based on Euclidean distance."""
    distances = [(j, compute_euclidean_distance(updates[client_id], updates[j])) 
                for j in neighbors]
    distances.sort(key=lambda x: x[1])
    return [x[0] for x in distances[:k]]

def compute_krum_score(client_id: int, updates: List[List[float]], 
                      neighbors: List[int], k: int) -> float:
    """Compute Krum score for a client."""
    k_nearest = find_k_nearest_neighbors(client_id, updates, neighbors, k)
    return sum(compute_euclidean_distance(updates[client_id], updates[j]) 
              for j in k_nearest)

def secure_aggregate_neighborhood(client_id: int, updates: List[List[float]], 
                               neighbors: List[int], k: int) -> List[float]:
    """Perform secure aggregation within a neighborhood."""
    # Find client with minimum Krum score in the neighborhood
    neighborhood = neighbors + [client_id]
    scores = [(i, compute_krum_score(i, updates, neighborhood, k)) 
             for i in neighborhood]
    best_client = min(scores, key=lambda x: x[1])[0]
    
    # Create noise matrix for secure aggregation
    dim = len(updates[0])
    noise_matrix = defaultdict(lambda: np.random.normal(0, 0.01, dim))
    
    # Generate pairwise noise that sums to zero
    for i in neighborhood:
        for j in neighborhood:
            if i < j:
                noise_matrix[(i,j)] = np.random.normal(0, 0.01, dim)
                noise_matrix[(j,i)] = -noise_matrix[(i,j)]
    
    # Compute noisy aggregate
    aggregate = np.array(updates[best_client])
    for i in neighborhood:
        if i != best_client:
            aggregate += noise_matrix[(best_client, i)]
    
    return aggregate.tolist()

def aggregate_updates(updates: List[List[float]], graph: List[List[int]], 
                     f: int, rounds: int, k: int) -> List[List[float]]:
    """Main function to perform decentralized federated learning aggregation."""
    # Validate inputs
    validate_inputs(updates, graph, f, rounds, k)
    
    n = len(updates)
    dim = len(updates[0])
    current_updates = [u.copy() for u in updates]
    
    for _ in range(rounds):
        new_updates = []
        
        # Each client performs local aggregation
        for i in range(n):
            # Perform secure aggregation within neighborhood
            neighborhood_aggregate = secure_aggregate_neighborhood(
                i, current_updates, graph[i], k)
            
            # Add small random noise for differential privacy
            noise = np.random.normal(0, 0.001, dim)
            new_update = np.array(neighborhood_aggregate) + noise
            
            new_updates.append(new_update.tolist())
        
        # Update all clients
        current_updates = new_updates
    
    return current_updates