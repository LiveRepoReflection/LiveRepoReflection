import heapq
import copy

class Edge:
    __slots__ = ["to", "cap", "cost", "rev", "transit_time"]
    def __init__(self, to, cap, cost, rev, transit_time):
        self.to = to
        self.cap = cap
        self.cost = cost
        self.rev = rev
        self.transit_time = transit_time

class CityRoutingNetwork:
    def __init__(self):
        # Graph is a dict mapping nodes to list of edges.
        self.graph = {}

    def _ensure_node(self, node):
        if node not in self.graph:
            self.graph[node] = []

    def add_route(self, frm, to, capacity, transit_time, cost_per_package):
        self._ensure_node(frm)
        self._ensure_node(to)
        # Forward edge from frm to to.
        forward = Edge(to, capacity, cost_per_package, len(self.graph[to]), transit_time)
        # Reverse edge from to to frm.
        reverse = Edge(frm, 0, -cost_per_package, len(self.graph[frm]), transit_time)
        self.graph[frm].append(forward)
        self.graph[to].append(reverse)

    def update_route(self, frm, to, capacity, transit_time, cost_per_package):
        if frm not in self.graph:
            return
        updated = False
        for idx, edge in enumerate(self.graph[frm]):
            if edge.to == to:
                # Update forward edge.
                edge.cap = capacity
                edge.cost = cost_per_package
                edge.transit_time = transit_time
                # Update reverse edge in the destination list.
                rev_index = edge.rev
                if to in self.graph and rev_index < len(self.graph[to]):
                    rev_edge = self.graph[to][rev_index]
                    # The reverse edge cost is always negative of the forward edge.
                    rev_edge.cost = -cost_per_package
                    rev_edge.transit_time = transit_time
                updated = True
                break
        # If route is not found, do nothing.
        if not updated:
            pass

    def process_delivery_request(self, source, sink, packages):
        # Create a copy of the graph so that queries do not affect global state.
        local_graph = self._copy_graph()
        result = self._min_cost_flow(source, sink, packages, local_graph)
        return result

    def _copy_graph(self):
        new_graph = {}
        # Ensure that all nodes in the global graph are copied.
        for node in self.graph:
            new_graph[node] = []
        # Also ensure that nodes referenced in edges are present.
        for node in self.graph:
            for edge in self.graph[node]:
                if edge.to not in new_graph:
                    new_graph[edge.to] = []
        # Copy all edges preserving the order.
        for u in self.graph:
            for edge in self.graph[u]:
                new_edge = Edge(edge.to, edge.cap, edge.cost, edge.rev, edge.transit_time)
                new_graph[u].append(new_edge)
        return new_graph

    def _min_cost_flow(self, s, t, f, graph):
        INF = float('inf')
        # Initialize potential for each node.
        potential = {node: 0 for node in graph}
        dist = {node: 0 for node in graph}
        prev_v = {node: None for node in graph}
        prev_e = {node: None for node in graph}
        flow = 0
        cost = 0

        while flow < f:
            # Dijkstra's algorithm to find the shortest path
            for node in graph:
                dist[node] = INF
            dist[s] = 0
            hq = []
            heapq.heappush(hq, (0, s))
            while hq:
                d, u = heapq.heappop(hq)
                if dist[u] < d:
                    continue
                for i, edge in enumerate(graph[u]):
                    if edge.cap > 0:
                        v = edge.to
                        nd = d + edge.cost + potential[u] - potential[v]
                        if nd < dist[v]:
                            dist[v] = nd
                            prev_v[v] = u
                            prev_e[v] = i
                            heapq.heappush(hq, (nd, v))
            if dist[t] == INF:
                return -1
            # Update potentials
            for v in graph:
                if dist[v] < INF:
                    potential[v] += dist[v]
            # Determine the maximum flow that can be pushed on the found path.
            add_flow = f - flow
            v = t
            while v != s:
                u = prev_v[v]
                edge = graph[u][prev_e[v]]
                add_flow = min(add_flow, edge.cap)
                v = u
            # Push the flow and update residual capacities.
            flow += add_flow
            cost += add_flow * potential[t]
            v = t
            while v != s:
                u = prev_v[v]
                edge = graph[u][prev_e[v]]
                edge.cap -= add_flow
                # Update reverse edge.
                graph[edge.to][edge.rev].cap += add_flow
                v = u
        return cost