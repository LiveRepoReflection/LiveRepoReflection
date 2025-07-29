import math
import random

class Node:
    def __init__(self, node_id, N, proposal_value):
        self.node_id = node_id
        self.N = N
        self.proposal_value = proposal_value  # initial value proposed by this node, may be None
        self.queue = []
        self.promised = -1  # highest proposal number promised
        self.accepted = None  # tuple: (proposal_number, value)
        self.learned = None  # final consensus value once learned
        # For proposer state if this node initiates a proposal
        # current_proposal is a dict containing:
        #   'proposal_number': unique proposal number,
        #   'value': candidate value,
        #   'phase': either "prepare" or "accept",
        #   'promises': list of promise messages received.
        self.current_proposal = None
        # For learner state: count accepted messages for proposals
        # mapping (proposal_number, value) -> count
        self.accepted_counts = {}

    def initiate_proposal(self, send_message):
        # Initiate a new proposal if not already done and if this node has a proposal_value.
        if self.proposal_value is None or self.current_proposal is not None:
            return
        # Using a simple proposal number scheme: round is initially 1.
        # Proposal number = round * N + node_id. Since round starts from 1, guarantees > 0.
        round_number = 1
        proposal_number = round_number * self.N + self.node_id
        self.current_proposal = {
            'proposal_number': proposal_number,
            'value': self.proposal_value,
            'phase': 'prepare',
            'promises': []
        }
        # Broadcast Prepare message to all nodes including itself.
        message = {
            'sender': self.node_id,
            'type': 'Prepare',
            'proposal_number': proposal_number
        }
        for receiver in range(self.N):
            send_message(receiver, message)

    def process_message(self, msg, send_message):
        msg_type = msg.get('type')
        
        # Process Prepare message: as an acceptor
        if msg_type == 'Prepare':
            incoming_proposal = msg.get('proposal_number')
            if incoming_proposal > self.promised:
                self.promised = incoming_proposal
                # Send Promise message back, including any accepted proposal if exists.
                promise_msg = {
                    'sender': self.node_id,
                    'type': 'Promise',
                    'proposal_number': incoming_proposal,
                    'accepted_number': self.accepted[0] if self.accepted is not None else None,
                    'accepted_value': self.accepted[1] if self.accepted is not None else None
                }
                send_message(msg['sender'], promise_msg)
            # else ignore the prepare message

        # Process Promise message: for a proposer waiting on promises
        elif msg_type == 'Promise':
            # Only process if this node is the proposer for the proposal_number.
            if self.current_proposal is None:
                return
            # Check if the promise is for the current proposal
            if msg.get('proposal_number') != self.current_proposal['proposal_number']:
                return
            # Append the promise if not already received from this sender
            sender = msg.get('sender')
            if sender not in [p.get('sender') for p in self.current_proposal['promises']]:
                self.current_proposal['promises'].append(msg)
            # If a promised message carries an accepted proposal, update candidate value if higher accepted number.
            accepted_num = msg.get('accepted_number')
            accepted_val = msg.get('accepted_value')
            if accepted_num is not None:
                # Check if the current candidate value should be replaced by a higher proposal from promises.
                # We choose the value from the promise with the highest accepted_number.
                # Compare with any previous accepted proposal stored in current_proposal.
                current_acc = self.current_proposal.get('promised_accepted_number', -1)
                if accepted_num > current_acc:
                    self.current_proposal['promised_accepted_number'] = accepted_num
                    self.current_proposal['value'] = accepted_val
            # Check if majority promises received.
            if len(self.current_proposal['promises']) >= (self.N // 2) + 1 and self.current_proposal['phase'] == 'prepare':
                # Move to Accept phase: broadcast Accept message to all nodes.
                self.current_proposal['phase'] = 'accept'
                accept_msg = {
                    'sender': self.node_id,
                    'type': 'Accept',
                    'proposal_number': self.current_proposal['proposal_number'],
                    'value': self.current_proposal['value']
                }
                for receiver in range(self.N):
                    send_message(receiver, accept_msg)

        # Process Accept message: as an acceptor
        elif msg_type == 'Accept':
            incoming_proposal = msg.get('proposal_number')
            value = msg.get('value')
            if incoming_proposal >= self.promised:
                self.promised = incoming_proposal
                self.accepted = (incoming_proposal, value)
                # Broadcast Accepted message to all nodes.
                accepted_msg = {
                    'sender': self.node_id,
                    'type': 'Accepted',
                    'proposal_number': incoming_proposal,
                    'value': value
                }
                for receiver in range(self.N):
                    send_message(receiver, accepted_msg)
            # Else, ignore the Accept message.

        # Process Accepted message: as a learner
        elif msg_type == 'Accepted':
            proposal_number = msg.get('proposal_number')
            value = msg.get('value')
            key = (proposal_number, value)
            self.accepted_counts[key] = self.accepted_counts.get(key, 0) + 1
            if self.accepted_counts[key] >= (self.N // 2) + 1 and self.learned is None:
                # Learn the value only once when majority is reached.
                self.learned = value

    def process_queue(self, send_message):
        # Process all messages currently in the queue.
        while self.queue:
            msg = self.queue.pop(0)
            self.process_message(msg, send_message)

def simulate_paxos(N, F, proposals, max_steps):
    # Create nodes. If there are fewer proposals than nodes, missing proposals become None.
    nodes = {}
    for i in range(N):
        proposal = proposals[i] if i < len(proposals) else None
        nodes[i] = Node(i, N, proposal)

    # Helper function to simulate message sending:
    # Given a dictionary next_queues mapping node id to list, add message to receiver's queue.
    def send_message_func(receiver, message):
        # Simulate asynchronous delivery: message can be delayed randomly.
        # For simplicity, we add a random chance of dropping messages to mimic message loss.
        # However, to ensure progress, we keep a high delivery probability.
        drop_probability = 0.05  # 5% chance to drop message
        if random.random() < drop_probability:
            return
        # Deep copy is not needed since messages are simple dicts.
        next_queues[receiver].append(message.copy())

    # Initialize message queues dictionary.
    current_queues = {i: [] for i in range(N)}
    # If N==0, return empty dictionary.
    if N == 0:
        return {}

    # At time step 0, have each node that has a proposal initiate its proposal.
    next_queues = {i: [] for i in range(N)}
    for node in nodes.values():
        node.initiate_proposal(send_message_func)
    # Merge next_queues into nodes' queues.
    for i in range(N):
        nodes[i].queue.extend(next_queues[i])

    # Main simulation loop.
    for step in range(max_steps):
        # Prepare next round queues
        next_queues = {i: [] for i in range(N)}
        # Each node processes its current message queue.
        for node in nodes.values():
            node.process_queue(send_message_func)
            # Additionally, if a node has not yet initiated proposal but has a proposal value,
            # we allow them to attempt a proposal in future rounds if no progress.
            if node.current_proposal is None and node.proposal_value is not None:
                # Re-initiate proposal with a new higher round number.
                # The new round number is chosen randomly between 2 and 10 to simulate retries.
                round_number = random.randint(2, 10)
                proposal_number = round_number * N + node.node_id
                node.current_proposal = {
                    'proposal_number': proposal_number,
                    'value': node.proposal_value,
                    'phase': 'prepare',
                    'promises': []
                }
                prepare_msg = {
                    'sender': node.node_id,
                    'type': 'Prepare',
                    'proposal_number': proposal_number
                }
                for receiver in range(N):
                    send_message_func(receiver, prepare_msg)
        # If all non-faulty nodes have learned a value, we can end early.
        learned_values = [node.learned for node in nodes.values() if node.proposal_value is not None]
        if learned_values and all(val is not None for val in learned_values):
            break
        # Assign next_queues to nodes for next step.
        for i in range(N):
            nodes[i].queue.extend(next_queues[i])
    # Build final result: mapping node id to learned consensus value or None.
    result = {}
    for i in range(N):
        result[i] = nodes[i].learned
    return result