import random

message_queue = []
MSG_LOSS_PROB = 0.0

def send_message(sender, receiver, msg_type, proposal_number, value, extra=None):
    global message_queue, MSG_LOSS_PROB
    if random.random() < MSG_LOSS_PROB:
        return
    msg = {"sender": sender, "receiver": receiver, "type": msg_type, "proposal_number": proposal_number, "value": value}
    if extra is not None:
        msg.update(extra)
    message_queue.append(msg)

class Node:
    def __init__(self, node_id, total_nodes):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.online = True
        self.promised_proposal = -1
        self.accepted_proposal = None
        self.initial_value = None
        self.current_proposal = None
        self.accepted_counts = {}

    def set_initial_proposal(self, value):
        self.initial_value = value

    def maybe_initiate_proposal(self):
        if self.initial_value is not None and self.current_proposal is None:
            self.proposal_counter = getattr(self, 'proposal_counter', 0) + 1
            proposal_number = self.proposal_counter * self.total_nodes + self.node_id
            self.current_proposal = {"proposal_number": proposal_number, "proposed_value": self.initial_value, "promises": []}
            for i in range(self.total_nodes):
                send_message(self.node_id, i, "prepare", proposal_number, None)

    def process_message(self, msg, nodes):
        if msg["type"] == "prepare":
            prop_num = msg["proposal_number"]
            if prop_num > self.promised_proposal:
                self.promised_proposal = prop_num
                extra = {}
                if self.accepted_proposal is not None:
                    extra["accepted_proposal"] = self.accepted_proposal
                else:
                    extra["accepted_proposal"] = None
                send_message(self.node_id, msg["sender"], "promise", prop_num, None, extra)
        elif msg["type"] == "promise":
            if self.current_proposal is not None and msg["proposal_number"] == self.current_proposal["proposal_number"]:
                self.current_proposal["promises"].append(msg)
                majority = (self.total_nodes // 2) + 1
                if len(self.current_proposal["promises"]) >= majority and not self.current_proposal.get("accept_sent", False):
                    selected_value = self.current_proposal["proposed_value"]
                    highest_accepted_number = -1
                    for promise in self.current_proposal["promises"]:
                        accepted = promise.get("accepted_proposal")
                        if accepted is not None and accepted[0] > highest_accepted_number:
                            highest_accepted_number = accepted[0]
                            selected_value = accepted[1]
                    self.current_proposal["chosen_value"] = selected_value
                    self.current_proposal["accept_sent"] = True
                    for i in range(self.total_nodes):
                        send_message(self.node_id, i, "accept", self.current_proposal["proposal_number"], selected_value)
        elif msg["type"] == "accept":
            prop_num = msg["proposal_number"]
            if prop_num >= self.promised_proposal:
                self.promised_proposal = prop_num
                self.accepted_proposal = (prop_num, msg["value"])
                send_message(self.node_id, msg["sender"], "accepted", prop_num, msg["value"])
                for i in range(self.total_nodes):
                    send_message(self.node_id, i, "accepted", prop_num, msg["value"])
        elif msg["type"] == "accepted":
            key = (msg["proposal_number"], msg["value"])
            self.accepted_counts[key] = self.accepted_counts.get(key, 0) + 1

    def check_consensus(self, total_nodes):
        majority = (total_nodes // 2) + 1
        for key, count in self.accepted_counts.items():
            if count >= majority:
                return key[1]
        return None

def simulate_paxos(n, proposals, message_loss_probability, failure_rate, recovery_rate, max_steps):
    global message_queue, MSG_LOSS_PROB
    MSG_LOSS_PROB = message_loss_probability
    message_queue = []
    nodes = [Node(i, n) for i in range(n)]
    for node_id, value in proposals:
        if 0 <= node_id < n:
            nodes[node_id].set_initial_proposal(value)
    step = 0
    while step < max_steps:
        step += 1
        for node in nodes:
            if node.online:
                if random.random() < failure_rate:
                    node.online = False
            else:
                if random.random() < recovery_rate:
                    node.online = True
        for node in nodes:
            if node.online:
                node.maybe_initiate_proposal()
        random.shuffle(message_queue)
        current_messages = message_queue.copy()
        message_queue.clear()
        for msg in current_messages:
            receiver = nodes[msg["receiver"]]
            if receiver.online:
                receiver.process_message(msg, nodes)
        for node in nodes:
            consensus = node.check_consensus(n)
            if consensus is not None:
                return consensus
    return "No Consensus"

if __name__ == "__main__":
    result = simulate_paxos(
        n=5,
        proposals=[(0, "value1"), (1, "value2")],
        message_loss_probability=0.1,
        failure_rate=0.05,
        recovery_rate=0.5,
        max_steps=500
    )
    print(result)