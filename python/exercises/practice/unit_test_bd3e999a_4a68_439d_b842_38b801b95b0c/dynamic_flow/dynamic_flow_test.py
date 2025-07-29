import unittest
from dynamic_flow import solve_dynamic_flow

def compute_effective_capacity(edge, t, init_caps, events):
    # Determine effective capacity for an edge at time t using initial capacity and events
    effective = init_caps[edge][t]
    # Consider events in time order: if an event for this edge occurred at or before time t, update effective capacity
    for ev in sorted(events, key=lambda x: x[1]):
        e, event_time, new_cap = ev
        if e == edge and event_time <= t:
            effective = new_cap
    return effective

def validate_solution(V, E, init_caps, commodities, events, T, flow):
    # Check: if flow is empty, then the instance should be unsolvable.
    # Otherwise, check all constraints.

    # Verify that flow is a dictionary.
    if not isinstance(flow, dict):
        return False, "Returned flow is not a dictionary"

    # For each key, check correct formatting: key = (commodity_index, edge, time)
    for key in flow:
        if not (isinstance(key, tuple) and len(key) == 3):
            return False, f"Invalid key format: {key}"
        k, edge, t = key
        if not (isinstance(edge, tuple) and len(edge) == 2):
            return False, f"Invalid edge format in key: {key}"
        if not (isinstance(t, int) and 0 <= t < T):
            return False, f"Time index out of range in key: {key}"
        if not (isinstance(k, int) and 0 <= k < len(commodities)):
            return False, f"Commodity index out of range in key: {key}"
        # Flow values must be non-negative numbers
        if flow[key] < 0:
            return False, f"Negative flow for key: {key}"

    # Capacity Constraints: For each edge and each time t, total flow from all commodities must be <= effective capacity.
    for e in E:
        for t in range(T):
            total_flow = 0
            for key, amount in flow.items():
                _, edge, time_index = key
                if edge == e and time_index == t:
                    total_flow += amount
            effective_cap = compute_effective_capacity(e, t, init_caps, events)
            if total_flow > effective_cap + 1e-6:
                return False, f"Capacity exceeded on edge {e} at time {t}: total flow {total_flow}, effective capacity {effective_cap}"

    # Flow Conservation & Demand Satisfaction:
    # We'll sum flow over all time steps.
    # For each commodity, compute net flow at each vertex:
    # net_flow[v] = (total outflow from v) - (total inflow into v)
    # For source: should equal demand, for destination: should equal -demand, and for others: 0.
    for k, (src, dst, demand) in enumerate(commodities):
        net_flow = {v: 0 for v in V}
        for key, amount in flow.items():
            com, edge, time_index = key
            if com != k:
                continue
            u, v = edge
            net_flow[u] += amount
            net_flow[v] -= amount
        # Check values at each vertex.
        for v in V:
            if v == src:
                # For source, net outflow should equal demand
                if abs(net_flow[v] - demand) > 1e-6:
                    return False, f"Demand not met at source {src} for commodity {k}: expected {demand}, got {net_flow[v]}"
            elif v == dst:
                # For destination, net inflow should equal demand (net_flow negative)
                if abs(net_flow[v] + demand) > 1e-6:
                    return False, f"Demand not met at destination {dst} for commodity {k}: expected {-demand}, got {net_flow[v]}"
            else:
                if abs(net_flow[v]) > 1e-6:
                    return False, f"Flow conservation violated at vertex {v} for commodity {k}: net flow {net_flow[v]}"
    return True, "Feasible solution"

class TestDynamicFlow(unittest.TestCase):
    def test_simple_flow(self):
        # Simple scenario: single edge, single commodity, no events.
        V = [0, 1]
        E = [(0, 1)]
        T = 3
        capacities = {
            (0, 1): [5, 5, 5]
        }
        commodities = [
            (0, 1, 3)  # commodity 0: demand 3 from vertex 0 to 1
        ]
        events = []
        flow = solve_dynamic_flow(V, E, capacities, commodities, events, T)
        valid, msg = validate_solution(V, E, capacities, commodities, events, T, flow)
        self.assertTrue(valid, msg)

    def test_dynamic_event(self):
        # Scenario with a capacity change event.
        V = [0, 1]
        E = [(0, 1)]
        T = 3
        capacities = {
            (0, 1): [5, 5, 5]
        }
        # At time index 1, capacity changes to 2 (and remains 2 afterwards)
        events = [((0, 1), 1, 2)]
        # Commodity with demand 4 that must be split over time steps.
        commodities = [
            (0, 1, 4)
        ]
        flow = solve_dynamic_flow(V, E, capacities, commodities, events, T)
        valid, msg = validate_solution(V, E, capacities, commodities, events, T, flow)
        self.assertTrue(valid, msg)

    def test_unsolvable(self):
        # Scenario where demand exceeds available capacity.
        V = [0, 1]
        E = [(0, 1)]
        T = 2
        capacities = {
            (0, 1): [1, 1]
        }
        commodities = [
            (0, 1, 5)  # demand is too high to be met
        ]
        events = []
        flow = solve_dynamic_flow(V, E, capacities, commodities, events, T)
        self.assertEqual(flow, {}, "Expected an empty dictionary for unsolvable flow, but got a non-empty solution.")

    def test_multi_commodity(self):
        # Scenario with multiple commodities and multiple paths.
        V = [0, 1, 2, 3]
        E = [(0, 1), (1, 3), (0, 2), (2, 3)]
        T = 3
        capacities = {
            (0, 1): [3, 3, 3],
            (1, 3): [3, 3, 3],
            (0, 2): [2, 2, 2],
            (2, 3): [2, 2, 2]
        }
        # Two commodities from 0 to 3 with different demands.
        commodities = [
            (0, 3, 3),  # commodity 0: demand 3
            (0, 3, 2)   # commodity 1: demand 2
        ]
        events = []
        flow = solve_dynamic_flow(V, E, capacities, commodities, events, T)
        valid, msg = validate_solution(V, E, capacities, commodities, events, T, flow)
        self.assertTrue(valid, msg)

    def test_cycle_graph(self):
        # Scenario with a cycle in the graph.
        V = [0, 1, 2]
        E = [(0, 1), (1, 2), (2, 0)]
        T = 4
        capacities = {
            (0, 1): [4, 4, 4, 4],
            (1, 2): [4, 4, 4, 4],
            (2, 0): [4, 4, 4, 4]
        }
        # Commodity from 0 to 2
        commodities = [
            (0, 2, 4)
        ]
        # Adding an event that changes capacity mid-simulation on edge (1, 2)
        events = [((1, 2), 2, 2)]
        flow = solve_dynamic_flow(V, E, capacities, commodities, events, T)
        valid, msg = validate_solution(V, E, capacities, commodities, events, T, flow)
        self.assertTrue(valid, msg)

if __name__ == '__main__':
    unittest.main()