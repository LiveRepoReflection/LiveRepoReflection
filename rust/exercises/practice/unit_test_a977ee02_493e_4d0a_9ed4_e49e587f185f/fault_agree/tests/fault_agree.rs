use fault_agree::ConsensusSystem;

#[test]
fn test_basic_consensus() {
    // Create a system with 3 nodes and fault tolerance f = 1
    let mut system = ConsensusSystem::new(3, 1);
    system.propose(0, "Event A".to_string());
    system.propose(1, "Event B".to_string());
    system.propose(2, "Event C".to_string());
    system.run_consensus();

    let log0 = system.get_log(0).expect("Missing log for node 0").clone();
    let log1 = system.get_log(1).expect("Missing log for node 1").clone();
    let log2 = system.get_log(2).expect("Missing log for node 2").clone();

    // All non-faulty nodes should have identical logs.
    assert_eq!(log0, log1);
    assert_eq!(log1, log2);

    // Verify that all events are present in the final consensus.
    let mut sorted_log = log0.clone();
    sorted_log.sort();
    let mut expected = vec!["Event A".to_string(), "Event B".to_string(), "Event C".to_string()];
    expected.sort();
    assert_eq!(sorted_log, expected);
}

#[test]
fn test_causal_ordering() {
    // Ensure that events proposed by the same node retain their causal (propositional) order.
    let mut system = ConsensusSystem::new(3, 1);
    system.propose(1, "First".to_string());
    system.propose(1, "Second".to_string());
    system.propose(0, "Alpha".to_string());
    system.propose(2, "Omega".to_string());
    system.run_consensus();

    for node in 0..3 {
        let log = system.get_log(node).expect("Missing node log");
        let pos_first = log.iter().position(|e| e == "First").expect("Missing 'First' event");
        let pos_second = log.iter().position(|e| e == "Second").expect("Missing 'Second' event");
        assert!(pos_first < pos_second, "Causal order violated in node {}", node);
    }
}

#[test]
fn test_duplicate_messages() {
    // Simulate duplicate network messages; the consensus should handle duplicates properly.
    let mut system = ConsensusSystem::new(4, 1);
    system.propose(0, "Duplicate".to_string());
    system.propose(0, "Duplicate".to_string());
    system.propose(1, "Unique".to_string());
    system.run_consensus();

    for node in 0..4 {
        let log = system.get_log(node).expect("Missing node log");
        let count_duplicate = log.iter().filter(|e| *e == "Duplicate").count();
        let count_unique = log.iter().filter(|e| *e == "Unique").count();
        assert_eq!(count_duplicate, 1, "Node {} has duplicate 'Duplicate' event", node);
        assert_eq!(count_unique, 1, "Node {} missing 'Unique' event", node);
        assert_eq!(log.len(), 2, "Unexpected log length for node {}", node);
    }
}

#[test]
fn test_out_of_order_proposals() {
    // Proposals are made out-of-order from different nodes;
    // after consensus, the events should appear in a consistent order across nodes.
    let mut system = ConsensusSystem::new(5, 2);
    system.propose(2, "Event2".to_string());
    system.propose(0, "Event0".to_string());
    system.propose(4, "Event4".to_string());
    system.propose(1, "Event1".to_string());
    system.propose(3, "Event3".to_string());
    system.run_consensus();

    let expected_sorted = vec![
        "Event0".to_string(), 
        "Event1".to_string(), 
        "Event2".to_string(), 
        "Event3".to_string(), 
        "Event4".to_string()
    ];

    for node in 0..5 {
        let mut log = system.get_log(node).expect("Missing node log").clone();
        log.sort();
        assert_eq!(log, expected_sorted, "Log mismatch for node {}", node);
    }
}

#[test]
fn test_fault_tolerance() {
    // Simulate a scenario where one node is faulty (i.e., it does not propose any events).
    let mut system = ConsensusSystem::new(4, 1);
    system.propose(0, "A".to_string());
    system.propose(1, "B".to_string());
    // Node 2 is faulty (no proposals made)
    system.propose(3, "C".to_string());
    system.run_consensus();

    let log0 = system.get_log(0).expect("Missing log for node 0").clone();
    let log1 = system.get_log(1).expect("Missing log for node 1").clone();
    let log3 = system.get_log(3).expect("Missing log for node 3").clone();

    assert_eq!(log0, log1);
    assert_eq!(log1, log3);

    let mut combined_log = log0.clone();
    combined_log.sort();
    let mut expected = vec!["A".to_string(), "B".to_string(), "C".to_string()];
    expected.sort();
    assert_eq!(combined_log, expected);
}

#[test]
fn test_heavy_load() {
    // Test the system under heavy load with multiple nodes and many proposals.
    let node_count = 7;
    let proposals_per_node = 50;
    let mut system = ConsensusSystem::new(node_count, 2);

    for node in 0..node_count {
        for i in 0..proposals_per_node {
            let event = format!("Node{}_Event{}", node, i);
            system.propose(node, event);
        }
    }
    system.run_consensus();

    let mut expected = Vec::new();
    for node in 0..node_count {
        for i in 0..proposals_per_node {
            expected.push(format!("Node{}_Event{}", node, i));
        }
    }
    expected.sort();

    for node in 0..node_count {
        let mut log = system.get_log(node).expect("Missing node log").clone();
        log.sort();
        assert_eq!(log, expected, "Mismatch in heavy load test for node {}", node);
    }
}