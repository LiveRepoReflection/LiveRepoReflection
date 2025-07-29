#[cfg(test)]
mod tests {
    use hyperspace_path::find_shortest_path;

    // Test with an empty graph should return None.
    #[test]
    fn test_no_route() {
        let initial_routes: Vec<(String, String, u32)> = Vec::new();
        let fluctuations: Vec<(u64, String, String, i32)> = Vec::new();
        assert_eq!(
            find_shortest_path(initial_routes, fluctuations, "Earth", "Mars", 0),
            None
        );
    }

    // Test a single route with no fluctuations.
    #[test]
    fn test_single_route_no_fluctuation() {
        let initial_routes = vec![
            ("Earth".to_string(), "Mars".to_string(), 10)
        ];
        let fluctuations = vec![];
        assert_eq!(
            find_shortest_path(initial_routes.clone(), fluctuations.clone(), "Earth", "Mars", 0),
            Some(10)
        );
        // Query at a later time should still have the same travel time.
        assert_eq!(
            find_shortest_path(initial_routes, fluctuations, "Earth", "Mars", 100),
            Some(10)
        );
    }

    // Test a single route with a fluctuation event that decreases the travel time.
    #[test]
    fn test_single_route_with_fluctuation() {
        let initial_routes = vec![
            ("Earth".to_string(), "Mars".to_string(), 10)
        ];
        // At t=5, reduce travel time by 5 (10 -> 5).
        let fluctuations = vec![
            (5, "Earth".to_string(), "Mars".to_string(), -5)
        ];
        // Before the event takes effect.
        assert_eq!(
            find_shortest_path(initial_routes.clone(), fluctuations.clone(), "Earth", "Mars", 4),
            Some(10)
        );
        // At and after t=5.
        assert_eq!(
            find_shortest_path(initial_routes, fluctuations, "Earth", "Mars", 5),
            Some(5)
        );
    }

    // Test a more complex graph with a fluctuation affecting one of the alternative routes.
    #[test]
    fn test_complex_graph_with_fluctuation() {
        // Graph:
        // A -> B: 3
        // B -> D: 4
        // A -> C: 10
        // C -> D: 1
        // A -> D: 15
        let initial_routes = vec![
            ("A".to_string(), "B".to_string(), 3),
            ("B".to_string(), "D".to_string(), 4),
            ("A".to_string(), "C".to_string(), 10),
            ("C".to_string(), "D".to_string(), 1),
            ("A".to_string(), "D".to_string(), 15),
        ];
        // At t=10, route A->C decreases by 8 (10 -> 2).
        let fluctuations = vec![
            (10, "A".to_string(), "C".to_string(), -8)
        ];
        // At time 9: fluctuation not applied, best path is A->B->D (3+4=7).
        assert_eq!(
            find_shortest_path(initial_routes.clone(), fluctuations.clone(), "A", "D", 9),
            Some(7)
        );
        // At time 10: fluctuation applied, best path is A->C->D (2+1=3).
        assert_eq!(
            find_shortest_path(initial_routes, fluctuations, "A", "D", 10),
            Some(3)
        );
    }

    // Test that multiple fluctuations on the same route cap the travel time at zero.
    #[test]
    fn test_fluctuation_capping() {
        let initial_routes = vec![
            ("X".to_string(), "Y".to_string(), 5)
        ];
        // At t=1, reduce travel time by 3 (5 -> 2).
        // At t=2, reduce travel time by 5 (would become -3, so cap at 0).
        let fluctuations = vec![
            (1, "X".to_string(), "Y".to_string(), -3),
            (2, "X".to_string(), "Y".to_string(), -5)
        ];
        // Before any fluctuation.
        assert_eq!(
            find_shortest_path(initial_routes.clone(), fluctuations.clone(), "X", "Y", 0),
            Some(5)
        );
        // After first event.
        assert_eq!(
            find_shortest_path(initial_routes.clone(), fluctuations.clone(), "X", "Y", 1),
            Some(2)
        );
        // After both events.
        assert_eq!(
            find_shortest_path(initial_routes, fluctuations, "X", "Y", 2),
            Some(0)
        );
    }

    // Test when the destination is unreachable.
    #[test]
    fn test_unreachable_destination() {
        let initial_routes = vec![
            ("A".to_string(), "B".to_string(), 10)
        ];
        let fluctuations: Vec<(u64, String, String, i32)> = Vec::new();
        assert_eq!(
            find_shortest_path(initial_routes, fluctuations, "A", "C", 0),
            None
        );
    }

    // Test a graph with multiple routes and fluctuations affecting different edges.
    #[test]
    fn test_multiple_routes_and_fluctuations() {
        // Graph:
        // P -> Q: 8
        // P -> R: 4
        // R -> Q: 5
        // Q -> S: 7
        // R -> S: 12
        let initial_routes = vec![
            ("P".to_string(), "Q".to_string(), 8),
            ("P".to_string(), "R".to_string(), 4),
            ("R".to_string(), "Q".to_string(), 5),
            ("Q".to_string(), "S".to_string(), 7),
            ("R".to_string(), "S".to_string(), 12),
        ];
        // Fluctuations:
        // At t=3, P -> Q decreases by 4 (8 -> 4).
        // At t=6, R -> S decreases by 5 (12 -> 7).
        let fluctuations = vec![
            (3, "P".to_string(), "Q".to_string(), -4),
            (6, "R".to_string(), "S".to_string(), -5),
        ];
        // At time 2: No fluctuations active.
        // Best path: P->Q->S = 8+7=15.
        assert_eq!(
            find_shortest_path(initial_routes.clone(), fluctuations.clone(), "P", "S", 2),
            Some(15)
        );
        // At time 3: P -> Q updated to 4, best path: P->Q->S = 4+7=11.
        assert_eq!(
            find_shortest_path(initial_routes.clone(), fluctuations.clone(), "P", "S", 3),
            Some(11)
        );
        // At time 6: Both fluctuations active.
        // Possibilities: P->R->S = 4+7=11 or P->Q->S = 4+7=11.
        assert_eq!(
            find_shortest_path(initial_routes, fluctuations, "P", "S", 6),
            Some(11)
        );
    }
}