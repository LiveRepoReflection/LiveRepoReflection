class Node:
    """
    A node in a distributed key-value store system with eventual consistency.
    Each node contains its own copy of the data.
    """
    def __init__(self):
        """Initialize an empty node with a dictionary to store key-value pairs and timestamps."""
        # Store data as {key: (value, timestamp)}
        self._store = {}
        # For advanced conflict resolution (bonus challenge)
        self._hinted_handoffs = {}  # {node_id: {key: (value, timestamp)}}

    def put(self, key, value, timestamp):
        """
        Store a key-value pair with its timestamp.
        
        Args:
            key (str): The key to store
            value (str): The value to store
            timestamp (int): The timestamp of the operation
            
        Returns:
            bool: True if the put operation changed the store, False otherwise
        """
        # Check if we already have this key with a newer or equal timestamp
        if key in self._store:
            old_value, old_timestamp = self._store[key]
            if old_timestamp > timestamp:
                return False  # Existing data is newer, ignore this update
            if old_timestamp == timestamp and old_value == value:
                return False  # Same data, no need to update
        
        # Store the new value and timestamp
        self._store[key] = (value, timestamp)
        return True

    def get(self, key):
        """
        Retrieve the value for a given key.
        
        Args:
            key (str): The key to look up
            
        Returns:
            str or None: The value if key exists, None otherwise
        """
        if key in self._store:
            value, _ = self._store[key]
            return value
        return None

    def _get_metadata(self):
        """
        Get lightweight metadata about the current state of the node.
        This is used to efficiently determine what needs to be synchronized.
        
        Returns:
            dict: A mapping of keys to timestamps
        """
        return {key: timestamp for key, (_, timestamp) in self._store.items()}

    def reconcile(self, other_node):
        """
        Synchronize data between this node and another node.
        After reconciliation, both nodes should have the most recent versions of all keys.
        
        Args:
            other_node (Node): The node to synchronize with
        """
        # Get metadata (just the keys and timestamps) from both nodes
        self_metadata = self._get_metadata()
        other_metadata = other_node._get_metadata()
        
        # Identify keys that need to be sent from self to other
        keys_to_send = []
        for key, self_ts in self_metadata.items():
            if key not in other_metadata or self_ts > other_metadata[key]:
                keys_to_send.append(key)
        
        # Identify keys that need to be received from other to self
        keys_to_receive = []
        for key, other_ts in other_metadata.items():
            if key not in self_metadata or other_ts > self_metadata[key]:
                keys_to_receive.append(key)
        
        # Handle the case where both have the same key with the same timestamp but different values
        # This is part of the conflict resolution strategy (bonus challenge)
        for key in set(self_metadata.keys()) & set(other_metadata.keys()):
            if self_metadata[key] == other_metadata[key]:
                self_value = self.get(key)
                other_value = other_node.get(key)
                if self_value != other_value:
                    # Deterministic conflict resolution: use lexicographically smaller value
                    if other_value < self_value:
                        keys_to_receive.append(key)
                    else:
                        keys_to_send.append(key)
        
        # Transfer data from self to other
        for key in keys_to_send:
            value, timestamp = self._store[key]
            other_node.put(key, value, timestamp)
        
        # Transfer data from other to self
        for key in keys_to_receive:
            value = other_node.get(key)
            timestamp = other_metadata[key]
            self.put(key, value, timestamp)

    # Bonus challenge: hinted handoff
    def register_handoff(self, target_node_id, key, value, timestamp):
        """
        Store data intended for another node that is currently unavailable.
        
        Args:
            target_node_id: Identifier for the target node
            key (str): The key to store
            value (str): The value to store
            timestamp (int): The timestamp of the operation
        """
        if target_node_id not in self._hinted_handoffs:
            self._hinted_handoffs[target_node_id] = {}
        
        current_store = self._hinted_handoffs[target_node_id]
        if key not in current_store or timestamp > current_store[key][1]:
            current_store[key] = (value, timestamp)

    def process_handoffs(self, target_node, target_node_id):
        """
        Deliver stored data to a node that was previously unavailable.
        
        Args:
            target_node (Node): The now-available node
            target_node_id: Identifier for the target node
        """
        if target_node_id not in self._hinted_handoffs:
            return
        
        for key, (value, timestamp) in self._hinted_handoffs[target_node_id].items():
            target_node.put(key, value, timestamp)
        
        # Clear processed handoffs
        del self._hinted_handoffs[target_node_id]