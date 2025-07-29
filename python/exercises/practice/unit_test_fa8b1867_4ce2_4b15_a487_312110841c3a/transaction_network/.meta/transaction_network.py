from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple

class TransactionValidator:
    def __init__(self, network_size: int, connections: List[Tuple[int, int]], 
                 transaction_proposals: Dict[int, List[Tuple[int, str, int, int]]], 
                 failed_nodes: Set[int]):
        self.network_size = network_size
        self.connections = connections
        self.transaction_proposals = transaction_proposals
        self.failed_nodes = failed_nodes
        self.adj_list = self._build_adjacency_list()
        self.visited = set()
        self.node_states = defaultdict(dict)

    def _build_adjacency_list(self) -> Dict[int, List[int]]:
        """Builds an adjacency list representation of the network."""
        adj_list = defaultdict(list)
        for u, v in self.connections:
            adj_list[u].append(v)
            adj_list[v].append(u)
        return adj_list

    def _is_network_connected(self) -> bool:
        """Verifies if all non-failed nodes are connected."""
        if not self.transaction_proposals:
            return True

        active_nodes = {node for node in range(self.network_size) 
                       if node not in self.failed_nodes}
        if not active_nodes:
            return False

        start_node = min(active_nodes)
        visited = set()

        def dfs(node: int) -> None:
            visited.add(node)
            for neighbor in self.adj_list[node]:
                if neighbor not in visited and neighbor not in self.failed_nodes:
                    dfs(neighbor)

        dfs(start_node)
        return visited == active_nodes

    def _validate_node_ids(self) -> bool:
        """Verifies that all node IDs in proposals are valid."""
        for node, proposals in self.transaction_proposals.items():
            if node >= self.network_size:
                return False
            for proposal in proposals:
                if proposal[0] >= self.network_size:
                    return False
        return True

    def _validate_local_consistency(self) -> bool:
        """Validates local consistency of transaction proposals."""
        node_modifications = defaultdict(list)
        
        # Group modifications by target node
        for node, proposals in self.transaction_proposals.items():
            if node in self.failed_nodes:
                continue
            for mod in proposals:
                node_modifications[mod[0]].append(mod)

        # Check for conflicts in modifications
        for node, mods in node_modifications.items():
            if node in self.failed_nodes:
                return False
            
            # Track modifications per key
            key_states = {}
            for mod in sorted(mods, key=lambda x: (x[1], x[2])):  # Sort by key and old_value
                _, key, old_value, new_value = mod
                if key in key_states:
                    if key_states[key] != old_value:
                        return False
                key_states[key] = new_value

        return True

    def _propagate_consensus(self) -> bool:
        """Implements a simple consensus protocol using BFS."""
        if not self.transaction_proposals:
            return True

        start_node = min(node for node in self.transaction_proposals.keys() 
                        if node not in self.failed_nodes)
        queue = deque([start_node])
        consensus = set([start_node])
        
        while queue:
            current = queue.popleft()
            
            for neighbor in self.adj_list[current]:
                if (neighbor not in consensus and 
                    neighbor not in self.failed_nodes and 
                    neighbor in self.transaction_proposals):
                    
                    # Check if neighbor's proposal is compatible
                    if not self._are_proposals_compatible(current, neighbor):
                        return False
                    
                    consensus.add(neighbor)
                    queue.append(neighbor)

        # Check if all non-failed nodes with proposals reached consensus
        active_proposing_nodes = {node for node in self.transaction_proposals 
                                if node not in self.failed_nodes}
        return consensus == active_proposing_nodes

    def _are_proposals_compatible(self, node1: int, node2: int) -> bool:
        """Checks if proposals from two nodes are compatible."""
        props1 = self.transaction_proposals[node1]
        props2 = self.transaction_proposals[node2]
        
        # Create a combined view of the modifications
        combined_view = {}
        
        for node_id, key, old_value, new_value in props1 + props2:
            if node_id in self.failed_nodes:
                return False
            
            if (key, node_id) in combined_view:
                existing = combined_view[(key, node_id)]
                if existing[0] != old_value or existing[1] != new_value:
                    return False
            else:
                combined_view[(key, node_id)] = (old_value, new_value)
                
        return True

    def validate(self) -> bool:
        """Main validation method that orchestrates the entire validation process."""
        # Basic validation checks
        if not self._validate_node_ids():
            return False
            
        if not self._is_network_connected():
            return False
            
        if not self._validate_local_consistency():
            return False
            
        # Consensus check
        if not self._propagate_consensus():
            return False
            
        return True


def is_transaction_consistent(network_size: int, 
                            connections: List[Tuple[int, int]],
                            transaction_proposals: Dict[int, List[Tuple[int, str, int, int]]],
                            failed_nodes: Set[int]) -> bool:
    """
    Main function to validate transaction consistency across the network.
    
    Args:
        network_size: Number of nodes in the network
        connections: List of bidirectional connections between nodes
        transaction_proposals: Dictionary of transaction proposals per node
        failed_nodes: Set of failed node IDs
    
    Returns:
        bool: True if the transaction is globally consistent, False otherwise
    """
    validator = TransactionValidator(network_size, connections, 
                                   transaction_proposals, failed_nodes)
    return validator.validate()