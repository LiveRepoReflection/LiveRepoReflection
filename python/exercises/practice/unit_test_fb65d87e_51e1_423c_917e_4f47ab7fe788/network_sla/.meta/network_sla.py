import heapq
import copy

class NetworkSLA:
    def __init__(self, graph, requests):
        # Graph: dict with "nodes" and "edges"
        # nodes: dict: node -> {"capacity": int}
        # edges: list of dicts with "from", "to", "capacity", "latency"
        self.graph = graph
        self.requests = requests
        # Build adjacency list for easier path search.
        self.adj = {}
        for node in graph["nodes"]:
            self.adj[node] = []
        # Each edge key will be (u,v) and store its initial capacity and latency.
        self.edge_info = {}
        for edge in graph["edges"]:
            u = edge["from"]
            v = edge["to"]
            cap = edge["capacity"]
            lat = edge["latency"]
            self.adj[u].append((v, lat))
            self.edge_info[(u, v)] = {"capacity": cap, "latency": lat}
        # Global available capacities for nodes and edges.
        # For nodes, we track remaining processing capacity.
        self.node_remaining = {node: graph["nodes"][node]["capacity"] for node in graph["nodes"]}
        # For edges, track remaining bandwidth.
        self.edge_remaining = {edge: self.edge_info[edge]["capacity"] for edge in self.edge_info}
        # Initialize edge flows mapping.
        self.edge_flows = {}

    def solve(self):
        satisfied_count = 0
        request_deliveries = []
        # Process requests in original order
        for req in self.requests:
            source = req["source"]
            destination = req["destination"]
            volume_needed = req["data_volume"]
            latency_req = req["latency_requirement"]
            # Make deep copies of capacities to attempt allocation for this request
            local_node = copy.deepcopy(self.node_remaining)
            local_edge = copy.deepcopy(self.edge_remaining)
            temp_edge_allocation = {}  # key: (u,v), value: allocated flow for this request
            
            # Special case: request from a node to itself.
            if source == destination:
                if local_node[source] >= volume_needed:
                    local_node[source] -= volume_needed
                    # Commit changes
                    self.node_remaining = local_node
                    satisfied_count += 1
                    request_deliveries.append(volume_needed)
                # else: cannot satisfy this request; do nothing.
                continue

            remaining = volume_needed
            allocation_possible = True
            # Try to allocate until the full volume is assigned.
            while remaining > 0:
                path, total_latency = self._find_shortest_path(source, destination, latency_req, local_edge)
                if path is None or total_latency > latency_req:
                    allocation_possible = False
                    break
                # Determine bottleneck along edges in the path
                bottleneck_edge = float('inf')
                for i in range(len(path)-1):
                    u, v = path[i], path[i+1]
                    bottleneck_edge = min(bottleneck_edge, local_edge.get((u,v), 0))
                # Determine bottleneck for node capacities along the path.
                # For source and destination, usage is f; for intermediate nodes, usage is 2*f.
                bottleneck_node = float('inf')
                for idx, node in enumerate(path):
                    if node == source or node == destination:
                        bottleneck_node = min(bottleneck_node, local_node[node])
                    else:
                        # require 2 units capacity per unit flow for intermediate nodes.
                        bottleneck_node = min(bottleneck_node, local_node[node] // 2)
                possible_flow = min(bottleneck_edge, bottleneck_node, remaining)
                if possible_flow <= 0:
                    allocation_possible = False
                    break
                # Update local capacities along edges.
                for i in range(len(path)-1):
                    u, v = path[i], path[i+1]
                    local_edge[(u,v)] -= possible_flow
                    temp_edge_allocation[(u, v)] = temp_edge_allocation.get((u, v), 0) + possible_flow
                # Update local node capacities.
                # Source and destination reduce by possible_flow.
                local_node[source] -= possible_flow
                local_node[destination] -= possible_flow
                # Intermediate nodes reduce by 2*possible_flow.
                for node in path[1:-1]:
                    local_node[node] -= 2 * possible_flow
                remaining -= possible_flow
            
            if allocation_possible and remaining == 0:
                # Commit local capacities to global ones.
                self.node_remaining = local_node
                self.edge_remaining = local_edge
                # Update global edge_flows.
                for edge in temp_edge_allocation:
                    self.edge_flows[edge] = self.edge_flows.get(edge, 0) + temp_edge_allocation[edge]
                satisfied_count += 1
                request_deliveries.append(volume_needed)
            # If allocation not possible, do nothing (roll back any tentative flow)
        return satisfied_count, request_deliveries, self.edge_flows

    def _find_shortest_path(self, source, destination, max_latency, edge_caps):
        # Modified Dijkstra to find shortest latency path (by sum of latencies)
        # using only edges with available capacity > 0.
        dist = {node: float('inf') for node in self.adj}
        prev = {node: None for node in self.adj}
        dist[source] = 0
        heap = [(0, source)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            if u == destination:
                break
            for v, lat in self.adj[u]:
                # Only consider edge if there is remaining capacity.
                if edge_caps.get((u, v), 0) <= 0:
                    continue
                new_dist = d + lat
                if new_dist < dist[v] and new_dist <= max_latency:
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(heap, (new_dist, v))
        if dist[destination] == float('inf'):
            return None, None
        # Reconstruct path
        path = []
        curr = destination
        while curr is not None:
            path.append(curr)
            curr = prev[curr]
        path.reverse()
        return path, dist[destination]