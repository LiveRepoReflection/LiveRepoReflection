use supply_routes::{Warehouse, DistributionCenter, Edge, Problem, FlowResult, optimize_routes};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_feasible() {
        // One warehouse with 10 units supply and one distribution center with 10 units demand.
        // A direct edge exists with capacity 10, cost 5, and delay 10.
        // Truck limit is 10 so that exactly 10 trucks can be used.
        let warehouse = Warehouse { id: 0, supply: 10 };
        let distribution_center = DistributionCenter { id: 1, demand: 10, time_window: (0, 100) };
        let edge = Edge { from: 0, to: 1, capacity: 10, cost: 5, delay: 10 };
        let problem = Problem {
            warehouses: vec![warehouse],
            distribution_centers: vec![distribution_center],
            edges: vec![edge],
            truck_limit: 10,
        };

        let result = optimize_routes(problem);
        assert!(result.is_ok());
        let flow_result = result.unwrap();
        // Expected total cost is 10 trucks * 5 cost = 50.
        assert_eq!(flow_result.total_cost, 50);
        // Verify that the flow from warehouse 0 to distribution center 1 is exactly 10.
        let flow_edge = flow_result.flows.iter().find(|f| f.from == 0 && f.to == 1);
        assert!(flow_edge.is_some());
        assert_eq!(flow_edge.unwrap().flow, 10);
    }

    #[test]
    fn test_multiple_routes() {
        // Two warehouses and two distribution centers with multiple routes.
        // Warehouse 0: supply 10, Warehouse 1: supply 15.
        // Distribution Center 2: demand 12, Distribution Center 3: demand 13.
        // Four edges are provided with different capacities, costs, and delays.
        // Truck limit is 25 which matches total demand.
        let warehouse0 = Warehouse { id: 0, supply: 10 };
        let warehouse1 = Warehouse { id: 1, supply: 15 };
        let dc2 = DistributionCenter { id: 2, demand: 12, time_window: (0, 100) };
        let dc3 = DistributionCenter { id: 3, demand: 13, time_window: (0, 100) };
        let edges = vec![
            Edge { from: 0, to: 2, capacity: 10, cost: 4, delay: 20 },
            Edge { from: 0, to: 3, capacity: 5, cost: 6, delay: 30 },
            Edge { from: 1, to: 2, capacity: 10, cost: 7, delay: 25 },
            Edge { from: 1, to: 3, capacity: 15, cost: 3, delay: 15 },
        ];
        let problem = Problem {
            warehouses: vec![warehouse0, warehouse1],
            distribution_centers: vec![dc2, dc3],
            edges,
            truck_limit: 25,
        };

        let result = optimize_routes(problem);
        assert!(result.is_ok());
        let flow_result = result.unwrap();
        // Expected optimal cost determined by optimal routing is 93.
        assert_eq!(flow_result.total_cost, 93);
        // Verify that distribution center 2 obtains exactly 12 trucks.
        let flow_into_dc2: i32 = flow_result
            .flows
            .iter()
            .filter(|f| f.to == 2)
            .map(|f| f.flow)
            .sum();
        assert_eq!(flow_into_dc2, 12);
        // Verify that distribution center 3 obtains exactly 13 trucks.
        let flow_into_dc3: i32 = flow_result
            .flows
            .iter()
            .filter(|f| f.to == 3)
            .map(|f| f.flow)
            .sum();
        assert_eq!(flow_into_dc3, 13);
    }

    #[test]
    fn test_infeasible_truck_limit() {
        // One warehouse with 10 supply and one distribution center with 10 demand.
        // Truck limit is insufficient (5 instead of 10), hence the problem is infeasible.
        let warehouse = Warehouse { id: 0, supply: 10 };
        let distribution_center = DistributionCenter { id: 1, demand: 10, time_window: (0, 100) };
        let edge = Edge { from: 0, to: 1, capacity: 10, cost: 5, delay: 10 };
        let problem = Problem {
            warehouses: vec![warehouse],
            distribution_centers: vec![distribution_center],
            edges: vec![edge],
            truck_limit: 5,
        };

        let result = optimize_routes(problem);
        assert!(result.is_err());
    }

    #[test]
    fn test_infeasible_time_window() {
        // One warehouse with 10 supply and one distribution center with 10 demand.
        // The distribution center has a time window [0, 5] which cannot be attained
        // because the only edge has a delay of 10.
        let warehouse = Warehouse { id: 0, supply: 10 };
        let distribution_center = DistributionCenter { id: 1, demand: 10, time_window: (0, 5) };
        let edge = Edge { from: 0, to: 1, capacity: 10, cost: 5, delay: 10 };
        let problem = Problem {
            warehouses: vec![warehouse],
            distribution_centers: vec![distribution_center],
            edges: vec![edge],
            truck_limit: 10,
        };

        let result = optimize_routes(problem);
        assert!(result.is_err());
    }
}