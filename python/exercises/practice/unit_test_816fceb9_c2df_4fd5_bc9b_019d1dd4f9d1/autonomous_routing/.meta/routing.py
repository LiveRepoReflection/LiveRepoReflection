import heapq
import math

class RoutingSystem:
    def __init__(self):
        self.nodes = {}  # node_id -> active (bool)
        self.edges = {}  # source -> list of edges: {"dest": int, "latency": int, "bandwidth": int, "active": bool}
        self.routing_tables = {}  # node_id -> routing table dict

    def add_node(self, node):
        self.nodes[node] = True
        if node not in self.edges:
            self.edges[node] = []

    def add_edge(self, src, dest, latency, bandwidth):
        # Ensure nodes exist; if not, add them.
        if src not in self.nodes:
            self.add_node(src)
        if dest not in self.nodes:
            self.add_node(dest)
        # Add edge as active.
        self.edges[src].append({
            "dest": dest,
            "latency": latency,
            "bandwidth": bandwidth,
            "active": True
        })

    def simulate_edge_failure(self, src, dest):
        # Mark the edge from src to dest as inactive.
        if src in self.edges:
            for edge in self.edges[src]:
                if edge["dest"] == dest and edge["active"]:
                    edge["active"] = False

    def simulate_node_failure(self, node):
        # Mark node as inactive.
        if node in self.nodes:
            self.nodes[node] = False
        # Also mark all outgoing edges as inactive.
        if node in self.edges:
            for edge in self.edges[node]:
                edge["active"] = False
        # Optionally, incoming edges from other nodes should be ignored in routing.
        # We will handle that by checking target node active status in compute.

    def compute_routing_tables(self):
        # Recompute routing tables for all active nodes.
        self.routing_tables = {}
        for source in self.nodes:
            if not self.nodes[source]:
                self.routing_tables[source] = {}
            else:
                self.routing_tables[source] = self._dijkstra(source)

    def _dijkstra(self, source):
        # Modified Dijkstra's algorithm with lexicographic ordering:
        # Primary: total latency (minimize)
        # Secondary: - available_bandwidth (maximize available bandwidth)
        # Tertiary: next_hop id (minimize)
        # For the source, the available bandwidth is considered infinite.
        routing = {}  # target -> {"next_hop": int, "path": [node], "latency": int, "bandwidth": int}
        # Dictionary to keep best cost found for each node
        costs = {}  # node -> (latency, available_bw, next_hop, path)
        # Priority queue will store tuples: (latency, -available_bw, next_hop, current_node, path)
        # For source, next_hop is None and available_bw is float('inf')
        heap = []
        initial_cost = (0, -math.inf, None, source, [source])
        heapq.heappush(heap, initial_cost)
        costs[source] = (0, math.inf, None, [source])
        
        while heap:
            curr_latency, neg_bw, curr_next_hop, curr_node, curr_path = heapq.heappop(heap)
            curr_bw = -neg_bw
            # If current popped cost does not match stored cost, skip.
            if curr_node in costs:
                stored = costs[curr_node]
                if curr_latency != stored[0] or curr_bw != stored[1]:
                    continue

            # Relax edges from current node.
            if curr_node not in self.edges:
                continue
            for edge in self.edges[curr_node]:
                # Only consider active edges
                if not edge["active"]:
                    continue
                neighbor = edge["dest"]
                # Skip neighbor if it is inactive.
                if neighbor not in self.nodes or not self.nodes[neighbor]:
                    continue
                new_latency = curr_latency + edge["latency"]
                new_bw = curr_bw if curr_bw < edge["bandwidth"] else edge["bandwidth"]
                # Determine next hop: if we are at the source then next hop is neighbor, otherwise inherit.
                if curr_node == source:
                    new_next_hop = neighbor
                else:
                    new_next_hop = curr_next_hop

                new_path = curr_path + [neighbor]
                new_cost = (new_latency, -new_bw, new_next_hop if new_next_hop is not None else math.inf, neighbor, new_path)

                # If neighbor not seen or found a better route:
                if neighbor not in costs:
                    costs[neighbor] = (new_latency, new_bw, new_next_hop, new_path)
                    heapq.heappush(heap, new_cost)
                else:
                    old_latency, old_bw, old_next_hop, old_path = costs[neighbor]
                    # Lexicographic comparison:
                    # Compare latency first:
                    update = False
                    if new_latency < old_latency:
                        update = True
                    elif new_latency == old_latency:
                        # For equal latency, choose the one with higher available bandwidth.
                        if new_bw > old_bw:
                            update = True
                        elif new_bw == old_bw:
                            # For tie, choose the one with lower next hop id.
                            if new_next_hop is not None and old_next_hop is not None:
                                if new_next_hop < old_next_hop:
                                    update = True
                    if update:
                        costs[neighbor] = (new_latency, new_bw, new_next_hop, new_path)
                        heapq.heappush(heap, new_cost)
        
        # Build routing table excluding source itself.
        table = {}
        for dest in costs:
            if dest == source:
                continue
            latency, bandwidth, next_hop, path = costs[dest]
            table[dest] = {
                "next_hop": next_hop,
                "path": path,
                "latency": latency,
                "bandwidth": bandwidth
            }
        return table

    def get_routing_table(self, node):
        # Return computed routing table for the node, or empty dict if not computed.
        if node in self.routing_tables:
            return self.routing_tables[node]
        return {}