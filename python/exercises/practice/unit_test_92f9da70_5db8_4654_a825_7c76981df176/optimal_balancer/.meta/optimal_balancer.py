from typing import List, Tuple
from dataclasses import dataclass
import heapq


@dataclass
class Server:
    id: int
    capacity: int
    health_score: float
    current_load: int = 0

    def can_handle_request(self, request_time: int) -> bool:
        return self.current_load + request_time <= self.capacity

    def add_request(self, request_time: int) -> None:
        self.current_load += request_time

    def get_cost_factor(self, alpha: float, request_time: int) -> float:
        # Calculate weighted cost based on health score and current load
        latency_cost = request_time
        availability_cost = (1 - self.health_score) * (self.current_load + request_time)
        return alpha * latency_cost + (1 - alpha) * availability_cost


def validate_inputs(servers: List[Tuple[int, int, float]], 
                   requests: List[int], 
                   time_window: int, 
                   alpha: float) -> None:
    """Validate all input parameters."""
    if not servers:
        raise ValueError("Servers list cannot be empty")
    
    if time_window <= 0:
        raise ValueError("Time window must be positive")
    
    if not 0 <= alpha <= 1:
        raise ValueError("Alpha must be between 0 and 1")
    
    for server_id, capacity, health_score in servers:
        if capacity <= 0:
            raise ValueError(f"Server {server_id} has invalid capacity")
        if not 0 <= health_score <= 1:
            raise ValueError(f"Server {server_id} has invalid health score")
    
    for req_time in requests:
        if req_time <= 0:
            raise ValueError("Request processing time must be positive")


def check_total_capacity(servers: List[Tuple[int, int, float]], 
                        requests: List[int]) -> None:
    """Check if servers have enough total capacity for all requests."""
    total_capacity = sum(capacity for _, capacity, _ in servers)
    total_request_time = sum(requests)
    
    if total_request_time > total_capacity:
        raise ValueError("Insufficient total server capacity for requests")


def balance_load(servers: List[Tuple[int, int, float]], 
                requests: List[int], 
                time_window: int, 
                alpha: float) -> List[int]:
    """
    Optimally distribute requests across servers to minimize latency and maximize availability.
    
    Args:
        servers: List of (server_id, capacity, health_score) tuples
        requests: List of request processing times
        time_window: Time window for scheduling
        alpha: Weight factor for latency vs availability trade-off
    
    Returns:
        List of server IDs assignments for each request
    """
    # Validate inputs
    validate_inputs(servers, requests, time_window, alpha)
    
    # Handle empty requests case
    if not requests:
        return []
    
    # Check total capacity
    check_total_capacity(servers, requests)
    
    # Initialize server objects
    server_objects = [Server(sid, cap, health) 
                     for sid, cap, health in servers]
    
    # Initialize result array
    assignments = [-1] * len(requests)
    
    # Sort requests in descending order with their indices
    request_indices = list(range(len(requests)))
    request_indices.sort(key=lambda i: requests[i], reverse=True)
    
    # Process each request
    for req_idx in request_indices:
        request_time = requests[req_idx]
        
        # Find best server for this request
        best_server = None
        min_cost = float('inf')
        
        for server in server_objects:
            if server.can_handle_request(request_time):
                cost = server.get_cost_factor(alpha, request_time)
                
                # Update best server if this one has lower cost
                if cost < min_cost:
                    min_cost = cost
                    best_server = server
        
        if best_server is None:
            raise ValueError("Cannot find valid server assignment")
        
        # Assign request to best server
        best_server.add_request(request_time)
        assignments[req_idx] = best_server.id
    
    return assignments


def get_optimal_cost(servers: List[Tuple[int, int, float]], 
                    requests: List[int],
                    assignments: List[int],
                    alpha: float) -> float:
    """Calculate the total cost of the assignment solution."""
    server_loads = {sid: 0 for sid, _, _ in servers}
    server_health = {sid: health for sid, _, health in servers}
    
    for req_idx, server_id in enumerate(assignments):
        server_loads[server_id] += requests[req_idx]
    
    latency_cost = sum(requests)
    availability_cost = sum((1 - server_health[sid]) * load 
                          for sid, load in server_loads.items())
    
    return alpha * latency_cost + (1 - alpha) * availability_cost