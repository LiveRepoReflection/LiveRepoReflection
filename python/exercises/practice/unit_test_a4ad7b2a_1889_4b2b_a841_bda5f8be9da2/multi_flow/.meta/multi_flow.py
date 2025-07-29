import math
from collections import defaultdict, deque

class Edge:
    def __init__(self, u, v, capacity, cost, rev, orig, orig_key):
        self.u = u            # tail node
        self.v = v            # head node
        self.capacity = capacity
        self.cost = cost
        self.rev = rev        # index of reverse edge in graph[v]
        self.orig = orig      # True if this is an original (forward) edge
        self.orig_key = orig_key  # (u, v) tuple if orig==True, else None

def multi_flow(num_nodes, edges, commodities):
    # Build the residual graph
    graph = [[] for _ in range(num_nodes)]
    # For each input edge, add forward and reverse edges.
    for u, v, cap, cost in edges:
        # Forward edge
        forward = Edge(u, v, cap, cost, len(graph[v]), True, (u, v))
        # Reverse edge
        reverse = Edge(v, u, 0, -cost, len(graph[u]), False, None)
        graph[u].append(forward)
        graph[v].append(reverse)

    # Global result: dictionary mapping (u, v) -> {commodity_index: flow}
    result = defaultdict(lambda: defaultdict(int))

    # For each commodity, use a successive shortest path algorithm on the residual graph.
    for comm_index, (source, sink, demand) in enumerate(commodities):
        flow_needed = demand
        # While there is remaining flow for this commodity.
        while flow_needed > 0:
            # Bellman-Ford to find the shortest path from source to sink.
            dist = [math.inf] * num_nodes
            in_queue = [False] * num_nodes
            prev_node = [-1] * num_nodes
            prev_edge = [-1] * num_nodes
            dist[source] = 0

            queue = deque([source])
            in_queue[source] = True

            while queue:
                u = queue.popleft()
                in_queue[u] = False
                for i, e in enumerate(graph[u]):
                    if e.capacity > 0 and dist[e.v] > dist[u] + e.cost:
                        dist[e.v] = dist[u] + e.cost
                        prev_node[e.v] = u
                        prev_edge[e.v] = i
                        if not in_queue[e.v]:
                            queue.append(e.v)
                            in_queue[e.v] = True

            # If sink is unreachable, then the commodity demand cannot be satisfied.
            if dist[sink] == math.inf:
                return None

            # Determine the maximum flow we can send along the found path.
            path_flow = flow_needed
            v = sink
            while v != source:
                u = prev_node[v]
                edge = graph[u][prev_edge[v]]
                if edge.capacity < path_flow:
                    path_flow = edge.capacity
                v = u

            # Augment the flow along the path.
            v = sink
            while v != source:
                u = prev_node[v]
                edge = graph[u][prev_edge[v]]
                # If this is an original forward edge, record the commodity flow.
                if edge.orig:
                    result[edge.orig_key][comm_index] += path_flow
                # Decrease capacity and increase capacity of the reverse edge.
                edge.capacity -= path_flow
                rev_edge = graph[edge.v][edge.rev]
                rev_edge.capacity += path_flow
                v = u

            flow_needed -= path_flow

    # Convert result to regular dicts.
    final_result = {}
    for key, comm_dict in result.items():
        final_result[key] = dict(comm_dict)
    return final_result

if __name__ == '__main__':
    # For simple ad-hoc testing
    num_nodes = 4
    edges = [
        (0, 1, 10, 1),
        (0, 2, 5, 2),
        (1, 2, 15, 1),
        (1, 3, 7, 3),
        (2, 3, 12, 1)
    ]
    commodities = [
        (0, 3, 8)
    ]
    solution = multi_flow(num_nodes, edges, commodities)
    if solution is None:
        print("No feasible solution")
    else:
        print(solution)