def byzantine_agreement(N, F, V, delay_matrix, R, faulty_nodes):
    # Initialize mailbox for each node as a dict: round -> list of received values.
    mailbox = {i: {} for i in range(N)}
    # For non-faulty commander, assume initial self-value at round 0.
    # Even if commander is faulty, we use its initial value as its own decision though its outgoing messages may be arbitrary.
    mailbox[0][0] = [V]

    # Initialize events dictionary: key = delivery time (round), value = list of events.
    # Each event is a tuple: (receiver, sender, value, sending_round)
    events = {}

    def schedule_event(delivery_time, receiver, sender, value, sending_round):
        if delivery_time > R:
            return
        if delivery_time not in events:
            events[delivery_time] = []
        events[delivery_time].append((receiver, sender, value, sending_round))

    # Round 0: Commander sends its value to every other node.
    # Determine message value based on whether the sender (commander, node 0) is faulty.
    for j in range(N):
        if j == 0:
            continue
        # For a non-faulty sender, send the actual value V.
        # For a faulty sender, send an arbitrary (potentially inconsistent) value.
        if 0 in faulty_nodes:
            send_value = (0 + j) % 2
        else:
            send_value = V
        delivery_time = 0 + delay_matrix[0][j]
        schedule_event(delivery_time, j, 0, send_value, 0)

    # Simulate rounds 1 to R-1.
    for current_round in range(1, R):
        # Process events scheduled for this round.
        if current_round in events:
            for receiver, sender, value, sending_round in events[current_round]:
                if current_round not in mailbox[receiver]:
                    mailbox[receiver][current_round] = []
                mailbox[receiver][current_round].append(value)
        # For each node, relay messages received in the previous round (current_round - 1).
        for i in range(N):
            if current_round - 1 not in mailbox[i]:
                continue
            # For each message received in the previous round, forward it to every other node.
            for msg in mailbox[i][current_round - 1]:
                for j in range(N):
                    if j == i:
                        continue
                    # Determine outgoing value.
                    if i in faulty_nodes:
                        forward_value = (i + j) % 2
                    else:
                        forward_value = msg
                    delivery_time = current_round + delay_matrix[i][j]
                    schedule_event(delivery_time, j, i, forward_value, current_round)
    # Process events that are scheduled exactly at time R.
    if R in events:
        for receiver, sender, value, sending_round in events[R]:
            if R not in mailbox[receiver]:
                mailbox[receiver][R] = []
            mailbox[receiver][R].append(value)

    # For each node, decide on a final value based on messages received by time R.
    # Non-faulty nodes use the majority of received values; tie defaults to 0.
    decisions = [0] * N
    for i in range(N):
        if i in faulty_nodes:
            # Faulty nodes can return any value; here we choose an arbitrary one.
            decisions[i] = i % 2
        else:
            # Collect all messages received in any round up to and including R.
            received = []
            for round_no in mailbox[i]:
                received.extend(mailbox[i][round_no])
            if not received:
                decisions[i] = 0
            else:
                count0 = received.count(0)
                count1 = received.count(1)
                if count1 > count0:
                    decisions[i] = 1
                elif count0 > count1:
                    decisions[i] = 0
                else:
                    decisions[i] = 0
    return decisions