import math
from collections import defaultdict

def minimal_trucks(warehouses, orders, truck_capacity):
    # Filter orders: only orders where both source and destination are valid warehouses
    valid_orders = []
    # Also accumulate total incoming for capacity check per warehouse and total volume
    total_incoming = defaultdict(int)
    total_outgoing = defaultdict(int)
    total_volume = 0
    for s, d, qty in orders:
        if s in warehouses and d in warehouses:
            # Ignore zero quantity orders (they don't matter)
            if qty < 0:
                # Negative orders are not allowed, ignore these as well
                continue
            valid_orders.append((s, d, qty))
            total_incoming[d] += qty
            total_outgoing[s] += qty
            total_volume += qty

    # Feasibility: for each warehouse, ensure total incoming <= capacity.
    for wh, cap in warehouses.items():
        if total_incoming[wh] > cap:
            return -1

    # If there are no valid orders, no trucks needed.
    if total_volume == 0:
        return 0

    # Build directed graph and aggregate weights for edges.
    graph = defaultdict(lambda: defaultdict(int))
    nodes = set()
    for s, d, qty in valid_orders:
        nodes.add(s)
        nodes.add(d)
        graph[s][d] += qty

    # Tarjan's algorithm to get strongly connected components.
    index = 0
    indices = {}
    lowlinks = {}
    onStack = {}
    S = []
    sccs = []
    node_to_scc = {}

    def strongconnect(v):
        nonlocal index
        indices[v] = index
        lowlinks[v] = index
        index += 1
        S.append(v)
        onStack[v] = True

        for w in graph[v]:
            if w not in indices:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif onStack.get(w, False):
                lowlinks[v] = min(lowlinks[v], indices[w])
        # If v is a root node, pop the stack and generate an SCC.
        if lowlinks[v] == indices[v]:
            component = []
            while True:
                w = S.pop()
                onStack[w] = False
                component.append(w)
                node_to_scc[w] = len(sccs)
                if w == v:
                    break
            sccs.append(component)

    # Ensure all nodes in orders are processed.
    for v in nodes:
        if v not in indices:
            strongconnect(v)

    # Build the contracted DAG for SCCs.
    scc_in = [0] * len(sccs)
    scc_out = [0] * len(sccs)
    # For each edge u->v, if they are in different SCCs, accumulate the weight.
    for u in graph:
        for v, w in graph[u].items():
            if node_to_scc[u] != node_to_scc[v]:
                scc_out[node_to_scc[u]] += w
                scc_in[node_to_scc[v]] += w

    # For each SCC, compute net supply needed at the start:
    # Only consider SCCs with no external incoming edges (source SCCs).
    scc_required = [0] * len(sccs)
    for i in range(len(sccs)):
        net = scc_out[i] - scc_in[i]
        if net < 0:
            net = 0
        scc_required[i] = net

    trucks_from_dag = 0
    # Sum required trucks for each source SCC in the contracted DAG (no incoming edge from other SCCs).
    # Also, if an SCC is isolated (no incoming) but might have net requirement.
    for i in range(len(sccs)):
        if scc_in[i] == 0:
            trucks_from_dag += math.ceil(scc_required[i] / truck_capacity) if scc_required[i] > 0 else 0

    # Base lower bound by total volume transported.
    base_trucks = math.ceil(total_volume / truck_capacity)

    # The answer is the maximum of the two lower bounds.
    return max(trucks_from_dag, base_trucks)
    
if __name__ == '__main__':
    # Sample manual test: This block can be used for simple local debugging.
    warehouses = {"A": 100, "B": 50, "C": 75}
    orders = [("A", "B", 30), ("B", "C", 20), ("A", "C", 40)]
    truck_capacity = 50
    print(minimal_trucks(warehouses, orders, truck_capacity))