import numpy as np
from typing import List, Tuple


def network_congestion_control(
    N: int,
    C: int,
    initial_rates: List[float],
    alpha: float,
    reduction_factor: float,
    T: int,
    congestion_notification_probability: float
) -> List[List[float]]:
    """
    Simulates a network congestion control algorithm.
    
    Args:
        N: The number of senders
        C: The bottleneck link capacity (packets per second)
        initial_rates: List of initial sending rates for each sender
        alpha: The additive increase parameter
        reduction_factor: The multiplicative decrease factor (between 0 and 1)
        T: Number of simulation iterations
        congestion_notification_probability: Probability of a sender receiving a congestion notification
        
    Returns:
        A list of lists containing the sending rates of all senders at each iteration
    """
    # Validate inputs
    if len(initial_rates) != N:
        raise ValueError(f"Expected {N} initial rates, got {len(initial_rates)}")
    if not (0 < reduction_factor < 1):
        raise ValueError(f"Reduction factor must be between 0 and 1, got {reduction_factor}")
    if not (0 <= congestion_notification_probability <= 1):
        raise ValueError(f"Congestion notification probability must be between 0 and 1, got {congestion_notification_probability}")
    
    # Convert to numpy arrays for efficient operations
    rates = np.array(initial_rates, dtype=float)
    
    # Initialize results storage with initial rates
    results = [initial_rates.copy()]
    
    # Run simulation for T iterations
    for _ in range(T):
        # Calculate total sending rate
        total_rate = np.sum(rates)
        
        # Check for congestion
        is_congested = total_rate > C
        
        # Determine which senders receive congestion notification
        if is_congested:
            # Calculate packet loss percentage
            loss_percentage = (total_rate - C) / total_rate
            
            # The higher the sender's rate, the more likely they are to experience loss
            # This implements a form of max-min fairness
            sender_loss_probabilities = rates / total_rate
            
            # Normalize to ensure fairness in congestion notification
            # Higher rate senders have higher probability of receiving notification
            normalized_probabilities = sender_loss_probabilities / np.sum(sender_loss_probabilities)
            
            # Scale by congestion_notification_probability
            notification_probabilities = normalized_probabilities * congestion_notification_probability * N
            
            # Ensure probabilities stay within [0, 1]
            notification_probabilities = np.minimum(notification_probabilities, 1.0)
            
            # Generate random values for each sender
            random_values = np.random.random(N)
            
            # Determine which senders receive notification
            receive_notification = random_values < notification_probabilities
            
            # Apply rate adjustments based on notifications
            # Multiplicative decrease for notified senders
            rates[receive_notification] *= reduction_factor
            
            # Additive increase for non-notified senders
            rates[~receive_notification] += alpha
        else:
            # If no congestion, all senders increase their rates
            rates += alpha
        
        # Ensure rates don't go negative
        rates = np.maximum(rates, 0.0)
        
        # Store the rates for this iteration
        results.append(rates.tolist())
    
    return results