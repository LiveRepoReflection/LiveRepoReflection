from typing import List, Tuple, Dict
import heapq
from collections import defaultdict

def optimize_network(
    data_centers: List[Tuple[int, float, float]],
    user_requests: List[Tuple[int, Tuple[float, float], int, int]],
    latency_matrix: Dict[Tuple[Tuple[float, float], int], int]
) -> Dict[int, List[int]]:
    """
    Optimizes CDN network assignments using a modified min-cost flow approach.
    
    Args:
        data_centers: List of (data_center_id, capacity_gbps, operational_cost_per_gbps)
        user_requests: List of (request_id, user_location, bandwidth_demand_mbps, latency_requirement_ms)
        latency_matrix: Dict of ((user_location, data_center_id), latency_ms)
    
    Returns:
        Dict mapping data_center_id to list of assigned request_ids
    """
    if not data_centers or not user_requests:
        return {}

    # Initialize data structures
    assignments = defaultdict(list)
    dc_remaining_capacity = {dc[0]: dc[1] for dc in data_centers}
    dc_cost = {dc[0]: dc[2] for dc in data_centers}
    
    # Create request objects with all relevant information
    request_objects = []
    for req_id, location, bandwidth, latency_req in user_requests:
        valid_dcs = []
        for dc_id, capacity, _ in data_centers:
            if (location, dc_id) in latency_matrix:
                if latency_matrix[(location, dc_id)] <= latency_req:
                    valid_dcs.append(dc_id)
        
        request_objects.append({
            'id': req_id,
            'bandwidth_gbps': bandwidth / 1000.0,  # Convert Mbps to Gbps
            'valid_dcs': valid_dcs
        })
    
    # Sort requests by bandwidth demand (descending) to handle larger requests first
    request_objects.sort(key=lambda x: x['bandwidth_gbps'], reverse=True)
    
    # First pass: Try to assign requests to their cheapest valid data center
    for request in request_objects:
        # Sort valid data centers by cost
        valid_dcs = sorted(
            request['valid_dcs'],
            key=lambda dc_id: dc_cost[dc_id]
        )
        
        assigned = False
        for dc_id in valid_dcs:
            if dc_remaining_capacity[dc_id] >= request['bandwidth_gbps']:
                assignments[dc_id].append(request['id'])
                dc_remaining_capacity[dc_id] -= request['bandwidth_gbps']
                assigned = True
                break
    
    # Second pass: Optimization phase
    improved = True
    while improved:
        improved = False
        
        # Try to swap assignments to reduce cost
        for dc1_id in assignments:
            for dc2_id in assignments:
                if dc1_id == dc2_id:
                    continue
                    
                for req1_id in assignments[dc1_id]:
                    for req2_id in assignments[dc2_id]:
                        # Find original requests
                        req1 = next(r for r in request_objects if r['id'] == req1_id)
                        req2 = next(r for r in request_objects if r['id'] == req2_id)
                        
                        # Check if swap is valid
                        if (dc2_id in req1['valid_dcs'] and 
                            dc1_id in req2['valid_dcs']):
                            
                            # Calculate current cost
                            current_cost = (
                                req1['bandwidth_gbps'] * dc_cost[dc1_id] +
                                req2['bandwidth_gbps'] * dc_cost[dc2_id]
                            )
                            
                            # Calculate new cost after swap
                            new_cost = (
                                req1['bandwidth_gbps'] * dc_cost[dc2_id] +
                                req2['bandwidth_gbps'] * dc_cost[dc1_id]
                            )
                            
                            # Check if swap reduces cost and maintains capacity constraints
                            if (new_cost < current_cost and
                                dc_remaining_capacity[dc1_id] + req1['bandwidth_gbps'] >= req2['bandwidth_gbps'] and
                                dc_remaining_capacity[dc2_id] + req2['bandwidth_gbps'] >= req1['bandwidth_gbps']):
                                
                                # Perform swap
                                assignments[dc1_id].remove(req1_id)
                                assignments[dc2_id].remove(req2_id)
                                assignments[dc1_id].append(req2_id)
                                assignments[dc2_id].append(req1_id)
                                
                                # Update remaining capacities
                                dc_remaining_capacity[dc1_id] = (
                                    dc_remaining_capacity[dc1_id] +
                                    req1['bandwidth_gbps'] -
                                    req2['bandwidth_gbps']
                                )
                                dc_remaining_capacity[dc2_id] = (
                                    dc_remaining_capacity[dc2_id] +
                                    req2['bandwidth_gbps'] -
                                    req1['bandwidth_gbps']
                                )
                                
                                improved = True
    
    return dict(assignments)