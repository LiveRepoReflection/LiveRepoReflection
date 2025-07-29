import random

def simulate_consensus(N, neighbors, initial_values, max_rounds, message_loss_probability):
    # Initialize each node's current value and promised round (initially set to -1)
    current_values = list(initial_values)
    promised_round = [-1] * N

    for r in range(max_rounds):
        # Phase 1: Propose
        # Each node sends its proposal (node id, round, current value) to each neighbor.
        # Messages might be lost. We'll collect proposals received by each node.
        proposals_received = {j: [] for j in range(N)}
        for proposer in range(N):
            for neighbor in neighbors[proposer]:
                if random.random() > message_loss_probability:
                    # Append proposal: tuple (proposer, round, proposed_value)
                    proposals_received[neighbor].append((proposer, r, current_values[proposer]))
        
        # Phase 2: Promise
        # Each node processes proposals received for this round in random order.
        # It promises at most one proposal with a round number strictly greater than what it has seen.
        promises_sent = {i: [] for i in range(N)}  # mapping proposer -> list of promise messages received
        for node in range(N):
            random.shuffle(proposals_received[node])
            promised = False
            for (proposer, round_num, proposed_value) in proposals_received[node]:
                if not promised and round_num > promised_round[node]:
                    # Update promised round and send promise back to proposer if message not lost.
                    promised_round[node] = round_num
                    promised = True
                    if random.random() > message_loss_probability:
                        promises_sent[proposer].append((node, round_num))  # storing the responder and round
                # If already promised in this round or round_num is not higher, we ignore (simulate rejection).
        
        # Phase 3: Accept
        # Each node that proposed will check if it received promises from a majority of its neighbors.
        # For a node with k neighbors, need more than k/2 promises.
        accept_messages = {j: [] for j in range(N)}
        for proposer in range(N):
            total_neighbors = len(neighbors[proposer])
            if total_neighbors == 0:
                # In case of isolated node, skip accept phase.
                continue
            # Check if majority of neighbors sent a promise.
            if len(promises_sent[proposer]) > total_neighbors // 2:
                # Send accept message to all neighbors with its proposed value.
                for neighbor in neighbors[proposer]:
                    if random.random() > message_loss_probability:
                        accept_messages[neighbor].append((proposer, r, current_values[proposer]))
        
        # Phase 4: Learn
        # Each node that receives one or more accept messages adopts the first one it receives.
        for node in range(N):
            if accept_messages[node]:
                # The first accept message is taken; if many, we break ties by order of message arrival.
                # We do not randomize order here to simulate a stable tie-break; using the order in accept_messages list.
                proposer, round_num, accepted_value = accept_messages[node][0]
                current_values[node] = accepted_value

    return current_values