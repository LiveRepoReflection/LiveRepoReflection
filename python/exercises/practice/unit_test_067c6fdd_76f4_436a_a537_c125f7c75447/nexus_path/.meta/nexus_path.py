import heapq
from collections import deque

def find_most_efficient_path(network, start_user_id, target_user_id, max_hops):
    if start_user_id not in network or target_user_id not in network:
        return []
    
    if start_user_id == target_user_id:
        return [start_user_id]
    
    # Priority queue: (current_product, current_latency, hops_remaining, path)
    heap = []
    heapq.heappush(heap, (0, 0, max_hops, [start_user_id]))
    
    visited = {}
    visited[(start_user_id, 0)] = 0  # (node, hops_remaining): min_product
    
    best_path = []
    best_product = float('inf')
    
    while heap:
        current_product, current_latency, hops_remaining, path = heapq.heappop(heap)
        
        current_node = path[-1]
        
        if current_node == target_user_id:
            if current_product < best_product:
                best_product = current_product
                best_path = path
            continue
        
        if hops_remaining == 0:
            continue
            
        if current_product > best_product:
            continue
            
        for neighbor in network[current_node]['friend_ids']:
            if neighbor not in network:
                continue
                
            new_latency = current_latency + network[neighbor]['latency']
            new_hops = hops_remaining - 1
            path_length = len(path) + 1 - 1  # hops = path_length - 1
            new_product = path_length * new_latency
            
            if (neighbor, new_hops) in visited and visited[(neighbor, new_hops)] <= new_product:
                continue
                
            visited[(neighbor, new_hops)] = new_product
            new_path = path + [neighbor]
            heapq.heappush(heap, (new_product, new_latency, new_hops, new_path))
    
    return best_path