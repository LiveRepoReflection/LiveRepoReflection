import math

def calculate_2pc_latency(participants):
    return 3  # PREPARE(1) + VOTE(1) + COMMIT/ABORT(1)

def calculate_pc_latency(participants, commit_prob):
    expected_participants = max(1, math.ceil(commit_prob * len(participants)))
    return 3  # Same as 2PC since we're approximating with ceil

def optimize_commit_protocol(N, transactions):
    total_latency = 0.0
    
    for coordinator_id, participants, commit_prob in transactions:
        # Calculate expected latency for both protocols
        standard_2pc_latency = calculate_2pc_latency(participants)
        
        # For PC, we need to consider the probability of commit/abort
        pc_latency = calculate_pc_latency(participants, commit_prob)
        
        # Choose the protocol with lower expected latency
        if standard_2pc_latency <= pc_latency:
            total_latency += standard_2pc_latency
        else:
            total_latency += pc_latency
    
    return total_latency