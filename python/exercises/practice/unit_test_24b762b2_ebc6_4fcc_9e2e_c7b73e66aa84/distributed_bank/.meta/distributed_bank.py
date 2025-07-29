import copy

class Node:
    def __init__(self, node_id, balances):
        self.node_id = node_id
        self.balances = copy.deepcopy(balances)
        self.state = 'alive'  # can be 'alive', 'fail', or 'partition'
        self.logs = []

    def prepare_transaction(self, transaction, role):
        if self.state != 'alive':
            return False
        # For the source node, check funds
        if role == 'source':
            account = transaction["from_account"]
            if account not in self.balances or self.balances[account] < transaction["amount"]:
                return False
        self.logs.append(f"prepared {transaction}")
        return True

    def commit_transaction(self, transaction, node_distribution):
        if self.state != 'alive':
            return False
        # In commit phase, modify balances based on role (if this node holds the involved account)
        if self.node_id == node_distribution[transaction["from_account"]]:
            account = transaction["from_account"]
            self.balances[account] -= transaction["amount"]
        if self.node_id == node_distribution[transaction["to_account"]]:
            account = transaction["to_account"]
            # If destination account does not exist, initialize it to 0
            self.balances[account] = self.balances.get(account, 0) + transaction["amount"]
        self.logs.append(f"committed {transaction}")
        return True

def simulate_transactions(num_nodes, transactions, node_distribution, initial_balances, failure_events):
    # Create nodes using the initial_balances given for each node; if a node has no account, use an empty dict.
    nodes = {}
    for node_id in range(num_nodes):
        node_bal = initial_balances.get(node_id, {})
        nodes[node_id] = Node(node_id, node_bal)

    # Sort failure events by time (ascending)
    failure_events_sorted = sorted(failure_events, key=lambda x: x[0])
    event_index = 0
    current_time = 1

    # Make a deep copy of the initial balances to restore in case of failure.
    initial_state_copy = copy.deepcopy(initial_balances)

    # Process each transaction sequentially
    for txn in transactions:
        # Process all failure events scheduled at the current time
        while event_index < len(failure_events_sorted) and failure_events_sorted[event_index][0] == current_time:
            time, event_type, node_id = failure_events_sorted[event_index]
            # Mark node as failed or partitioned. Treat both as non-responsive.
            if event_type in ("fail", "partition"):
                nodes[node_id].state = event_type
                nodes[node_id].logs.append(f"{event_type} at time {time}")
            event_index += 1

        # Identify the source and destination nodes for the current transaction.
        source_id = node_distribution.get(txn["from_account"])
        dest_id = node_distribution.get(txn["to_account"])
        if source_id is None or dest_id is None:
            # If account mapping is missing, rollback simulation.
            return (False, initial_state_copy)

        source_node = nodes[source_id]
        dest_node = nodes[dest_id]

        # Prepare Phase: Both nodes must be alive and prepared.
        if not source_node.prepare_transaction(txn, 'source'):
            return (False, initial_state_copy)
        if not dest_node.prepare_transaction(txn, 'destination'):
            return (False, initial_state_copy)

        # Commit Phase: Both nodes commit the transaction.
        # In a true 2PC these would be done atomically. Here, if any commit fails, we rollback.
        commit_success_source = source_node.commit_transaction(txn, node_distribution)
        commit_success_dest = dest_node.commit_transaction(txn, node_distribution)
        if not (commit_success_source and commit_success_dest):
            return (False, initial_state_copy)

        current_time += 1

    # Build the final state from each node.
    final_state = {}
    for node_id, node in nodes.items():
        final_state[node_id] = copy.deepcopy(node.balances)

    return (True, final_state)