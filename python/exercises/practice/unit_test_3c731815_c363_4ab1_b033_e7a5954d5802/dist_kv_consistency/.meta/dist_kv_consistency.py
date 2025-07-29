import time
import random

# Global configuration
CLUSTER_N = 1000
REPLICATION_FACTOR = 3
READ_QUORUM = 2

# Global in-memory store for all nodes.
# Each node_id maps to a dictionary which maps key -> (value, version_vector, timestamp)
store = {}

def create_node(node_id):
    if node_id not in store:
        store[node_id] = {}

def consistent_hash(key, N, R):
    base = abs(hash(key))
    return [(base + i) % N for i in range(R)]

def write(key, value, node_id):
    # Determine replica nodes using consistent hashing
    replicas = consistent_hash(key, CLUSTER_N, REPLICATION_FACTOR)
    # Write the key to each replica node
    for replica in replicas:
        create_node(replica)
        if key in store[replica]:
            current_value, current_vv, current_ts = store[replica][key]
            new_vv = current_vv[:]  # copy the version vector
        else:
            new_vv = [0] * CLUSTER_N
        new_vv[replica] += 1
        store[replica][key] = (value, new_vv, time.time())

def read(key, node_id):
    # Use consistent hash to determine the replica nodes for the key
    replicas = consistent_hash(key, CLUSTER_N, REPLICATION_FACTOR)
    collected_values = []
    collected_vvs = []
    collected_timestamps = []
    count = 0
    for replica in replicas:
        if replica in store and key in store[replica]:
            val, vv, ts = store[replica][key]
            collected_values.append(val)
            collected_vvs.append(vv)
            collected_timestamps.append(ts)
            count += 1
            if count >= READ_QUORUM:
                break
    if collected_values:
        return reconcile(collected_values, collected_vvs, collected_timestamps)
    return None

def gossip(node_id):
    create_node(node_id)
    # Select a random node from the cluster excluding the current node.
    all_nodes = list(range(CLUSTER_N))
    all_nodes.remove(node_id)
    target = random.choice(all_nodes)
    create_node(target)
    
    # Get the union of keys present in both nodes.
    keys_node = set(store[node_id].keys())
    keys_target = set(store[target].keys())
    all_keys = keys_node.union(keys_target)
    
    for key in all_keys:
        rec1 = store[node_id].get(key)
        rec2 = store[target].get(key)
        if rec1 and rec2:
            # Use reconcile to determine the most recent value.
            reconciled_value = reconcile([rec1[0], rec2[0]], [rec1[1], rec2[1]], [rec1[2], rec2[2]])
            # Determine which record to propagate based on reconciliation.
            if reconciled_value == rec1[0]:
                store[target][key] = rec1
            else:
                store[node_id][key] = rec2
        elif rec1:
            store[target][key] = rec1
        elif rec2:
            store[node_id][key] = rec2

def reconcile(values, version_vectors, timestamps):
    n = len(values)
    def dominates(v1, v2):
        # v1 dominates v2 if for all indices, v1[i] >= v2[i] and there is at least one index with >
        length = min(len(v1), len(v2))
        greater = False
        for i in range(length):
            if v1[i] < v2[i]:
                return False
            if v1[i] > v2[i]:
                greater = True
        return greater

    chosen_index = 0
    for i in range(1, n):
        if dominates(version_vectors[i], version_vectors[chosen_index]):
            chosen_index = i
        elif not dominates(version_vectors[chosen_index], version_vectors[i]):
            # Conflict: choose the one with the later timestamp.
            if timestamps[i] > timestamps[chosen_index]:
                chosen_index = i
    return values[chosen_index]