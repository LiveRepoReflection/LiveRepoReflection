import bisect

class Transaction:
    def __init__(self, id, operations):
        self.id = id
        self.operations = operations

class Operation:
    def __init__(self, type, key, shard_id, estimated_duration, transaction_id):
        self.type = type
        self.key = key
        self.shard_id = shard_id
        self.estimated_duration = estimated_duration
        self.transaction_id = transaction_id

class Shard:
    def __init__(self, processing_capacity):
        self.processing_capacity = processing_capacity

def schedule_transactions(transactions, shard_map):
    # Initialize per-transaction pointer and ready time for the next operation.
    txn_pointer = {txn.id: 0 for txn in transactions}
    txn_ready_time = {txn.id: 0 for txn in transactions}

    # Build a lookup for transactions by id.
    txn_lookup = {txn.id: txn for txn in transactions}

    # For each shard, maintain a timeline: a sorted list of events (time, delta).
    # For an event (t, delta), if t is a start time (delta=+1) it adds to active count,
    # if t is finish time (delta=-1) it reduces active count.
    shard_timelines = {shard_id: [] for shard_id in shard_map}

    # For each key, track the finish time of the last operation scheduled from a different transaction.
    key_last_finish = {}

    schedule = []  # list of tuples (timestamp, transaction_id, shard_id)

    # Helper function: Given a shard's timeline (list of (time, delta)), a candidate start time,
    # and the capacity, compute the earliest time >= candidate when active count < capacity.
    def get_earliest_shard_time(timeline, candidate, capacity):
        # Compute active count at candidate time: include events with time < candidate.
        # timeline is sorted by time, with finishing events (-1) properly placed if same timestamp.
        active = 0
        for t, delta in timeline:
            if t < candidate:
                active += delta
            else:
                break
        # If active is less than capacity, candidate is valid.
        # Otherwise, iterate over events to find next time when capacity might free up.
        if active < capacity:
            return candidate

        # Iterate over timeline events to update active count and find a slot.
        # Because candidate might fall into an interval with full capacity.
        sorted_events = timeline[:]  # already sorted
        # We start at candidate, then simulate events moving forward.
        current_time = candidate
        for time, delta in sorted_events:
            if time < current_time:
                continue
            # Move current time to the event time.
            current_time = time
            active += delta
            if active < capacity:
                return current_time
        # No events free up capacity, so return current_time.
        return current_time

    # Main loop: continue until all transactions have scheduled all their operations.
    pending = True
    while pending:
        candidate_ops = []
        # For each transaction that has pending operations.
        for txn_id in txn_pointer:
            txn = txn_lookup[txn_id]
            ptr = txn_pointer[txn_id]
            if ptr >= len(txn.operations):
                continue  # all operations scheduled for this transaction
            op = txn.operations[ptr]
            base_time = txn_ready_time[txn_id]
            # For conflict serializability: ensure that if another transaction has done a conflicting op
            # on the same key, then start time must be after that op's finish time.
            key = op.key
            conflict_time = 0
            if key in key_last_finish:
                # If the last operation on this key was from a different transaction, enforce ordering.
                last_txn_id, last_finish = key_last_finish[key]
                if last_txn_id != txn_id:
                    conflict_time = last_finish
            candidate_start = max(base_time, conflict_time)
            # Check shard availability.
            shard_id = op.shard_id
            capacity = shard_map[shard_id].processing_capacity
            timeline = shard_timelines[shard_id]
            estimated_start = get_earliest_shard_time(timeline, candidate_start, capacity)
            candidate_finish = estimated_start + op.estimated_duration
            candidate_ops.append((estimated_start, candidate_finish, txn_id, op, shard_id))
        if not candidate_ops:
            pending = False
            break

        # Choose the operation with the smallest estimated start time (tie-breaker: lower txn id).
        candidate_ops.sort(key=lambda x: (x[0], x[2]))
        best_start, best_finish, best_txn_id, best_op, best_shard_id = candidate_ops[0]

        # Schedule this operation.
        schedule.append((best_start, best_txn_id, best_shard_id))
        # Update the transaction ready time to the finish time of this operation.
        txn_ready_time[best_txn_id] = best_finish

        # Update key_last_finish for conflict serializability.
        # For the same key, if the previous operation was from another transaction, we record this op.
        # If it's the same transaction, we still update the finish time.
        key_last_finish[best_op.key] = (best_txn_id, best_finish)

        # Update the shard timeline: add start and finish events.
        timeline = shard_timelines[best_shard_id]
        bisect.insort(timeline, (best_start, +1))
        bisect.insort(timeline, (best_finish, -1))
        shard_timelines[best_shard_id] = timeline

        # Advance the pointer for the transaction.
        txn_pointer[best_txn_id] += 1

    # Return the schedule sorted by timestamp.
    schedule.sort(key=lambda x: x[0])
    return schedule