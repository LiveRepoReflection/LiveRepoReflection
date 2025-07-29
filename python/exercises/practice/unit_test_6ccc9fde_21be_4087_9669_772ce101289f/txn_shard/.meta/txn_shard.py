import threading

global_shard_mapping = {}
global_nodes = {}
active_transactions = {}
transaction_counter = 0
transaction_lock = threading.Lock()

def get_sorted_shards():
    return sorted(global_shard_mapping.keys())

def get_node_for_key(key):
    shards = get_sorted_shards()
    if not shards:
        raise Exception("No shards available")
    index = hash(key) % len(shards)
    shard = shards[index]
    node_id = global_shard_mapping[shard]
    if node_id not in global_nodes:
        global_nodes[node_id] = Node(node_id)
    return global_nodes[node_id]

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.store = {}
        self.locked_keys = {}   # key -> txn_id
        self.pending_ops = {}   # txn_id -> dict of key -> (action, value)
        self.lock = threading.Lock()
    
    def read(self, key):
        with self.lock:
            return self.store.get(key, None)
    
    def prepare(self, txn_id, operations):
        with self.lock:
            for key in operations:
                if key in self.locked_keys and self.locked_keys[key] != txn_id:
                    return False
            if txn_id not in self.pending_ops:
                self.pending_ops[txn_id] = {}
            for key, op in operations.items():
                self.locked_keys[key] = txn_id
                self.pending_ops[txn_id][key] = op
            return True

    def commit(self, txn_id):
        with self.lock:
            if txn_id not in self.pending_ops:
                return
            ops = self.pending_ops.pop(txn_id)
            for key, (action, value) in ops.items():
                if action == 'write':
                    self.store[key] = value
                elif action == 'delete':
                    if key in self.store:
                        del self.store[key]
                if key in self.locked_keys and self.locked_keys[key] == txn_id:
                    del self.locked_keys[key]
    
    def abort(self, txn_id):
        with self.lock:
            if txn_id not in self.pending_ops:
                return
            ops = self.pending_ops.pop(txn_id)
            for key in ops:
                if key in self.locked_keys and self.locked_keys[key] == txn_id:
                    del self.locked_keys[key]

def begin_transaction():
    global transaction_counter
    with transaction_lock:
        txn_id = transaction_counter
        transaction_counter += 1
    active_transactions[txn_id] = {}
    return txn_id

def read(txn_id, key):
    if txn_id not in active_transactions:
        raise Exception("Invalid Transaction")
    node = get_node_for_key(key)
    node_id = node.node_id
    txn_ops = active_transactions[txn_id].get(node_id, {})
    if key in txn_ops:
        action, value = txn_ops[key]
        if action == 'write':
            return value
        elif action == 'delete':
            return None
    return node.read(key)

def write(txn_id, key, value):
    if txn_id not in active_transactions:
        raise Exception("Invalid Transaction")
    node = get_node_for_key(key)
    node_id = node.node_id
    if node_id not in active_transactions[txn_id]:
        active_transactions[txn_id][node_id] = {}
    active_transactions[txn_id][node_id][key] = ('write', value)

def delete(txn_id, key):
    if txn_id not in active_transactions:
        raise Exception("Invalid Transaction")
    node = get_node_for_key(key)
    node_id = node.node_id
    if node_id not in active_transactions[txn_id]:
        active_transactions[txn_id][node_id] = {}
    active_transactions[txn_id][node_id][key] = ('delete', None)

def commit_transaction(txn_id):
    if txn_id not in active_transactions:
        raise Exception("Invalid Transaction")
    txn_nodes = active_transactions[txn_id]
    prepared_nodes = []
    for node_id, operations in txn_nodes.items():
        node = global_nodes.get(node_id)
        if node is None:
            node = Node(node_id)
            global_nodes[node_id] = node
        if not node.prepare(txn_id, operations):
            for prepared_node in prepared_nodes:
                prepared_node.abort(txn_id)
            del active_transactions[txn_id]
            return False
        prepared_nodes.append(node)
    for node in prepared_nodes:
        node.commit(txn_id)
    del active_transactions[txn_id]
    return True

def abort_transaction(txn_id):
    if txn_id not in active_transactions:
        raise Exception("Invalid Transaction")
    txn_nodes = active_transactions[txn_id]
    for node_id in txn_nodes:
        node = global_nodes.get(node_id)
        if node:
            node.abort(txn_id)
    del active_transactions[txn_id]

def update_shard_mapping(shard_mappings):
    global global_shard_mapping
    global_shard_mapping.clear()
    for shard, node_id in shard_mappings.items():
        global_shard_mapping[shard] = node_id
        if node_id not in global_nodes:
            global_nodes[node_id] = Node(node_id)