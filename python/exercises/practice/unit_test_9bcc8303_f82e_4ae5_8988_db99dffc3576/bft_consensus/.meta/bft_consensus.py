def bft_consensus(n, f, proposer_id, node_id, proposed_value, received_values):
    # Convert received votes: valid votes (0 or 1) are kept,
    # invalid values (None or anything else) are treated as default vote 0.
    votes = []
    for vote in received_values:
        if vote in (0, 1):
            votes.append(vote)
        else:
            votes.append(0)

    # Count the votes for 0 and 1.
    count0 = votes.count(0)
    count1 = votes.count(1)

    # Calculate the threshold as more than (2*n + f)/3.
    # Because votes are integer, we compute the minimum integer greater than (2*n+f)/3.
    threshold = (2 * n + f) // 3 + 1

    if count0 >= threshold:
        return 0
    elif count1 >= threshold:
        return 1
    else:
        return None