def simulate_congestion_control(n, network, initial_rate, max_rate, congestion_threshold, 
                               decrease_factor, increase_increment, num_rounds):
    """
    Simulates a network congestion control algorithm.
    
    Args:
        n (int): Number of nodes in the network
        network (dict): Adjacency list representing network topology
        initial_rate (float): Initial sending rate for each node
        max_rate (float): Maximum allowable sending rate for any node
        congestion_threshold (float): Threshold for link utilization that triggers congestion
        decrease_factor (float): Factor by which to decrease sending rate when congestion occurs
        increase_increment (float): Amount to increase sending rate when no congestion
        num_rounds (int): Number of simulation rounds
        
    Returns:
        list: Final sending rates for each node after simulation
    """
    # Initialize the sending rates for all nodes
    sending_rates = [initial_rate] * n
    
    # For nodes with no outgoing links in the network dictionary, add empty lists
    for i in range(n):
        if i not in network:
            network[i] = []
    
    for _ in range(num_rounds):
        # Calculate link utilizations
        link_utilizations = {}  # (from_node, to_node) -> utilization
        
        # For each sending node
        for from_node, links in network.items():
            # For each link from this node
            for to_node, capacity in links:
                # Initialize link utilization if not already done
                link_key = (from_node, to_node)
                if link_key not in link_utilizations:
                    link_utilizations[link_key] = 0
                
                # Add the current sender's rate to the link utilization
                link_utilizations[link_key] += sending_rates[from_node]
                
        # Track congestion signals for each node
        congestion_signals = [False] * n
        
        # Check for congestion on each link
        for (from_node, to_node), utilization in link_utilizations.items():
            # Find the link capacity
            capacity = next(cap for node, cap in network[from_node] if node == to_node)
            
            # Check if link is congested
            if capacity > 0 and utilization / capacity > congestion_threshold:
                # Signal the sending node about congestion
                congestion_signals[from_node] = True
        
        # Update sending rates based on congestion signals
        for i in range(n):
            if congestion_signals[i]:
                # Decrease rate due to congestion
                sending_rates[i] = max(sending_rates[i] * decrease_factor, 0)
            else:
                # Increase rate if no congestion and node has outgoing links
                if network[i]:  # Check if the node has outgoing links
                    sending_rates[i] = min(sending_rates[i] + increase_increment, max_rate)
    
    return sending_rates