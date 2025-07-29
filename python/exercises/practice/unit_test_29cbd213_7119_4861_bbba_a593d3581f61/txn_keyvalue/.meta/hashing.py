def get_node_id(key, num_nodes):
    return hash(key) % num_nodes