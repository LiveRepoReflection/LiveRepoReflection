import heapq

def optimize_supply_chain(nodes, edges):
    # Build graph as a dictionary mapping node to list of edges
    graph = {}

    def add_node(u):
        if u not in graph:
            graph[u] = []

    # Add super source and sink
    add_node("super_source")
    add_node("super_sink")

    # Add nodes from input: For factories and distribution centers, add as is.
    # For warehouses, add two nodes: warehouse_in and warehouse_out.
    for node in nodes:
        if node['type'] == 'warehouse':
            add_node(node['id'] + "_in")
            add_node(node['id'] + "_out")
        else:
            add_node(node['id'])

    # Define Edge class for use in the residual graph.
    class Edge:
        def __init__(self, to, cap, cost, rev):
            self.to = to      # target node
            self.cap = cap    # remaining capacity
            self.cost = cost  # cost per unit of flow
            self.rev = rev    # index of reverse edge in target node's list

    # Function to add an edge to the graph (and its reverse edge).
    def add_edge(frm, to, cap, cost):
        forward = Edge(to, cap, cost, len(graph[to]))
        backward = Edge(frm, 0, -cost, len(graph[frm]))
        graph[frm].append(forward)
        graph[to].append(backward)
        return forward

    # List to hold mapping details for each original supply chain edge.
    original_edges = []  # Each element: (original_source, original_destination, forward_edge, original_capacity)

    # Add edges from super_source to factories and from distribution centers to super_sink.
    for node in nodes:
        if node['type'] == 'factory':
            add_edge("super_source", node['id'], node['production_capacity'], 0)
        elif node['type'] == 'distribution_center':
            add_edge(node['id'], "super_sink", node['demand'], 0)
        elif node['type'] == 'warehouse':
            add_edge(node['id'] + "_in", node['id'] + "_out", node['storage_capacity'], 0)

    # Helper function to find the type of a node given its id
    def find_node_type(node_id):
        for node in nodes:
            if node['id'] == node_id:
                return node['type']
        return None

    # Add the original supply chain edges with proper node transformation.
    for e in edges:
        u = e['source']
        v = e['destination']
        type_u = find_node_type(u)
        type_v = find_node_type(v)
        effective_u = u + "_out" if type_u == "warehouse" else u
        effective_v = v + "_in" if type_v == "warehouse" else v
        forward_edge = add_edge(effective_u, effective_v, e['capacity'], e['cost_per_unit'])
        original_edges.append((u, v, forward_edge, e['capacity']))

    # Calculate the total required flow (sum of demands at distribution centers)
    total_demand = sum(node['demand'] for node in nodes if node['type'] == 'distribution_center')

    # Min Cost Flow algorithm parameters
    INF = 10**9
    # Initialize potentials for all nodes (used for reduced costs in Dijkstra)
    potential = {u: 0 for u in graph}

    flow = 0
    cost = 0

    # Continue until we've pushed the required flow
    while flow < total_demand:
        # Use Dijkstra to find shortest path from super_source to super_sink
        dist = {u: INF for u in graph}
        dist["super_source"] = 0
        prev_v = {u: None for u in graph}
        prev_e = {u: None for u in graph}
        hq = []
        heapq.heappush(hq, (0, "super_source"))
        while hq:
            d, u = heapq.heappop(hq)
            if d != dist[u]:
                continue
            for i, edge in enumerate(graph[u]):
                if edge.cap > 0 and dist[edge.to] > dist[u] + edge.cost + potential[u] - potential[edge.to]:
                    dist[edge.to] = dist[u] + edge.cost + potential[u] - potential[edge.to]
                    prev_v[edge.to] = u
                    prev_e[edge.to] = i
                    heapq.heappush(hq, (dist[edge.to], edge.to))
        # If sink is unreachable, no solution exists.
        if dist["super_sink"] == INF:
            break
        # Update potentials for nodes reached.
        for u in graph:
            if dist[u] < INF:
                potential[u] += dist[u]

        # Determine the maximum additional flow possible along the found path.
        add_flow = total_demand - flow
        v = "super_sink"
        while v != "super_source":
            u = prev_v[v]
            e_index = prev_e[v]
            add_flow = min(add_flow, graph[u][e_index].cap)
            v = u

        flow += add_flow
        cost += add_flow * potential["super_sink"]

        # Update the residual network with the found flow.
        v = "super_sink"
        while v != "super_source":
            u = prev_v[v]
            e_index = prev_e[v]
            graph[u][e_index].cap -= add_flow
            rev_index = graph[u][e_index].rev
            graph[v][rev_index].cap += add_flow
            v = u

    # Check if the required flow was sent.
    if flow < total_demand:
        return None

    # Construct the result for original supply chain edges.
    result = {}
    for orig_u, orig_v, edge_obj, orig_cap in original_edges:
        used_flow = orig_cap - edge_obj.cap
        key = (orig_u, orig_v)
        if key in result:
            result[key] += used_flow
        else:
            result[key] = used_flow

    return result

if __name__ == "__main__":
    nodes = [
        {'id': 'F1', 'type': 'factory', 'production_capacity': 100},
        {'id': 'W1', 'type': 'warehouse', 'storage_capacity': 80},
        {'id': 'D1', 'type': 'distribution_center', 'demand': 70},
        {'id': 'D2', 'type': 'distribution_center', 'demand': 30}
    ]
    edges = [
        {'source': 'F1', 'destination': 'W1', 'capacity': 60, 'cost_per_unit': 2},
        {'source': 'F1', 'destination': 'D1', 'capacity': 40, 'cost_per_unit': 5},
        {'source': 'W1', 'destination': 'D1', 'capacity': 50, 'cost_per_unit': 3},
        {'source': 'W1', 'destination': 'D2', 'capacity': 30, 'cost_per_unit': 4}
    ]
    solution = optimize_supply_chain(nodes, edges)
    print("Optimal flows for the given supply chain:" if solution is not None else "No feasible solution", solution)