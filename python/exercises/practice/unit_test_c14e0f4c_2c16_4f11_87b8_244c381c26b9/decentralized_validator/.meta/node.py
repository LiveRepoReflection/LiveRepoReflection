import hashlib
import random

class Node:
    def __init__(self, node_id, computational_power, network_size):
        self.node_id = node_id
        self.computational_power = computational_power
        self.network_size = network_size
        self.global_state = ""
        self.validation_error_prob = 1 / (computational_power * 2)

    def propose_transaction(self, transaction_content):
        return transaction_content

    def validate_transaction(self, transaction_content, current_global_state):
        # Simulate potential validation error based on computational power
        if random.random() < self.validation_error_prob:
            return not self._is_valid_transition(transaction_content, current_global_state)
        return self._is_valid_transition(transaction_content, current_global_state)

    def _is_valid_transition(self, transaction_content, current_global_state):
        # All transitions are considered valid in this simplified model
        # In a real system, this would check transaction semantics
        return True

    def commit_transaction(self, transaction_content, validation_results):
        total_weight = 0
        positive_weight = 0
        
        for node_id, is_valid in validation_results.items():
            # In a real system, we would look up each node's computational power
            # For simplicity, we assume all nodes have equal weight here
            weight = 1
            total_weight += weight
            if is_valid:
                positive_weight += weight

        if positive_weight > total_weight / 2:
            self.global_state = hashlib.sha256(
                (self.global_state + transaction_content).encode()
            ).hexdigest()
            return True
        return False

    def get_global_state(self):
        return self.global_state