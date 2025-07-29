import math
import random
import numpy as np
from collections import defaultdict
from scipy.spatial.distance import cdist
from typing import List, Tuple

def optimize_network_placement(nodes: List[Tuple[int, int]], k: int) -> Tuple[List[Tuple[float, float]], List[int]]:
    """
    Optimize the placement of K gateway servers to minimize the maximum latency.
    
    Args:
        nodes: List of (x, y) coordinates for compute nodes
        k: Number of gateway servers to place
    
    Returns:
        Tuple containing:
        - List of (x, y) coordinates for the gateway servers
        - List of assignments (which gateway each node connects to)
    """
    # Handle edge cases
    n = len(nodes)
    
    # Edge case: K equals N, place gateway at each node
    if k >= n:
        return nodes[:k], list(range(min(n, k)))
    
    # Edge case: K=1, use geometric median
    if k == 1:
        gateway = find_geometric_median(nodes)
        return [gateway], [0] * n
    
    # Initialize solution with K-means++ seeding
    best_gateways, best_assignments = kmeans_plus_plus(nodes, k)
    best_max_latency = calculate_max_latency(nodes, best_gateways, best_assignments)
    
    # Try different optimization techniques and keep the best result
    for _ in range(3):  # Try a few different starting points
        # K-means with Lloyd's algorithm
        gateways, assignments = kmeans_lloyd(nodes, k, max_iterations=50)
        max_latency = calculate_max_latency(nodes, gateways, assignments)
        
        if max_latency < best_max_latency:
            best_gateways = gateways
            best_assignments = assignments
            best_max_latency = max_latency
    
    # Apply local optimization to refine the solution
    improved_gateways, improved_assignments = local_optimization(nodes, best_gateways, best_assignments)
    improved_max_latency = calculate_max_latency(nodes, improved_gateways, improved_assignments)
    
    if improved_max_latency < best_max_latency:
        best_gateways = improved_gateways
        best_assignments = improved_assignments
    
    return best_gateways, best_assignments

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def calculate_max_latency(nodes: List[Tuple[int, int]], gateways: List[Tuple[float, float]], 
                         assignments: List[int]) -> float:
    """Calculate the maximum latency based on node assignments."""
    max_latency = 0
    for i, node in enumerate(nodes):
        gateway = gateways[assignments[i]]
        distance = calculate_distance(node, gateway)
        max_latency = max(max_latency, distance)
    return max_latency

def find_geometric_median(points: List[Tuple[int, int]]) -> Tuple[float, float]:
    """
    Find the geometric median of a set of points using an iterative method.
    """
    # Initial guess: centroid of points
    if not points:
        return (0.0, 0.0)
    
    n = len(points)
    x_sum = sum(p[0] for p in points)
    y_sum = sum(p[1] for p in points)
    
    median = (x_sum / n, y_sum / n)
    
    # Weiszfeld's algorithm
    epsilon = 1e-6
    max_iterations = 100
    prev_median = None
    
    for _ in range(max_iterations):
        numerator_x = 0
        numerator_y = 0
        denominator = 0
        
        for point in points:
            distance = calculate_distance(median, point)
            if distance < epsilon:  # Avoid division by zero
                # If we're very close to a point, just return that point
                return point
            
            weight = 1 / distance
            numerator_x += weight * point[0]
            numerator_y += weight * point[1]
            denominator += weight
        
        if denominator == 0:
            break
            
        new_median = (numerator_x / denominator, numerator_y / denominator)
        
        # Check for convergence
        if prev_median is not None:
            if calculate_distance(new_median, prev_median) < epsilon:
                break
        
        prev_median = median
        median = new_median
    
    return median

def kmeans_plus_plus(points: List[Tuple[int, int]], k: int) -> Tuple[List[Tuple[float, float]], List[int]]:
    """
    Initialize cluster centers using K-means++ algorithm.
    This improves the starting positions for K-means clustering.
    """
    n = len(points)
    centers = []
    
    # Choose first center randomly
    first_center_idx = random.randrange(n)
    centers.append(points[first_center_idx])
    
    # Choose the remaining centers
    for _ in range(1, k):
        # Calculate distances from points to the nearest existing center
        distances = []
        for point in points:
            min_dist = float('inf')
            for center in centers:
                dist = calculate_distance(point, center)
                min_dist = min(min_dist, dist)
            distances.append(min_dist ** 2)  # Square for probability weighting
        
        # Convert distances to probabilities
        total = sum(distances)
        if total == 0:  # All points coincide with existing centers
            # Choose a random point as the next center
            idx = random.randrange(n)
            centers.append(points[idx])
        else:
            probabilities = [d / total for d in distances]
            # Choose the next center based on these probabilities
            idx = random.choices(range(n), weights=probabilities, k=1)[0]
            centers.append(points[idx])
    
    # Assign points to nearest center
    assignments = assign_points(points, centers)
    
    return centers, assignments

def assign_points(points: List[Tuple[int, int]], centers: List[Tuple[float, float]]) -> List[int]:
    """
    Assign each point to the nearest center.
    """
    assignments = []
    for point in points:
        min_dist = float('inf')
        min_idx = 0
        for i, center in enumerate(centers):
            dist = calculate_distance(point, center)
            if dist < min_dist:
                min_dist = dist
                min_idx = i
        assignments.append(min_idx)
    return assignments

def update_centers(points: List[Tuple[int, int]], assignments: List[int], k: int) -> List[Tuple[float, float]]:
    """
    Update centers based on the mean of assigned points.
    """
    new_centers = []
    for i in range(k):
        cluster_points = [points[j] for j in range(len(points)) if assignments[j] == i]
        if not cluster_points:
            # If no points assigned, keep the old center or choose a random point
            if i < len(points):
                new_centers.append(points[random.randrange(len(points))])
            else:
                new_centers.append((random.uniform(0, 1000), random.uniform(0, 1000)))
        else:
            # Calculate the center as the mean of assigned points
            x_sum = sum(p[0] for p in cluster_points)
            y_sum = sum(p[1] for p in cluster_points)
            new_centers.append((x_sum / len(cluster_points), y_sum / len(cluster_points)))
    
    return new_centers

def kmeans_lloyd(points: List[Tuple[int, int]], k: int, max_iterations: int = 100) -> Tuple[List[Tuple[float, float]], List[int]]:
    """
    Perform K-means clustering using Lloyd's algorithm.
    
    Args:
        points: List of points to cluster
        k: Number of clusters
        max_iterations: Maximum number of iterations
        
    Returns:
        Tuple containing:
        - List of center coordinates
        - List of assignments (which center each point belongs to)
    """
    # Initialize centers using K-means++
    centers, assignments = kmeans_plus_plus(points, k)
    
    for _ in range(max_iterations):
        # Assign points to nearest centers
        new_assignments = assign_points(points, centers)
        
        # Check for convergence
        if new_assignments == assignments:
            break
        
        assignments = new_assignments
        
        # Update centers
        centers = update_centers(points, assignments, k)
    
    # Final assignment to ensure consistency
    assignments = assign_points(points, centers)
    
    return centers, assignments

def local_optimization(nodes: List[Tuple[int, int]], gateways: List[Tuple[float, float]], 
                      assignments: List[int]) -> Tuple[List[Tuple[float, float]], List[int]]:
    """
    Apply local optimization to refine the gateway positions.
    
    The idea is to iteratively move each gateway to minimize the maximum distance
    to its assigned nodes.
    """
    k = len(gateways)
    improved_gateways = list(gateways)
    improved_assignments = list(assignments)
    
    # Group nodes by their assigned gateway
    gateway_nodes = [[] for _ in range(k)]
    for i, assignment in enumerate(assignments):
        gateway_nodes[assignment].append(i)
    
    # Iterate a few times to refine the solution
    for _ in range(5):
        # Optimize each gateway position
        for i in range(k):
            if not gateway_nodes[i]:
                continue
                
            # Find the geometric median of the nodes assigned to this gateway
            assigned_nodes = [nodes[idx] for idx in gateway_nodes[i]]
            improved_gateways[i] = find_geometric_median(assigned_nodes)
        
        # Reassign nodes to gateways
        improved_assignments = assign_points(nodes, improved_gateways)
        
        # Update node groupings
        gateway_nodes = [[] for _ in range(k)]
        for i, assignment in enumerate(improved_assignments):
            gateway_nodes[assignment].append(i)
    
    return improved_gateways, improved_assignments