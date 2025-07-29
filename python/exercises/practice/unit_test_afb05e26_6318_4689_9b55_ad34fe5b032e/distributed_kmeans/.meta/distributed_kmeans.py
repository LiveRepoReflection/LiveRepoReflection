import math
from typing import List, Tuple
import copy

def distributed_kmeans(data_fragments: List[List[List[float]]], 
                        k: int, 
                        initial_centroids: List[List[float]], 
                        convergence_threshold: float = 1e-6,
                        max_iterations: int = 100) -> List[List[float]]:
    """
    Distributed k-means clustering algorithm.
    
    Args:
        data_fragments: List of lists, where each inner list is a data fragment (subset of data points)
                       residing on a different node. Each data point is a list of numerical features.
        k: Integer representing the desired number of clusters.
        initial_centroids: Initial positions of centroids.
        convergence_threshold: Threshold for convergence check.
        max_iterations: Maximum number of iterations.
        
    Returns:
        List of final centroid positions after convergence.
    """
    # Input validation
    if not data_fragments:
        raise ValueError("data_fragments cannot be empty")
    
    if k <= 0:
        raise ValueError("k must be a positive integer")
    
    # Validate data dimensions consistency
    total_points = 0
    dimensions = None
    
    for fragment in data_fragments:
        if not fragment:
            continue
            
        total_points += len(fragment)
        
        for point in fragment:
            if dimensions is None:
                dimensions = len(point)
            elif len(point) != dimensions:
                raise ValueError("All data points must have the same dimensions")
    
    if k > total_points:
        raise ValueError("k cannot be greater than the total number of data points")
    
    # Validate centroid dimensions
    if not initial_centroids or len(initial_centroids) != k:
        raise ValueError(f"initial_centroids must contain exactly {k} centroids")
    
    for centroid in initial_centroids:
        if len(centroid) != dimensions:
            raise ValueError("Centroid dimensions must match data point dimensions")
    
    # Initialize centroids
    centroids = copy.deepcopy(initial_centroids)
    
    # Main k-means loop
    for iteration in range(max_iterations):
        # Step 2: Assignment (Distributed)
        assigned_points = []
        
        for fragment_idx, fragment in enumerate(data_fragments):
            local_assignments = assign_points_to_centroids(fragment, centroids)
            assigned_points.extend(local_assignments)
        
        # Step 3: Update Centroids
        new_centroids = update_centroids(assigned_points, k, dimensions)
        
        # Step 4: Convergence Check
        if check_convergence(centroids, new_centroids, convergence_threshold):
            break
        
        centroids = new_centroids
    
    return centroids

def assign_points_to_centroids(data_points: List[List[float]], 
                              centroids: List[List[float]]) -> List[Tuple[int, List[float]]]:
    """
    Assign each data point to the nearest centroid based on Euclidean distance.
    
    Args:
        data_points: List of data points.
        centroids: List of centroid positions.
        
    Returns:
        List of tuples (centroid_index, data_point).
    """
    assignments = []
    
    for point in data_points:
        # Find the nearest centroid for this point
        min_distance = float('inf')
        min_centroid_idx = -1
        
        for idx, centroid in enumerate(centroids):
            distance = euclidean_distance(point, centroid)
            
            if distance < min_distance:
                min_distance = distance
                min_centroid_idx = idx
        
        assignments.append((min_centroid_idx, point))
    
    return assignments

def update_centroids(assigned_points: List[Tuple[int, List[float]]], 
                     k: int, 
                     dimensions: int) -> List[List[float]]:
    """
    Update the centroids based on the mean of assigned points.
    
    Args:
        assigned_points: List of tuples (centroid_index, data_point).
        k: Number of centroids.
        dimensions: Number of dimensions.
        
    Returns:
        List of updated centroid positions.
    """
    # Initialize counters and sums for each centroid
    centroid_counts = [0] * k
    centroid_sums = [[0.0] * dimensions for _ in range(k)]
    
    # Accumulate sums for each centroid
    for centroid_idx, point in assigned_points:
        centroid_counts[centroid_idx] += 1
        
        for dim in range(dimensions):
            centroid_sums[centroid_idx][dim] += point[dim]
    
    # Calculate new centroid positions
    new_centroids = []
    for idx in range(k):
        if centroid_counts[idx] > 0:
            # If there are points assigned to this centroid, update it
            new_centroid = [centroid_sums[idx][dim] / centroid_counts[idx] for dim in range(dimensions)]
            new_centroids.append(new_centroid)
        else:
            # If no points are assigned to this centroid, keep it at its current position
            # This is necessary to handle the edge case where a centroid has no assigned points
            # We'll create a dummy centroid at (0, 0, ...) in this case
            new_centroids.append([0.0] * dimensions)
    
    return new_centroids

def check_convergence(old_centroids: List[List[float]], 
                      new_centroids: List[List[float]], 
                      threshold: float) -> bool:
    """
    Check if the algorithm has converged by comparing old and new centroids.
    
    Args:
        old_centroids: Previous centroid positions.
        new_centroids: Updated centroid positions.
        threshold: Convergence threshold.
        
    Returns:
        True if algorithm has converged, False otherwise.
    """
    # Calculate the sum of squared distances between old and new centroids
    sum_squared_distances = 0.0
    
    for old, new in zip(old_centroids, new_centroids):
        sum_squared_distances += euclidean_distance_squared(old, new)
    
    return sum_squared_distances < threshold

def euclidean_distance(point1: List[float], point2: List[float]) -> float:
    """
    Calculate the Euclidean distance between two points.
    
    Args:
        point1: First point.
        point2: Second point.
        
    Returns:
        Euclidean distance.
    """
    return math.sqrt(euclidean_distance_squared(point1, point2))

def euclidean_distance_squared(point1: List[float], point2: List[float]) -> float:
    """
    Calculate the squared Euclidean distance between two points.
    
    Args:
        point1: First point.
        point2: Second point.
        
    Returns:
        Squared Euclidean distance.
    """
    return sum((a - b) ** 2 for a, b in zip(point1, point2))