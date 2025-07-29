use adaptive_flow::{Simulation, Event};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_allocation() {
        // Network: two edges: (0 -> 1) capacity 10, (1 -> 2) capacity 10.
        // Initial request: id 1 from node 0 to node 2 with demand 8.
        let edges = vec![(0, 1, 10), (1, 2, 10)];
        let initial_requests = vec![(1, 0, 2, 8)];
        let mut sim = Simulation::new(edges, initial_requests);
        let alloc = sim.allocations();
        // With a single request and no bottleneck issues, the allocation should equal the request.
        assert_eq!(alloc, vec![(1, 8)]);
    }

    #[test]
    fn test_add_request() {
        // Start with one request.
        let edges = vec![(0, 1, 10), (1, 2, 10)];
        let initial_requests = vec![(1, 0, 2, 8)];
        let mut sim = Simulation::new(edges, initial_requests);
        let alloc_initial = sim.allocations();
        assert_eq!(alloc_initial, vec![(1, 8)]);

        // Process AddRequest event for request id 2 with demand 6.
        let event = Event::AddRequest {
            request_id: 2,
            source: 0,
            destination: 2,
            demand: 6,
        };
        let alloc = sim.process_event(event);
        // Proportional allocation rule:
        // Total demand = 8 + 6 = 14, capacity = 10.
        // Base allocation for request 1 = (8*10)/14 = 5 and for request 2 = (6*10)/14 = 4.
        // Sum of base = 9, remainder = 1 allocated to the lower request id.
        // Therefore, expected allocations: request 1 -> 5+1 = 6, request 2 -> 4.
        assert_eq!(alloc, vec![(1, 6), (2, 4)]);
    }

    #[test]
    fn test_update_request() {
        // Start with two requests.
        let edges = vec![(0, 1, 10), (1, 2, 10)];
        let initial_requests = vec![(1, 0, 2, 8), (2, 0, 2, 6)];
        let mut sim = Simulation::new(edges, initial_requests);
        let _ = sim.allocations();

        // Process UpdateRequest event: update request 1 to a new demand of 4.
        let event = Event::UpdateRequest {
            request_id: 1,
            demand: 4,
        };
        let alloc = sim.process_event(event);
        // Now, total demand = 4 (for req 1) + 6 (for req 2) = 10, which equals the capacity.
        // Expected allocation: request 1 -> 4, request 2 -> 6.
        assert_eq!(alloc, vec![(1, 4), (2, 6)]);
    }

    #[test]
    fn test_remove_request() {
        // Start with two requests.
        let edges = vec![(0, 1, 10), (1, 2, 10)];
        let initial_requests = vec![(1, 0, 2, 4), (2, 0, 2, 6)];
        let mut sim = Simulation::new(edges, initial_requests);
        let _ = sim.allocations();

        // Process RemoveRequest event: remove request id 2.
        let event = Event::RemoveRequest { request_id: 2 };
        let alloc = sim.process_event(event);
        // Only request 1 remains; allocation should be its full demand (4) as it is under capacity.
        assert_eq!(alloc, vec![(1, 4)]);
    }

    #[test]
    fn test_update_capacity() {
        // Start with one request.
        let edges = vec![(0, 1, 10), (1, 2, 10)];
        let initial_requests = vec![(1, 0, 2, 4)];
        let mut sim = Simulation::new(edges, initial_requests);
        let _ = sim.allocations();

        // Process UpdateCapacity event: update the capacity of edge (0,1) to 3.
        let event = Event::UpdateCapacity {
            source: 0,
            destination: 1,
            capacity: 3,
        };
        let alloc = sim.process_event(event);
        // The path capacity becomes min(3, 10) = 3.
        // Expected allocation for request 1 is the minimum of its demand and the bottleneck, which is 3.
        assert_eq!(alloc, vec![(1, 3)]);
    }

    #[test]
    fn test_complex_sequence() {
        // Initialize simulation with one request.
        let edges = vec![(0, 1, 10), (1, 2, 10)];
        let initial_requests = vec![(1, 0, 2, 8)];
        let mut sim = Simulation::new(edges, initial_requests);
        assert_eq!(sim.allocations(), vec![(1, 8)]);

        // 1. Add request 2: demand 6.
        let event = Event::AddRequest {
            request_id: 2,
            source: 0,
            destination: 2,
            demand: 6,
        };
        let alloc = sim.process_event(event);
        // Total demand = 8 + 6 = 14; capacity = 10.
        // Base: req1 = (8*10)/14 = 5, req2 = (6*10)/14 = 4; sum = 9, remainder = 1 to lower id (req1).
        // Expected: (1,6) and (2,4).
        assert_eq!(alloc, vec![(1, 6), (2, 4)]);

        // 2. Update request 1 to demand 4.
        let event = Event::UpdateRequest {
            request_id: 1,
            demand: 4,
        };
        let alloc = sim.process_event(event);
        // Now, total demand = 4 + 6 = 10, matching the capacity.
        // Expected allocation: (1,4) and (2,6).
        assert_eq!(alloc, vec![(1, 4), (2, 6)]);

        // 3. Remove request 2.
        let event = Event::RemoveRequest { request_id: 2 };
        let alloc = sim.process_event(event);
        // Only request 1 remains; allocation: (1,4).
        assert_eq!(alloc, vec![(1, 4)]);

        // 4. Update capacity on edge (0,1) to 3.
        let event = Event::UpdateCapacity {
            source: 0,
            destination: 1,
            capacity: 3,
        };
        let alloc = sim.process_event(event);
        // The bottleneck becomes 3. Expected allocation for request 1: min(4,3) = 3.
        assert_eq!(alloc, vec![(1, 3)]);

        // 5. Add request 3 with demand 3.
        let event = Event::AddRequest {
            request_id: 3,
            source: 0,
            destination: 2,
            demand: 3,
        };
        let alloc = sim.process_event(event);
        // Now, active requests: req1 with demand 4 and req3 with demand 3; capacity remains 3.
        // Total demand = 4 + 3 = 7.
        // Base allocation: req1 = (4*3)/7 = 1, req3 = (3*3)/7 = 1; sum = 2.
        // Remainder = 3 - 2 = 1, allocated to the lower request id (req1).
        // Expected: req1 gets 2 and req3 gets 1.
        assert_eq!(alloc, vec![(1, 2), (3, 1)]);
    }
}