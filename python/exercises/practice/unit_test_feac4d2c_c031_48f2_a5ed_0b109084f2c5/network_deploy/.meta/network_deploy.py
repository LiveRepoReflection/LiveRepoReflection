import math
import random
from itertools import combinations

def euclidean_distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def assign_nodes_to_routers(nodes, routers):
    assignments = []
    for node in nodes:
        min_dist = float('inf')
        best_router = None
        for i, router in enumerate(routers):
            dist = euclidean_distance(node, router)
            if dist < min_dist or (dist == min_dist and i < best_router):
                min_dist = dist
                best_router = i
        assignments.append(best_router)
    return assignments

def calculate_average_latency(nodes, routers, assignments):
    total_latency = 0
    count = 0
    router_positions = [routers[i] for i in assignments]
    
    for i, j in combinations(range(len(nodes)), 2):
        router_i = assignments[i]
        router_j = assignments[j]
        
        dist_i = euclidean_distance(nodes[i], routers[router_i])
        dist_j = euclidean_distance(nodes[j], routers[router_j])
        dist_routers = euclidean_distance(routers[router_i], routers[router_j])
        
        total_latency += dist_i + dist_j + dist_routers
        count += 1
    
    return total_latency / count if count > 0 else 0

def k_means_plusplus(nodes, k):
    routers = [random.choice(nodes)]
    
    for _ in range(1, k):
        distances = []
        for node in nodes:
            min_dist = min(euclidean_distance(node, r) for r in routers)
            distances.append(min_dist**2)
        
        total = sum(distances)
        r = random.uniform(0, total)
        cumulative = 0
        for i, d in enumerate(distances):
            cumulative += d
            if cumulative >= r:
                routers.append(nodes[i])
                break
    
    return routers

def optimize_routers(nodes, initial_routers, max_iterations=100):
    routers = initial_routers.copy()
    
    for _ in range(max_iterations):
        assignments = assign_nodes_to_routers(nodes, routers)
        
        new_routers = []
        for i in range(len(routers)):
            cluster_nodes = [nodes[j] for j in range(len(nodes)) if assignments[j] == i]
            if not cluster_nodes:
                new_routers.append(routers[i])
                continue
            
            avg_x = sum(n[0] for n in cluster_nodes) / len(cluster_nodes)
            avg_y = sum(n[1] for n in cluster_nodes) / len(cluster_nodes)
            new_routers.append((round(avg_x), round(avg_y)))
        
        if new_routers == routers:
            break
        routers = new_routers
    
    return routers

def optimal_router_placement(nodes, k):
    if k >= len(nodes):
        return nodes[:k]
    
    # Initialize with k-means++
    initial_routers = k_means_plusplus(nodes, k)
    
    # Optimize with k-means
    optimized_routers = optimize_routers(nodes, initial_routers)
    
    # Final refinement with local search
    best_routers = optimized_routers
    best_latency = calculate_average_latency(nodes, optimized_routers, 
                                           assign_nodes_to_routers(nodes, optimized_routers))
    
    # Try small perturbations to escape local minima
    for _ in range(5):
        perturbed = [(x + random.randint(-1, 1), y + random.randint(-1, 1)) 
                    for x, y in optimized_routers]
        perturbed = [(max(0, min(1000, x)), max(0, min(1000, y))) for x, y in perturbed]
        current_latency = calculate_average_latency(nodes, perturbed, 
                                                  assign_nodes_to_routers(nodes, perturbed))
        if current_latency < best_latency:
            best_latency = current_latency
            best_routers = perturbed
    
    return best_routers