from collections import defaultdict
from typing import List, Tuple, Set

def reach_consensus(n: int, m: int, commander_decision: bool, 
                   messages: List[Tuple[int, int, bool]]) -> List[bool]:
    """
    Implements Byzantine Agreement algorithm with faulty messengers.
    
    Args:
        n: Number of generals
        m: Number of faulty messengers
        commander_decision: Initial decision from commander (True/False)
        messages: List of (sender_id, receiver_id, message_content) tuples
        
    Returns:
        List of final decisions for each general
    """
    # Input validation
    if not 3 <= n <= 1000:
        raise ValueError("Number of generals must be between 3 and 1000")
    if not 0 <= m < n:
        raise ValueError("Number of faulty messengers must be less than number of generals")
    
    # Validate messages
    for sender, receiver, _ in messages:
        if not (0 <= sender < n and 0 <= receiver < n):
            raise ValueError("Invalid sender or receiver ID in messages")

    # Initialize message records for each general
    message_records = [defaultdict(list) for _ in range(n)]
    
    # Initialize with commander's decision
    for i in range(n):
        if i != 0:  # All except commander
            message_records[i][0].append(commander_decision)
    
    # Process all messages
    processed_messages: Set[Tuple[int, int]] = set()
    for sender, receiver, content in messages:
        if (sender, receiver) in processed_messages:
            continue
            
        # Record the message for the receiver
        message_records[receiver][sender].append(content)
        processed_messages.add((sender, receiver))

    # Make decisions
    final_decisions = []
    for general_id in range(n):
        if general_id == 0:  # Commander
            final_decisions.append(commander_decision)
            continue
            
        # Collect all received values
        received_values = []
        for sender in range(n):
            if sender != general_id:
                messages_from_sender = message_records[general_id][sender]
                if messages_from_sender:
                    # Take majority vote from this sender if multiple messages
                    true_count = sum(1 for msg in messages_from_sender if msg)
                    false_count = len(messages_from_sender) - true_count
                    received_values.append(true_count > false_count)

        # Make decision based on majority of received values
        if not received_values:  # If no messages received
            final_decisions.append(commander_decision)
        else:
            # Count True vs False values
            true_count = sum(1 for val in received_values if val)
            false_count = len(received_values) - true_count
            
            # Factor in the number of faulty messengers
            if m == 0:
                # With no faulty messengers, follow commander
                final_decisions.append(commander_decision)
            else:
                # With faulty messengers, use majority vote with threshold
                threshold = (len(received_values) - m) // 2
                final_decisions.append(true_count > threshold)

    # Ensure consistency in the presence of faulty messengers
    if m > 0:
        # If majority of generals agree on a decision, enforce that decision
        true_count = sum(1 for decision in final_decisions if decision)
        majority_decision = true_count > len(final_decisions) // 2
        final_decisions = [majority_decision] * n

    return final_decisions