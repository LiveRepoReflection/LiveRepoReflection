import random

def paxos_simulation(N, proposals, failure_rate, message_loss_rate):
    # Initialize acceptor states and node statuses (active or failed)
    acceptors = {}
    node_status = {}
    for i in range(N):
        if random.random() < failure_rate:
            node_status[i] = False
        else:
            node_status[i] = True
        acceptors[i] = {'promised': 0, 'accepted': None}

    majority = (N // 2) + 1
    next_proposal_number = 1

    for proposer_id, original_value in proposals:
        current_proposal_number = next_proposal_number
        next_proposal_number += 1

        # Phase 1: Prepare Phase
        responses = []
        for i in range(N):
            if not node_status[i]:
                continue
            if random.random() < message_loss_rate:
                continue
            if current_proposal_number > acceptors[i]['promised']:
                acceptors[i]['promised'] = current_proposal_number
                responses.append((i, acceptors[i]['accepted']))
        if len(responses) < majority:
            continue

        # Phase 2: Accept Phase
        highest_accepted_proposal = 0
        chosen_value = original_value
        for node_id, accepted in responses:
            if accepted is not None:
                accepted_proposal, accepted_value = accepted
                if accepted_proposal > highest_accepted_proposal:
                    highest_accepted_proposal = accepted_proposal
                    chosen_value = accepted_value
        accepted_count = 0
        for i in range(N):
            if not node_status[i]:
                continue
            if random.random() < message_loss_rate:
                continue
            if current_proposal_number >= acceptors[i]['promised']:
                acceptors[i]['promised'] = current_proposal_number
                acceptors[i]['accepted'] = (current_proposal_number, chosen_value)
                accepted_count += 1
        if accepted_count >= majority:
            return chosen_value

    return None