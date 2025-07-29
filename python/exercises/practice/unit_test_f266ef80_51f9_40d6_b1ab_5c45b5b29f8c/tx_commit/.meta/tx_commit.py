def simulate_commit(N, initial_votes, rounds, coordinator_decision):
    final_state = ["Uncertain"] * N
    for i, nodes in enumerate(rounds):
        # Collect votes based on initial_votes for the nodes participating in this round.
        votes = [initial_votes[p - 1] for p in nodes]
        # Compute the decision based solely on votes: "Commit" if all votes are "Commit"; otherwise "Abort".
        computed_decision = "Commit" if all(vote == "Commit" for vote in votes) else "Abort"
        # Use the provided coordinator decision to override if it is "Abort".
        provided_decision = coordinator_decision[i] if i < len(coordinator_decision) else "Commit"
        round_decision = "Commit" if (computed_decision == "Commit" and provided_decision == "Commit") else "Abort"
        # For each participating node, update its final state if it is not already Aborted.
        for p in nodes:
            if final_state[p - 1] != "Abort":
                final_state[p - 1] = round_decision
    return final_state