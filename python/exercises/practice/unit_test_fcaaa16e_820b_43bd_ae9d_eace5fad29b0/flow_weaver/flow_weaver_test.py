import unittest
from collections import defaultdict

# Import the function to test from the flow_weaver module.
# It is expected that optimize_network_flow(snapshot: dict) -> list of allocations is implemented.
from flow_weaver import optimize_network_flow

class TestFlowWeaver(unittest.TestCase):
    
    def _validate_allocations(self, snapshot, allocations):
        """
        Validate that the allocation meets capacity constraints, demand fulfillment,
        and flow conservation conditions.
        """
        nodes = snapshot["nodes"]
        links = snapshot["links"]
        commodities = snapshot["commodities"]

        # Build a mapping for link capacity: (source, destination) -> capacity info.
        link_capacities = {}
        for link in links:
            key = (link["source"], link["destination"])
            link_capacities[key] = {
                "capacity": link["capacity"],
                "length": link["length"],
                "cost": link["cost"]
            }

        # Aggregate flows per link
        flow_on_link = defaultdict(int)
        # Aggregated flows per commodity on nodes for flow conservation check.
        # For each commodity, for each node, record net flow.
        commodity_node_flow = {commodity["commodity_id"]: defaultdict(int) for commodity in commodities}

        for alloc in allocations:
            commodity_id = alloc["commodity_id"]
            src = alloc["source"]
            dst = alloc["destination"]
            flow = alloc["flow"]

            # Check that the link exists
            self.assertIn((src, dst), link_capacities, 
                          msg=f"Allocation uses non-existent link {src}->{dst} for commodity {commodity_id}")
            flow_on_link[(src, dst)] += flow

            # For flow conservation, subtract flow from src and add flow to dst.
            commodity_node_flow[commodity_id][src] -= flow
            commodity_node_flow[commodity_id][dst] += flow

        # Check link capacity constraints
        for (src, dst), total_flow in flow_on_link.items():
            capacity = link_capacities[(src, dst)]["capacity"]
            self.assertLessEqual(total_flow, capacity, 
                                 msg=f"Link {src}->{dst} exceeded capacity: {total_flow} > {capacity}")

        # Check that commodity demand is satisfied at origin and destination, and intermediate nodes equalize.
        for commodity in commodities:
            cid = commodity["commodity_id"]
            origin = commodity["origin"]
            destination = commodity["destination"]
            demand = commodity["demand"]

            for node in nodes:
                net_flow = commodity_node_flow[cid][node]
                if node == origin:
                    # Origin should emit exactly demand.
                    self.assertEqual(net_flow, -demand, 
                                     msg=f"Origin {origin} for commodity {cid} should emit {demand} but got {-net_flow}")
                elif node == destination:
                    # Destination should receive exactly demand.
                    self.assertEqual(net_flow, demand, 
                                     msg=f"Destination {destination} for commodity {cid} should receive {demand} but got {net_flow}")
                else:
                    # Other nodes may have zero net flow.
                    self.assertEqual(net_flow, 0, 
                                     msg=f"Intermediate node {node} for commodity {cid} net flow is not 0 (got {net_flow})")


    def test_basic_flow(self):
        # Simple network: Two nodes with one link.
        snapshot = {
            "nodes": ["A", "B"],
            "links": [
                {"source": "A", "destination": "B", "capacity": 10, "length": 5, "cost": 1.0},
            ],
            "commodities": [
                {"commodity_id": "commodity1", "origin": "A", "destination": "B", "demand": 5, "latency_weight": 1.0},
            ]
        }

        allocations = optimize_network_flow(snapshot)
        # Check that one allocation exists: A->B providing exactly 5 units.
        self.assertEqual(len(allocations), 1, msg="Expected a single allocation.")
        alloc = allocations[0]
        self.assertEqual(alloc["commodity_id"], "commodity1")
        self.assertEqual(alloc["source"], "A")
        self.assertEqual(alloc["destination"], "B")
        self.assertEqual(alloc["flow"], 5)
        self._validate_allocations(snapshot, allocations)

    def test_multi_path(self):
        # Network with two possible paths from A to C.
        snapshot = {
            "nodes": ["A", "B", "C"],
            "links": [
                {"source": "A", "destination": "B", "capacity": 5, "length": 4, "cost": 1.0},
                {"source": "B", "destination": "C", "capacity": 5, "length": 3, "cost": 0.5},
                {"source": "A", "destination": "C", "capacity": 10, "length": 2, "cost": 2.0},
            ],
            "commodities": [
                {"commodity_id": "commodity1", "origin": "A", "destination": "C", "demand": 8, "latency_weight": 1.5},
            ]
        }

        allocations = optimize_network_flow(snapshot)
        # Validate that total allocated flow from A equals the demand.
        total_flow = 0
        for alloc in allocations:
            if alloc["commodity_id"] == "commodity1" and alloc["source"] == "A":
                total_flow += alloc["flow"]
        self.assertEqual(total_flow, 8, msg="Total flow out of A should equal demand of 8.")
        self._validate_allocations(snapshot, allocations)

    def test_link_failure(self):
        # Network where one link has failed (capacity = 0)
        snapshot = {
            "nodes": ["A", "B", "C"],
            "links": [
                {"source": "A", "destination": "B", "capacity": 0, "length": 4, "cost": 1.0},  # failed link
                {"source": "A", "destination": "C", "capacity": 10, "length": 2, "cost": 2.0},
                {"source": "B", "destination": "C", "capacity": 5, "length": 3, "cost": 0.5},
            ],
            "commodities": [
                {"commodity_id": "commodity1", "origin": "A", "destination": "C", "demand": 6, "latency_weight": 1.0},
            ]
        }

        allocations = optimize_network_flow(snapshot)
        # Check that no allocation uses the failed link A->B.
        for alloc in allocations:
            self.assertFalse(alloc["source"] == "A" and alloc["destination"] == "B",
                             msg="Allocation should not use failed link A->B.")
        # Validate allocations against conservation and capacity.
        self._validate_allocations(snapshot, allocations)

    def test_flow_conservation(self):
        # More complex network to test flow conservation at intermediate nodes.
        snapshot = {
            "nodes": ["A", "B", "C", "D"],
            "links": [
                {"source": "A", "destination": "B", "capacity": 10, "length": 3, "cost": 1.0},
                {"source": "B", "destination": "C", "capacity": 10, "length": 4, "cost": 1.0},
                {"source": "A", "destination": "D", "capacity": 5, "length": 2, "cost": 2.0},
                {"source": "D", "destination": "C", "capacity": 5, "length": 3, "cost": 1.5},
                {"source": "B", "destination": "D", "capacity": 5, "length": 1, "cost": 0.5}
            ],
            "commodities": [
                {"commodity_id": "commodity1", "origin": "A", "destination": "C", "demand": 5, "latency_weight": 1.2},
            ]
        }

        allocations = optimize_network_flow(snapshot)
        # Validate flow conservation for commodity1 at each node.
        self._validate_allocations(snapshot, allocations)

    def test_over_capacity(self):
        # Network where multiple commodities share links, ensuring aggregated flow does not exceed link capacity.
        snapshot = {
            "nodes": ["A", "B", "C", "D"],
            "links": [
                {"source": "A", "destination": "B", "capacity": 8, "length": 3, "cost": 1.0},
                {"source": "B", "destination": "C", "capacity": 8, "length": 4, "cost": 1.0},
                {"source": "A", "destination": "D", "capacity": 5, "length": 2, "cost": 2.0},
                {"source": "D", "destination": "C", "capacity": 5, "length": 3, "cost": 1.5}
            ],
            "commodities": [
                {"commodity_id": "commodity1", "origin": "A", "destination": "C", "demand": 6, "latency_weight": 1.0},
                {"commodity_id": "commodity2", "origin": "A", "destination": "C", "demand": 4, "latency_weight": 1.5}
            ]
        }

        allocations = optimize_network_flow(snapshot)
        # For each link, validate that sum of flows from both commodities does not exceed capacity.
        self._validate_allocations(snapshot, allocations)

if __name__ == '__main__':
    unittest.main()