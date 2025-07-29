use std::collections::HashMap;

use net_control::network::Network;
use net_control::simulation::{Simulation, SimulationResult, Traffic};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_network() {
        // Create an empty network and run simulation with no traffic.
        let network = Network::new();
        let traffic: Vec<Traffic> = Vec::new();
        let mut simulation = Simulation::new(network, traffic, 10);
        let result: SimulationResult = simulation.run();

        // Expect no deliveries, no drops and zero utilization.
        assert_eq!(result.total_dropped, 0);
        assert!(result.delivered.is_empty());
        assert!(result.avg_latency.is_empty());
        assert_eq!(result.max_utilization, 0.0);
    }

    #[test]
    fn test_simple_delivery() {
        // Create a simple network with two routers and a single link
        // with high enough capacity for traffic to pass unhindered.
        let mut network = Network::new();
        network.add_router("A");
        network.add_router("B");
        network.add_link("A", "B", 100);

        // Create one traffic flow from A to B with a rate of 50 packets per time step.
        let traffic = vec![Traffic::new("A", "B", 50)];

        // Simulate for 10 time steps.
        let mut simulation = Simulation::new(network, traffic, 10);
        let result = simulation.run();

        // Expect that all packets are delivered.
        // 50 packets per step over 10 steps gives total 500 packets delivered.
        let delivered = result
            .delivered
            .iter()
            .find(|(src, dst, _)| src == "A" && dst == "B")
            .map(|(_, _, count)| *count)
            .unwrap_or(0);
        assert_eq!(delivered, 500);
        // No packet should be dropped.
        assert_eq!(result.total_dropped, 0);
        // Maximum link utilization should be below or equal to 1.0.
        assert!(result.max_utilization <= 1.0);
        // Average latency for delivered packets should be positive.
        let latency = result
            .avg_latency
            .iter()
            .find(|(src, dst, _)| src == "A" && dst == "B")
            .map(|(_, _, lat)| *lat)
            .unwrap_or(0.0);
        assert!(latency > 0.0);
    }

    #[test]
    fn test_congestion() {
        // Create a network with two routers connected by a link with limited capacity.
        let mut network = Network::new();
        network.add_router("A");
        network.add_router("B");
        // Set capacity less than the traffic rate to induce congestion.
        network.add_link("A", "B", 30);

        // Set a traffic flow from A to B at a rate higher than the link capacity.
        let traffic = vec![Traffic::new("A", "B", 50)];

        // Run simulation for 5 time steps.
        let mut simulation = Simulation::new(network, traffic, 5);
        let result = simulation.run();

        // Delivered packets cannot exceed link capacity per step (i.e., at most 30 per step).
        let delivered = result
            .delivered
            .iter()
            .find(|(src, dst, _)| src == "A" && dst == "B")
            .map(|(_, _, count)| *count)
            .unwrap_or(0);
        assert!(delivered <= 30 * 5);

        // Since the traffic rate is higher, some packets should be dropped.
        assert!(result.total_dropped > 0);

        // The link should have reached or exceeded full utilization.
        assert!(result.max_utilization >= 1.0);
    }

    #[test]
    fn test_fairness_among_flows() {
        // Create a network where two flows share a common bottleneck.
        // Network topology:
        //   A -> X -> B
        //   A -> X -> C
        // The common link A->X is the bottleneck.
        let mut network = Network::new();
        network.add_router("A");
        network.add_router("X");
        network.add_router("B");
        network.add_router("C");

        // Link A -> X has limited capacity to enforce fairness between flows.
        network.add_link("A", "X", 100);
        // Other links have sufficient capacity.
        network.add_link("X", "B", 100);
        network.add_link("X", "C", 100);

        // Two traffic flows sharing the common link A->X.
        let traffic = vec![
            Traffic::new("A", "B", 80),
            Traffic::new("A", "C", 80),
        ];

        // Run simulation for 10 time steps.
        let mut simulation = Simulation::new(network, traffic, 10);
        let result = simulation.run();

        // Since the common link (A->X) can only carry 100 packets per step,
        // the total capacity over 10 steps is 1000 packets.
        // Ideally, fairness would allow each flow near 500 packets delivered.
        let delivered_flow1 = result
            .delivered
            .iter()
            .find(|(src, dst, _)| src == "A" && dst == "B")
            .map(|(_, _, count)| *count)
            .unwrap_or(0);
        let delivered_flow2 = result
            .delivered
            .iter()
            .find(|(src, dst, _)| src == "A" && dst == "C")
            .map(|(_, _, count)| *count)
            .unwrap_or(0);

        // Check that each flow delivered a substantial number of packets,
        // indicating that the bandwidth is shared in a roughly fair manner.
        assert!(delivered_flow1 >= 400, "Flow A->B delivered less than expected");
        assert!(delivered_flow2 >= 400, "Flow A->C delivered less than expected");

        // Both flows should report a positive average latency.
        let latency_flow1 = result
            .avg_latency
            .iter()
            .find(|(src, dst, _)| src == "A" && dst == "B")
            .map(|(_, _, lat)| *lat)
            .unwrap_or(0.0);
        let latency_flow2 = result
            .avg_latency
            .iter()
            .find(|(src, dst, _)| src == "A" && dst == "C")
            .map(|(_, _, lat)| *lat)
            .unwrap_or(0.0);
        assert!(latency_flow1 > 0.0);
        assert!(latency_flow2 > 0.0);
    }
}