def validate_input(N, transactions):
    if not isinstance(N, int) or N < 1 or N > 1000:
        raise ValueError("N must be an integer between 1 and 1000")
    
    for idx, (coordinator_id, participants, commit_prob) in enumerate(transactions):
        if not isinstance(coordinator_id, int) or coordinator_id < 0 or coordinator_id >= N:
            raise ValueError(f"Transaction {idx}: coordinator_id must be between 0 and N-1")
        
        if not isinstance(participants, set) or any(p < 0 or p >= N for p in participants):
            raise ValueError(f"Transaction {idx}: participants must be a set of valid node IDs")
            
        if not isinstance(commit_prob, float) or commit_prob < 0.0 or commit_prob > 1.0:
            raise ValueError(f"Transaction {idx}: commit_prob must be a float between 0.0 and 1.0")
            
        if coordinator_id not in participants:
            raise ValueError(f"Transaction {idx}: coordinator must be included in participants")