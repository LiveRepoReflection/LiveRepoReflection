import random
import collections

INF = 10**9

def optimize_supply_chain(graph_data):
    """
    Baseline algorithm for optimizing the supply chain resiliency.
    This baseline does not invest in hardening or redundant routes and returns empty sets for both,
    while simulating supply chain disruptions to compute the worst-case delivery amount.
    
    Args:
        graph_data (dict): A dictionary containing:
            - 'nodes': List of node dictionaries.
            - 'edges': List of edge dictionaries.
            - 'budget': Total available budget (not used in baseline).
            - 'number_of_scenarios': Number of disruption scenarios to simulate.
    
    Returns:
        tuple: (set of hardened facility ids, set of redundant route tuples, expected minimum delivery)
    """
    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('edges', [])
    budget = graph_data.get('budget', 0)
    num_scenarios = graph_data.get('number_of_scenarios', 10)
    
    # Baseline: No facilities are hardened and no redundant edges are added.
    hardened = set()
    redundant = set()
    
    # Precompute incoming edges to identify source nodes (nodes with no incoming edges)
    incoming = {node['id']: 0 for node in nodes}
    for edge in edges:
        target = edge['target']
        if target in incoming:
            incoming[target] += 1
    source_ids = {node['id'] for node in nodes if incoming[node['id']] == 0}
    # Identify sink nodes (customer nodes)
    sink_ids = {node['id'] for node in nodes if node.get('is_customer', False)}
    
    # Create a lookup for node info by id
    node_map = {node['id']: node for node in nodes}
    
    delivery_results = []
    for _ in range(num_scenarios):
        # Determine operational status for each node.
        # For hardened nodes, operational always True. For others, operational with probability 1 - disruption_probability.
        operational = {}
        for node in nodes:
            node_id = node['id']
            if node_id in hardened:
                operational[node_id] = True
            else:
                if random.random() < (1 - node.get('disruption_probability', 0)):
                    operational[node_id] = True
                else:
                    operational[node_id] = False

        # Build flow network for this scenario and compute max flow.
        flow_network, src, sink = build_flow_network(operational, node_map, edges, source_ids, sink_ids)
        flow = edmonds_karp(flow_network, src, sink)
        delivery_results.append(flow)
    
    # The expected minimum delivery is interpreted as the worst-case delivery across scenarios.
    expected_delivery = min(delivery_results) if delivery_results else 0

    return (hardened, redundant, expected_delivery)

def build_flow_network(operational, node_map, edges, source_ids, sink_ids):
    """
    Build a flow network from the supply chain graph for operational nodes only.
    Each operational node v is split into v_in and v_out.
    
    A super source 'S' connects to each source node (v_in) with capacity INF.
    Each operational node v has an edge from v_in to v_out with capacity = node capacity.
    For each edge (u, v) in the original graph where both nodes are operational,
    add an edge from u_out to v_in with capacity equal to edge capacity.
    Each sink node (customer) v connects from v_out to a super sink 'T' with capacity INF.
    
    Returns:
        (graph, source, sink) where graph is a dict: {u: {v: capacity, ...}, ...}
    """
    graph = collections.defaultdict(dict)
    
    # Helper to add edge in residual graph
    def add_edge(u, v, capacity):
        if capacity <= 0:
            return
        if v in graph[u]:
            graph[u][v] += capacity
        else:
            graph[u][v] = capacity
        # Ensure reverse edge exists with 0 capacity
        if u not in graph[v]:
            graph[v][u] = 0

    # Create node-split for each operational node
    for node_id, node in node_map.items():
        if not operational.get(node_id, False):
            continue
        in_node = f"{node_id}_in"
        out_node = f"{node_id}_out"
        capacity = node.get('capacity', 0)
        add_edge(in_node, out_node, capacity)
    
    # Add edges corresponding to supply chain edges from u_out to v_in
    for edge in edges:
        u = edge['source']
        v = edge['target']
        if not (operational.get(u, False) and operational.get(v, False)):
            continue
        u_out = f"{u}_out"
        v_in = f"{v}_in"
        edge_capacity = edge.get('capacity', 0)
        add_edge(u_out, v_in, edge_capacity)
    
    # Create super source 'S' and super sink 'T'
    source = "S"
    sink = "T"
    
    # Connect super source S to each source node's in_node if operational.
    for node_id in source_ids:
        if not operational.get(node_id, False):
            continue
        in_node = f"{node_id}_in"
        add_edge(source, in_node, INF)
    
    # Connect each customer node's out_node to super sink T if operational.
    for node_id in sink_ids:
        if not operational.get(node_id, False):
            continue
        out_node = f"{node_id}_out"
        add_edge(out_node, sink, INF)
    
    return graph, source, sink

def edmonds_karp(graph, source, sink):
    """
    Implementation of the Edmonds-Karp algorithm for computing max flow.
    Graph is represented as a dict of dicts: {u: {v: capacity, ...}, ...}
    """
    max_flow = 0
    parent = {}
    
    def bfs():
        nonlocal parent
        parent = {source: None}
        queue = collections.deque([source])
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if v not in parent and graph[u][v] > 0:
                    parent[v] = u
                    if v == sink:
                        return True
                    queue.append(v)
        return False
    
    while bfs():
        # Find the minimum residual capacity along the path found by BFS
        path_flow = INF
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, graph[u][v])
            v = u
        # Update residual capacities along the path
        v = sink
        while v != source:
            u = parent[v]
            graph[u][v] -= path_flow
            graph[v][u] += path_flow
            v = u
        max_flow += path_flow
    return max_flow

if __name__ == "__main__":
    # Sample execution using a fixed graph for debugging purposes.
    sample_graph = {
        'nodes': [
            {'id': 'A', 'capacity': 100, 'hardening_cost': 10, 'disruption_probability': 0.0, 'is_customer': False},
            {'id': 'B', 'capacity': 50, 'hardening_cost': 20, 'disruption_probability': 0.0, 'is_customer': False},
            {'id': 'C', 'capacity': 30, 'hardening_cost': 15, 'disruption_probability': 0.0, 'is_customer': False},
            {'id': 'D', 'capacity': 100, 'hardening_cost': 25, 'disruption_probability': 0.0, 'is_customer': True}
        ],
        'edges': [
            {'source': 'A', 'target': 'B', 'capacity': 40},
            {'source': 'B', 'target': 'C', 'capacity': 30},
            {'source': 'C', 'target': 'D', 'capacity': 30},
            {'source': 'A', 'target': 'C', 'capacity': 20}
        ],
        'budget': 50,
        'number_of_scenarios': 10
    }
    result = optimize_supply_chain(sample_graph)
    print("Hardened facilities:", result[0])
    print("Redundant routes:", result[1])
    print("Expected minimum delivery:", result[2])