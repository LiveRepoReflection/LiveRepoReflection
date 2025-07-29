from collections import defaultdict
from typing import List, Tuple, Set

def simulate_network(
    N: int,
    links: List[Tuple[int, int, int]],
    initial_rates: List[float],
    routes: List[List[List[int]]],
    T: int,
    alpha: float,
    beta: float,
    max_rate: float
) -> List[float]:
    """
    Simulates network congestion control for T time steps.
    
    Args:
        N: Number of nodes
        links: List of (source, destination, capacity) tuples
        initial_rates: Initial sending rates for each node
        routes: List of possible routes for each node
        T: Number of time steps to simulate
        alpha: Additive increase factor
        beta: Multiplicative decrease factor
        max_rate: Maximum allowed sending rate
    
    Returns:
        List of final sending rates for each node
    """
    # Input validation
    if N <= 0:
        raise ValueError("Number of nodes must be positive")
    if alpha <= 0:
        raise ValueError("Alpha must be positive")
    if beta <= 0 or beta >= 1:
        raise ValueError("Beta must be between 0 and 1")
    if max_rate <= 0:
        raise ValueError("Maximum rate must be positive")

    # Create link capacity dictionary
    link_capacities = {(u, v): cap for u, v, cap in links}
    
    # Initialize current rates
    current_rates = initial_rates.copy()
    
    # Create link usage mapping
    def get_links_used_by_node(node: int) -> Set[Tuple[int, int]]:
        links_used = set()
        for route in routes[node]:
            for i in range(len(route) - 1):
                links_used.add((route[i], route[i + 1]))
        return links_used

    # Simulate for T time steps
    for _ in range(T):
        # Calculate flow on each link
        link_flows = defaultdict(float)
        node_uses_congested_link = [False] * N
        
        # Calculate total flow through each link
        for node in range(N):
            for route in routes[node]:
                for i in range(len(route) - 1):
                    link = (route[i], route[i + 1])
                    link_flows[link] += current_rates[node]
        
        # Check for congestion and mark affected nodes
        for node in range(N):
            links_used = get_links_used_by_node(node)
            for link in links_used:
                if link in link_capacities and link_flows[link] > link_capacities[link]:
                    node_uses_congested_link[node] = True
                    break
        
        # Update rates based on congestion
        for node in range(N):
            if node_uses_congested_link[node]:
                # Multiplicative decrease
                current_rates[node] *= beta
            else:
                # Additive increase
                current_rates[node] = min(current_rates[node] + alpha, max_rate)
            
            # Ensure rate stays within bounds
            current_rates[node] = max(0, min(current_rates[node], max_rate))
    
    return current_rates