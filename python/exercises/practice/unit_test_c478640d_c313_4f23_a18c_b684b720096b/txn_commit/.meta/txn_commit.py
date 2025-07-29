import time

TIMEOUT_THRESHOLD = 2  # seconds

class NodeState:
    def __init__(self):
        self.status = "active"  # active or failed
        self.delay = 0  # artificial network delay in seconds
        self.log = []  # persistent log for recording transaction actions

class TransactionProcessor:
    def __init__(self):
        # All nodes are stored in a dictionary with node_id as key and NodeState as value.
        self.nodes = {}

    def _ensure_node(self, node_id):
        if node_id not in self.nodes:
            self.nodes[node_id] = NodeState()

    def simulate_failure(self, node_id):
        self._ensure_node(node_id)
        self.nodes[node_id].status = "failed"

    def recover_node(self, node_id):
        self._ensure_node(node_id)
        self.nodes[node_id].status = "active"
        self.nodes[node_id].delay = 0

    def simulate_delay(self, node_id, delay):
        self._ensure_node(node_id)
        self.nodes[node_id].delay = delay

    def process_transaction(self, transaction):
        # Extract transaction details
        coordinator = transaction.get("coordinator")
        participants = transaction.get("participants", [])
        txn_id = transaction.get("txn_id")
        data = transaction.get("data")

        # Determine all involved nodes
        involved_nodes = [coordinator] + participants
        for node_id in involved_nodes:
            self._ensure_node(node_id)

        votes = {}
        decision = "COMMIT"

        # Phase 1: Prepare Phase
        # Coordinator automatically votes YES if active, otherwise NO.
        coord_state = self.nodes[coordinator]
        if coord_state.status != "active":
            votes[coordinator] = "NO"
        else:
            # Simulate coordinator's delay
            if coord_state.delay >= TIMEOUT_THRESHOLD:
                votes[coordinator] = "NO"
            else:
                if coord_state.delay > 0:
                    time.sleep(coord_state.delay)
                votes[coordinator] = "YES"
                coord_state.log.append(f"{txn_id}: PREPARED")

        # Participants prepare vote
        for node_id in participants:
            state = self.nodes[node_id]
            if state.status != "active":
                votes[node_id] = "NO"
                continue
            # Simulate network delay
            if state.delay >= TIMEOUT_THRESHOLD:
                # Simulate timeout: node does not respond in time.
                votes[node_id] = "NO"
            else:
                if state.delay > 0:
                    time.sleep(state.delay)
                votes[node_id] = "YES"
                state.log.append(f"{txn_id}: PREPARED")

        # Evaluate votes. If any vote is not "YES", decision becomes ABORT.
        for vote in votes.values():
            if vote != "YES":
                decision = "ABORT"
                break

        # Phase 2: Commit Phase
        for node_id in involved_nodes:
            state = self.nodes[node_id]
            # Even if a node is failed, we simulate that its final outcome becomes ABORT.
            if state.status == "active":
                state.log.append(f"{txn_id}: {decision}")
            # For failed nodes, we do not append to the log, but the outcome is considered ABORT.
        
        # Return final outcome mapping for each node.
        outcome = {}
        for node_id in involved_nodes:
            # If node is active, outcome is based on what was decided.
            # If node is failed, outcome is automatically ABORT.
            if self.nodes[node_id].status != "active":
                outcome[node_id] = "ABORT"
            else:
                outcome[node_id] = decision
        return outcome