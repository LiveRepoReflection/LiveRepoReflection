import threading
import time
import uuid
import copy
import random
from collections import defaultdict, deque

# Global state
nodes = {}
current_node_id = None
all_node_ids = None

class Node:
    def __init__(self, node_id, all_node_ids):
        self.node_id = node_id
        self.all_node_ids = all_node_ids
        self.data = {}  # Main key-value store
        self.transaction_data = {}  # Snapshot data for active transactions
        self.transaction_writes = {}  # Write sets for active transactions
        self.transaction_start_times = {}  # Start times for active transactions
        self.committed_transactions = []  # List of committed transaction IDs with timestamps
        self.locks = {}  # Locks for keys
        self.global_lock = threading.RLock()  # Global lock for transaction management
        self.transaction_lock = threading.RLock()  # Lock for transaction operations
        
        # Log for durability
        self.transaction_log = []
        
        # For consensus
        self.prepare_responses = defaultdict(dict)
        self.commit_responses = defaultdict(dict)
        
        # For failure detection
        self.heartbeats = {node_id: time.time() for node_id in all_node_ids}
        self.heartbeat_thread = threading.Thread(target=self._send_heartbeats, daemon=True)
        self.heartbeat_thread.start()
    
    def _send_heartbeats(self):
        """Simulates sending heartbeats to other nodes."""
        while True:
            for node_id in self.all_node_ids:
                if node_id != self.node_id:
                    # In a real system, we'd send a network request here
                    # For simulation, we just update our own record
                    self.heartbeats[node_id] = time.time()
            time.sleep(1)
    
    def is_node_alive(self, node_id):
        """Check if a node is alive based on heartbeats."""
        # In a real system, this would involve network checks
        # For simulation, we assume all nodes are alive
        return True

    def begin_transaction(self):
        """Start a new transaction."""
        with self.transaction_lock:
            tx_id = str(uuid.uuid4())
            # Create a snapshot of the current state
            self.transaction_data[tx_id] = copy.deepcopy(self.data)
            self.transaction_writes[tx_id] = set()  # Track keys modified in this transaction
            self.transaction_start_times[tx_id] = time.time()
            return tx_id
    
    def get(self, tx_id, key):
        """Get a value for a key within a transaction."""
        if tx_id not in self.transaction_data:
            raise Exception(f"Transaction {tx_id} not found or already committed/rolled back")
        
        # Return value from transaction's snapshot
        return self.transaction_data[tx_id].get(key)
    
    def put(self, tx_id, key, value):
        """Update a value for a key within a transaction."""
        if tx_id not in self.transaction_data:
            raise Exception(f"Transaction {tx_id} not found or already committed/rolled back")
        
        # Update in transaction's snapshot
        self.transaction_data[tx_id][key] = value
        self.transaction_writes[tx_id].add(key)
    
    def prepare_commit(self, tx_id):
        """First phase of two-phase commit protocol."""
        with self.global_lock:
            # Check for conflicts with transactions that committed after this one started
            tx_start_time = self.transaction_start_times[tx_id]
            write_set = self.transaction_writes[tx_id]
            
            for committed_tx_id, commit_time in self.committed_transactions:
                if commit_time > tx_start_time:
                    # Check if this transaction's write set intersects with a committed transaction
                    committed_write_set = self.transaction_writes.get(committed_tx_id, set())
                    if write_set & committed_write_set:
                        return False  # Conflict detected
            
            # No conflicts found, vote to commit
            return True
    
    def commit_transaction(self, tx_id):
        """Commit a transaction using a simplified consensus protocol."""
        if tx_id not in self.transaction_data:
            raise Exception(f"Transaction {tx_id} not found or already committed/rolled back")
        
        # Phase 1: Prepare (collect votes)
        prepare_success = self._two_phase_commit_prepare(tx_id)
        if not prepare_success:
            self._cleanup_transaction(tx_id)
            return False
        
        # Phase 2: Commit
        commit_success = self._two_phase_commit_commit(tx_id)
        if not commit_success:
            self._cleanup_transaction(tx_id)
            return False
        
        # Apply changes locally
        with self.global_lock:
            # Update main data store
            for key, value in self.transaction_data[tx_id].items():
                if key in self.transaction_writes[tx_id]:
                    self.data[key] = value
            
            # Record the commit
            commit_time = time.time()
            self.committed_transactions.append((tx_id, commit_time))
            
            # Log the transaction for durability
            self.transaction_log.append({
                'type': 'commit',
                'tx_id': tx_id,
                'changes': {k: self.transaction_data[tx_id][k] for k in self.transaction_writes[tx_id]},
                'timestamp': commit_time
            })
            
            # Clean up
            self._cleanup_transaction(tx_id, committed=True)
            
            return True
    
    def _two_phase_commit_prepare(self, tx_id):
        """Simulate the prepare phase of 2PC across all nodes."""
        # In a real system, we'd send prepare messages to all nodes
        # For simulation, we'll just check if this node can commit
        
        # Clear previous responses
        self.prepare_responses[tx_id] = {}
        
        # Local prepare
        local_prepare = self.prepare_commit(tx_id)
        self.prepare_responses[tx_id][self.node_id] = local_prepare
        
        # Simulate responses from other nodes
        for node_id in self.all_node_ids:
            if node_id != self.node_id:
                if not self.is_node_alive(node_id):
                    continue  # Skip failed nodes
                
                # Simulate other nodes' prepare phase
                # In a real system, this would involve network communication
                # For simulation, we'll just assume they all agree
                self.prepare_responses[tx_id][node_id] = True
        
        # Count successful votes
        successful_votes = sum(1 for node_id, response in self.prepare_responses[tx_id].items() 
                              if response and self.is_node_alive(node_id))
        
        # Need a majority to proceed
        return successful_votes > len(self.all_node_ids) // 2
    
    def _two_phase_commit_commit(self, tx_id):
        """Simulate the commit phase of 2PC across all nodes."""
        # In a real system, we'd send commit messages to all nodes
        # For simulation, we'll just assume all nodes can commit
        
        # Clear previous responses
        self.commit_responses[tx_id] = {}
        
        # Record local commit
        self.commit_responses[tx_id][self.node_id] = True
        
        # Simulate responses from other nodes
        for node_id in self.all_node_ids:
            if node_id != self.node_id:
                if not self.is_node_alive(node_id):
                    continue  # Skip failed nodes
                
                # Simulate other nodes' commit phase
                # In a real system, this would involve network communication
                self.commit_responses[tx_id][node_id] = True
        
        # Count successful commits
        successful_commits = sum(1 for node_id, response in self.commit_responses[tx_id].items() 
                                if response and self.is_node_alive(node_id))
        
        # Need a majority to consider the commit successful
        return successful_commits > len(self.all_node_ids) // 2
    
    def rollback_transaction(self, tx_id):
        """Roll back a transaction."""
        if tx_id not in self.transaction_data:
            raise Exception(f"Transaction {tx_id} not found or already committed/rolled back")
        
        # Log the rollback for durability
        self.transaction_log.append({
            'type': 'rollback',
            'tx_id': tx_id,
            'timestamp': time.time()
        })
        
        # Clean up
        self._cleanup_transaction(tx_id)
        
        return True
    
    def _cleanup_transaction(self, tx_id, committed=False):
        """Clean up transaction data."""
        with self.transaction_lock:
            # Remove transaction data
            self.transaction_data.pop(tx_id, None)
            
            # Keep write set for committed transactions to check conflicts
            if not committed:
                self.transaction_writes.pop(tx_id, None)
            
            # Remove start time
            self.transaction_start_times.pop(tx_id, None)
            
            # Clean up consensus data
            self.prepare_responses.pop(tx_id, None)
            self.commit_responses.pop(tx_id, None)
    
    def recover_from_log(self):
        """Recover the node's state from the transaction log."""
        with self.global_lock:
            # Re-apply all committed transactions in order
            for log_entry in self.transaction_log:
                if log_entry['type'] == 'commit':
                    tx_id = log_entry['tx_id']
                    changes = log_entry['changes']
                    timestamp = log_entry['timestamp']
                    
                    # Apply changes
                    for key, value in changes.items():
                        self.data[key] = value
                    
                    # Record the commit
                    self.committed_transactions.append((tx_id, timestamp))

def initialize(node_id, node_ids):
    """Initialize a node in the distributed key-value store."""
    global nodes, current_node_id, all_node_ids
    
    current_node_id = node_id
    all_node_ids = node_ids
    
    # Create the node if it doesn't exist
    if node_id not in nodes:
        nodes[node_id] = Node(node_id, node_ids)
    
    # If node already exists, it might be recovering from a failure
    # In a real system, we'd initiate recovery here
    nodes[node_id].recover_from_log()

def begin():
    """Start a new transaction."""
    global nodes, current_node_id
    
    if current_node_id is None or current_node_id not in nodes:
        raise Exception("Node not initialized")
    
    return nodes[current_node_id].begin_transaction()

def get(tx_id, key):
    """Get a value within a transaction."""
    global nodes, current_node_id
    
    if current_node_id is None or current_node_id not in nodes:
        raise Exception("Node not initialized")
    
    return nodes[current_node_id].get(tx_id, key)

def put(tx_id, key, value):
    """Put a value within a transaction."""
    global nodes, current_node_id
    
    if current_node_id is None or current_node_id not in nodes:
        raise Exception("Node not initialized")
    
    return nodes[current_node_id].put(tx_id, key, value)

def commit(tx_id):
    """Commit a transaction."""
    global nodes, current_node_id
    
    if current_node_id is None or current_node_id not in nodes:
        raise Exception("Node not initialized")
    
    return nodes[current_node_id].commit_transaction(tx_id)

def rollback(tx_id):
    """Roll back a transaction."""
    global nodes, current_node_id
    
    if current_node_id is None or current_node_id not in nodes:
        raise Exception("Node not initialized")
    
    return nodes[current_node_id].rollback_transaction(tx_id)