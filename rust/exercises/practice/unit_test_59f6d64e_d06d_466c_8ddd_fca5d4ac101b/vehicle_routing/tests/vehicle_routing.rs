use std::collections::HashMap;
use vehicle_routing::{find_optimal_route, CityGraph, IntersectionId, RoadSegment, Route, Timestamp};

struct TestCityGraph {
    graph: HashMap<IntersectionId, Vec<RoadSegment>>,
}

impl TestCityGraph {
    fn new() -> Self {
        Self {
            graph: HashMap::new(),
        }
    }

    fn add_edge(&mut self, from: IntersectionId, to: IntersectionId, length: f64, congestion: u8) {
        let segment = RoadSegment { from, to, length, congestion };
        self.graph.entry(from).or_insert_with(Vec::new).push(segment);
    }
}

impl CityGraph for TestCityGraph {
    fn get_outgoing_edges(&self, intersection_id: IntersectionId) -> &[RoadSegment] {
        self.graph.get(&intersection_id).map(|v| v.as_slice()).unwrap_or(&[])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_same_intersection() {
        // When start and end are the same, the route should have one node with zero travel time/cost.
        let graph = TestCityGraph::new();
        let start: IntersectionId = 1;
        let end: IntersectionId = 1;
        let current_time: Timestamp = 1000;
        let deadline: Timestamp = 2000;
        let penalty_weight = 1.0;

        let result = find_optimal_route(&graph, start, end, deadline, current_time, penalty_weight);
        assert!(result.is_some(), "Expected a valid route when start and end are the same");
        let route: Route = result.unwrap();
        assert_eq!(route.path, vec![start]);
        assert!((route.total_travel_time - 0.0).abs() < 1e-6, "Expected zero travel time");
        assert!((route.total_cost - 0.0).abs() < 1e-6, "Expected zero cost");
    }

    #[test]
    fn test_simple_route() {
        // Create a simple graph with a direct path from 1 -> 2 -> 3.
        let mut graph = TestCityGraph::new();
        // At congestion 0, travel time = length / 30 m/s.
        // For a length of 300 m: travel time = 300 / 30 = 10 seconds.
        graph.add_edge(1, 2, 300.0, 0);
        graph.add_edge(2, 3, 300.0, 0);

        let start: IntersectionId = 1;
        let end: IntersectionId = 3;
        let current_time: Timestamp = 0;
        let deadline: Timestamp = 25; // Enough time before deadline.
        let penalty_weight = 1.0;

        let result = find_optimal_route(&graph, start, end, deadline, current_time, penalty_weight);
        assert!(result.is_some(), "Expected valid route for simple graph");
        let route: Route = result.unwrap();
        assert_eq!(route.path, vec![1, 2, 3]);
        let expected_travel_time = 10.0 + 10.0; // 20 seconds total.
        assert!((route.total_travel_time - expected_travel_time).abs() < 1e-6, "Travel time mismatch");
        // Since arrival time (20) is before deadline (25), no lateness penalty.
        assert!((route.total_cost - expected_travel_time).abs() < 1e-6, "Cost mismatch for simple route");
    }

    #[test]
    fn test_no_route() {
        // Create a graph where there is no path from start to destination.
        let mut graph = TestCityGraph::new();
        graph.add_edge(1, 2, 100.0, 0);
        // No edge from 2 leads to destination 3.
        let start: IntersectionId = 1;
        let end: IntersectionId = 3;
        let current_time: Timestamp = 0;
        let deadline: Timestamp = 100;
        let penalty_weight = 1.0;

        let result = find_optimal_route(&graph, start, end, deadline, current_time, penalty_weight);
        assert!(result.is_none(), "Expected no route when destination is unreachable");
    }

    #[test]
    fn test_lateness_penalty() {
        // Build a graph where the total travel time exceeds the request deadline.
        let mut graph = TestCityGraph::new();
        // Two edges: each with travel time 600/30 = 20 seconds, total travel time = 40 seconds.
        graph.add_edge(1, 2, 600.0, 0);
        graph.add_edge(2, 3, 600.0, 0);

        let start: IntersectionId = 1;
        let end: IntersectionId = 3;
        let current_time: Timestamp = 0;
        let deadline: Timestamp = 30; // Deadline is shorter than travel time.
        let penalty_weight = 2.0;

        let result = find_optimal_route(&graph, start, end, deadline, current_time, penalty_weight);
        assert!(result.is_some(), "Expected valid route even when lateness occurs");
        let route: Route = result.unwrap();
        // Total travel time = 40 seconds, lateness = 10 seconds.
        let lateness = 10.0;
        let expected_cost = 40.0 + penalty_weight * lateness;
        assert!((route.total_travel_time - 40.0).abs() < 1e-6, "Total travel time mismatch");
        assert!((route.total_cost - expected_cost).abs() < 1e-6, "Total cost mismatch with lateness penalty");
    }

    #[test]
    fn test_dynamic_congestion() {
        // Create two potential routes from 1 to 3:
        // Route A: 1 -> 2 -> 3 with zero congestion.
        // Route B: 1 -> 4 -> 3 where 1 -> 4 has high congestion, making this route slower.
        let mut graph = TestCityGraph::new();
        // Route A edges (congestion 0): travel time = 300/30 = 10 seconds each.
        graph.add_edge(1, 2, 300.0, 0);
        graph.add_edge(2, 3, 300.0, 0);
        // Route B edges: first edge with high congestion.
        // For 1->4: effective speed = 30 * (1 - 70/100) = 9 m/s, travel time = 300/9 ≈ 33.33 seconds.
        graph.add_edge(1, 4, 300.0, 70);
        // Second edge of Route B has congestion 0.
        graph.add_edge(4, 3, 300.0, 0);

        let start: IntersectionId = 1;
        let end: IntersectionId = 3;
        let current_time: Timestamp = 0;
        let deadline: Timestamp = 50;
        let penalty_weight = 1.0;

        let result = find_optimal_route(&graph, start, end, deadline, current_time, penalty_weight);
        assert!(result.is_some(), "Expected valid route considering dynamic congestion");
        let route: Route = result.unwrap();
        // The optimal route should be via Route A: 1 -> 2 -> 3.
        assert_eq!(route.path, vec![1, 2, 3]);
        let expected_travel_time = 10.0 + 10.0; // 20 seconds total.
        assert!((route.total_travel_time - expected_travel_time).abs() < 1e-6, "Travel time mismatch in dynamic congestion case");
    }
}