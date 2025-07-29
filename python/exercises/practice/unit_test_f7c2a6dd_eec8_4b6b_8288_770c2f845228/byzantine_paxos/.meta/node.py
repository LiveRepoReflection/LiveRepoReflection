from collections import defaultdict
from .message import Message
from .constants import MessageType

class Node:
    def __init__(self, node_id, is_byzantine=False):
        self.node_id = node_id
        self.is_byzantine = is_byzantine
        self.proposals = []
        self.commitments = []
        self.received_messages = defaultdict(list)
        self.accepted_values = {}

    def set_proposals(self, proposals):
        self.proposals = proposals
        self.commitments = [None] * len(proposals)

    def send_message(self, message_type, slot, value, nodes):
        if self.is_byzantine:
            # Byzantine nodes may send corrupted messages
            if slot % 2 == 0:
                value = -1  # Corrupt the value
            message = Message(self.node_id, message_type, slot, value)
        else:
            message = Message(self.node_id, message_type, slot, value)
        
        for node in nodes:
            if node.node_id != self.node_id:
                node.receive_message(message)

    def receive_message(self, message):
        self.received_messages[message.slot].append(message)

    def process_slot(self, slot, nodes):
        if slot >= len(self.proposals):
            return

        # Phase 1: Prepare
        self.send_message(MessageType.PREPARE, slot, self.proposals[slot], nodes)

        # Phase 2: Accept
        prepare_messages = [m for m in self.received_messages[slot] 
                          if m.type == MessageType.PREPARE]
        
        if len(prepare_messages) >= len(nodes) // 2 + 1:
            # Select value from lowest node ID
            selected_value = min(prepare_messages, key=lambda m: m.sender).value
            self.send_message(MessageType.ACCEPT, slot, selected_value, nodes)

        # Phase 3: Commit
        accept_messages = [m for m in self.received_messages[slot] 
                         if m.type == MessageType.ACCEPT]
        
        if len(accept_messages) >= len(nodes) // 2 + 1:
            # Check if majority accepted same value
            values = [m.value for m in accept_messages]
            if all(v == values[0] for v in values):
                self.commitments[slot] = values[0]