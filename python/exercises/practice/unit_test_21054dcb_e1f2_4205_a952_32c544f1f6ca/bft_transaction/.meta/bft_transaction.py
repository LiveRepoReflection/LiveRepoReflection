import random

class DTMNode:
    def __init__(self, node_id, is_faulty=False):
        self.node_id = node_id
        self.is_faulty = is_faulty

    def vote(self, tx_id, data):
        # Honest nodes always vote "commit" when services prepare successfully.
        # Faulty nodes vote arbitrarily.
        if not self.is_faulty:
            return "commit"
        else:
            return random.choice(["commit", "abort"])

class TransactionManager:
    def __init__(self, num_nodes, fault_tolerance, services):
        self.num_nodes = num_nodes
        self.fault_tolerance = fault_tolerance
        self.services = services
        self.nodes = [DTMNode(node_id=i) for i in range(num_nodes)]

    def start_transaction(self, tx_id, data):
        # Phase 1: Preparation - ask all services to prepare.
        prepare_success = True
        for service in self.services:
            if not service.prepare(tx_id, data):
                prepare_success = False
                break

        if not prepare_success:
            # Abort the transaction if any service fails to prepare.
            for service in self.services:
                service.abort(tx_id)
            return "abort"

        # Phase 2: Consensus - nodes vote on whether to commit.
        votes = []
        for node in self.nodes:
            vote = node.vote(tx_id, data)
            votes.append(vote)

        commit_votes = votes.count("commit")
        # For safety in BFT, require at least (num_nodes - fault_tolerance) commit votes.
        if commit_votes >= (self.num_nodes - self.fault_tolerance):
            consensus = "commit"
        else:
            consensus = "abort"

        # Phase 3: Finalization - apply the decision to all services.
        if consensus == "commit":
            for service in self.services:
                service.commit(tx_id, data)
        else:
            for service in self.services:
                service.abort(tx_id)

        return consensus