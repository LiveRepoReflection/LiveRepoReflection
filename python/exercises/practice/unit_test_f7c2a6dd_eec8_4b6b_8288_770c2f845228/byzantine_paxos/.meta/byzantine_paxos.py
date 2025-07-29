from .node import Node

class ByzantinePaxosSimulator:
    def __init__(self, n, f, proposals, byzantine_nodes):
        if n != 3 * f + 1:
            raise ValueError("n must equal 3f + 1 for Byzantine fault tolerance")
        
        self.n = n
        self.f = f
        self.proposals = proposals
        self.byzantine_nodes = byzantine_nodes
        self.nodes = []
        
        # Initialize nodes
        for node_id in range(n):
            is_byzantine = node_id in byzantine_nodes
            node = Node(node_id, is_byzantine)
            node_proposals = [proposals[node_id][i] for i in range(len(proposals[0]))]
            node.set_proposals(node_proposals)
            self.nodes.append(node)

    def run(self):
        num_slots = len(self.proposals[0])
        
        for slot in range(num_slots):
            for node in self.nodes:
                node.process_slot(slot, self.nodes)
        
        # Collect commitments from all nodes
        commitments = []
        for node in self.nodes:
            commitments.append(node.commitments)
        
        return commitments