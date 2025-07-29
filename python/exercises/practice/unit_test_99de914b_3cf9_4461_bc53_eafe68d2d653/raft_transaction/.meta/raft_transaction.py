class TransactionSimulator:
    def __init__(self, num_nodes: int):
        """Initialize the distributed transaction simulator with num_nodes nodes.
        
        Args:
            num_nodes: The number of nodes in the distributed system (odd number >= 3)
        """
        self.num_nodes = num_nodes
        self.leader_id = 0  # The node with the lowest ID is always the leader
        
        # Initialize the key-value store and log for each node
        self.nodes = []
        for _ in range(num_nodes):
            self.nodes.append({
                'data': {},  # Key-value store for this node
                'log': [],   # Transaction log for this node
            })
    
    def propose_transaction(self, leader_id: int, key: str, value: str) -> bool:
        """Simulate a transaction proposal.
        
        Args:
            leader_id: The ID of the node proposing the transaction
            key: The key to update/insert
            value: The value to set
            
        Returns:
            True if the transaction was successfully committed, False otherwise
        """
        # Check if the proposing node is the leader
        if leader_id != self.leader_id:
            # Non-leader nodes can't propose transactions
            # But we still add it to all logs to maintain consistency
            transaction = {'key': key, 'value': value}
            for node in self.nodes:
                node['log'].append(transaction)
            return False
        
        # Step 1: Leader appends the transaction to its log
        transaction = {'key': key, 'value': value}
        self.nodes[leader_id]['log'].append(transaction)
        
        # Step 2: Leader sends the transaction to all followers (log replication)
        # and Step 3: Followers append to their logs and send ACKs back
        acks = 1  # Leader counts as 1 ACK
        
        # Simulate sending to all followers and getting ACKs
        for node_id in range(self.num_nodes):
            if node_id != leader_id:
                # Follower appends to its log
                self.nodes[node_id]['log'].append(transaction)
                # Follower acknowledges
                acks += 1
        
        # Step 4: Leader waits for majority of ACKs
        majority = (self.num_nodes // 2) + 1
        if acks < majority:
            return False  # Not enough acknowledgments
        
        # Step 5: Leader commits the transaction and informs followers
        # Step 6: All nodes apply the transaction to their key-value stores
        for node_id in range(self.num_nodes):
            self.nodes[node_id]['data'][key] = value
        
        return True
    
    def get_node_data(self, node_id: int) -> dict:
        """Get the key-value store of a specific node.
        
        Args:
            node_id: The ID of the node to query
            
        Returns:
            A dictionary representing the key-value store of the node
        """
        return self.nodes[node_id]['data'].copy()
    
    def get_node_log(self, node_id: int) -> list:
        """Get the transaction log of a specific node.
        
        Args:
            node_id: The ID of the node to query
            
        Returns:
            A list representing the transaction log of the node
        """
        return self.nodes[node_id]['log'].copy()