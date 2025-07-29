def byzantine_agreement(n, m, initial_order, general_is_traitor):
    """
    Implement the Byzantine Generals Problem algorithm.
    
    Args:
        n: The total number of generals (including the commander).
        m: The maximum number of traitorous generals.
        initial_order: The supreme commander's initial order ('Attack' or 'Retreat').
        general_is_traitor: A function that returns True if a general is a traitor.
        
    Returns:
        The agreed-upon order ('Attack' or 'Retreat') by the loyal generals.
    """
    # Check if the algorithm can handle the given number of traitors
    if n <= 3 * m:
        raise ValueError(f"Cannot guarantee consensus with {n} generals and up to {m} traitors. Need n > 3m.")
    
    # Handle edge case where there's only one general (the commander)
    if n == 1:
        return initial_order
    
    # Initialize message vectors for all generals
    # message_vectors[i][j] represents the message that general i knows general j received from the commander
    message_vectors = [[None for _ in range(n)] for _ in range(n)]
    
    # Phase 1: Commander sends the initial order to all lieutenants
    for i in range(1, n):
        if general_is_traitor(0):  # Commander is a traitor
            # Traitor commander can send different messages to different lieutenants
            # For simulation, we'll have the traitor randomly decide based on lieutenant ID
            message = 'Retreat' if i % 2 == 0 else 'Attack'
        else:
            message = initial_order
        
        # Direct message from commander to lieutenant i
        message_vectors[i][0] = message
        message_vectors[0][i] = message  # Commander knows what he sent
    
    # Phase 2: Lieutenants exchange information (recursive message passing)
    for k in range(1, m+1):  # m rounds of message exchange
        # Each round, lieutenants share what they know about other lieutenants
        new_vectors = [row[:] for row in message_vectors]  # Make a copy
        
        for i in range(1, n):  # For each lieutenant i
            if general_is_traitor(i):
                continue  # Traitors might not participate or send false information
                
            for j in range(1, n):  # Lieutenant i tells lieutenant j what they know
                if i == j:
                    continue  # Skip self
                
                # Lieutenant i tells j about all the messages they've received
                for target in range(n):
                    if message_vectors[i][target] is not None:
                        if not general_is_traitor(i):
                            new_vectors[j][target] = message_vectors[i][target]
        
        message_vectors = new_vectors
    
    # Phase 3: Each loyal lieutenant makes a decision based on their information
    final_decisions = []
    
    for i in range(1, n):  # For each lieutenant
        if general_is_traitor(i):
            continue  # We don't care about traitors' decisions
            
        # Count the messages this lieutenant has received/heard about
        attack_count = sum(1 for msg in message_vectors[i] if msg == 'Attack')
        retreat_count = sum(1 for msg in message_vectors[i] if msg == 'Retreat')
        
        # Lieutenant decides based on majority
        if attack_count > retreat_count:
            final_decisions.append('Attack')
        else:
            final_decisions.append('Retreat')
    
    # Ensure all loyal lieutenants have reached the same decision
    if not final_decisions:
        # Edge case: if all lieutenants are traitors, follow commander's order
        return initial_order
    
    loyal_decision = max(set(final_decisions), key=final_decisions.count)
    return loyal_decision


def oral_message(sender, receivers, value, level, traitors, message_history=None):
    """
    Helper function for implementing the Oral Message algorithm (a recursive approach).
    
    Args:
        sender: The ID of the general sending the message.
        receivers: List of general IDs receiving the message.
        value: The value being sent ('Attack' or 'Retreat').
        level: The recursion level (starts at m, decreases to 0).
        traitors: Set of general IDs who are traitors.
        message_history: Dictionary to keep track of messages for debugging.
        
    Returns:
        A dictionary mapping each receiver to their received value.
    """
    if message_history is None:
        message_history = {}
    
    results = {}
    
    # Base case
    if level == 0:
        for receiver in receivers:
            if sender in traitors:
                # Traitor might send different messages to different receivers
                results[receiver] = 'Attack' if receiver % 2 == 0 else 'Retreat'
            else:
                results[receiver] = value
                
            # Record the message for debugging
            key = (sender, receiver, level)
            message_history[key] = results[receiver]
            
        return results
    
    # Recursive case
    for receiver in receivers:
        if sender in traitors:
            # Traitor might behave unpredictably
            sub_value = 'Attack' if receiver % 2 == 0 else 'Retreat'
        else:
            sub_value = value
            
        # Record this message
        key = (sender, receiver, level)
        message_history[key] = sub_value
        
        # Recursively send messages from receiver to others
        sub_receivers = [r for r in range(len(receivers) + 1) if r != sender and r != receiver]
        sub_results = oral_message(receiver, sub_receivers, sub_value, level - 1, traitors, message_history)
        
        # Update results
        results.update(sub_results)
    
    return results