import threading
import hashlib

TOTAL_NODES = 10
REPLICATION_FACTOR = 3

# Global list of storage nodes
nodes = []

def init_nodes():
    global nodes
    nodes = [StorageNode(i) for i in range(TOTAL_NODES)]

class StorageNode:
    def __init__(self, node_id):
        self.id = node_id
        self.store = {}  # key -> list of records; each record: {"data": bytes, "vc": list[int]}
        self.lock = threading.Lock()

    def put(self, key, data):
        with self.lock:
            if key not in self.store:
                base_vc = [0] * TOTAL_NODES
            else:
                records = self.store[key]
                base_vc = merge_vc([rec["vc"] for rec in records])
            # Increment this node's component
            new_vc = base_vc.copy()
            new_vc[self.id] += 1
            new_record = {"data": data, "vc": new_vc}
            # For simplicity, we always overwrite with the new record
            self.store[key] = [new_record]
            return new_record

    def get(self, key):
        with self.lock:
            if key in self.store:
                return self.store[key]
            else:
                return None

    def force_update(self, key, record):
        with self.lock:
            self.store[key] = [record]

def merge_vc(vcs):
    if not vcs:
        return [0] * TOTAL_NODES
    merged = [0] * TOTAL_NODES
    for i in range(TOTAL_NODES):
        merged[i] = max(vc[i] for vc in vcs)
    return merged

def sum_vc(vc):
    return sum(vc)

def get_replica_nodes(key):
    # Use a consistent hash of the key to determine starting index
    h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
    start = h % TOTAL_NODES
    replica_nodes = []
    for i in range(REPLICATION_FACTOR):
        index = (start + i) % TOTAL_NODES
        replica_nodes.append(nodes[index])
    return replica_nodes

def conflict_resolve(records):
    # In case of multiple versions (siblings), select by highest sum of vector clock.
    # If tie, select the first one.
    if not records:
        return None
    best = records[0]
    best_sum = sum_vc(best["vc"])
    for rec in records[1:]:
        current_sum = sum_vc(rec["vc"])
        if current_sum > best_sum:
            best = rec
            best_sum = current_sum
    return best

def put(key, data):
    replica_nodes = get_replica_nodes(key)
    results = []
    # Perform put on each replica node
    for node in replica_nodes:
        record = node.put(key, data)
        results.append(record)
    # Resolve conflicts among nodes
    final_record = conflict_resolve(results)
    # Force all replica nodes to update to the final record
    for node in replica_nodes:
        node.force_update(key, final_record)
    return final_record

def get(key):
    replica_nodes = get_replica_nodes(key)
    retrieved_records = []
    for node in replica_nodes:
        recs = node.get(key)
        if recs is not None:
            retrieved_records.extend(recs)
    if not retrieved_records:
        return None
    final_record = conflict_resolve(retrieved_records)
    return final_record["data"]

# Initialize nodes when module is imported
init_nodes()