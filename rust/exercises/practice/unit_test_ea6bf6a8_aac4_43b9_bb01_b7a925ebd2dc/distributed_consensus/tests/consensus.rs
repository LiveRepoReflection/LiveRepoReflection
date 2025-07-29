use std::thread;
use distributed_consensus;

#[test]
fn test_basic_consensus() {
    // Test that with all nodes having a default state (0) and a proposed value,
    // the consensus round sets all nodes to the proposed value.
    let num_nodes = 5;
    let initial_states = vec![0; num_nodes];
    let proposed_value = 10;
    let final_states = distributed_consensus::run_consensus_round(num_nodes, initial_states, proposed_value);
    assert_eq!(final_states.len(), num_nodes);
    for state in final_states {
        assert_eq!(state, 10, "Each node should have adopted the proposed value");
    }
}

#[test]
fn test_prior_value_override() {
    // When some nodes have a non-default prior accepted value, the consensus round
    // must adopt the highest such value instead of the newly proposed value.
    // Here, nodes 0 and 3 have prior values 7 and 5. Since 7 is the highest,
    // even though the client proposes 3, the consensus result should be 7.
    let num_nodes = 5;
    let initial_states = vec![7, 0, 0, 5, 0];
    let proposed_value = 3;
    let final_states = distributed_consensus::run_consensus_round(num_nodes, initial_states, proposed_value);
    assert_eq!(final_states.len(), num_nodes);
    for state in final_states {
        assert_eq!(state, 7, "Each node should have adopted the highest prior value (7)");
    }
}

#[test]
fn test_concurrent_execution() {
    // This test asserts that running consensus rounds concurrently results in
    // correct state updates for each independent round.
    let num_threads = 4;
    let mut handles = Vec::new();
    for _ in 0..num_threads {
        // Spawn each consensus round in a separate thread.
        let handle = thread::spawn(|| {
            let num_nodes = 5;
            let initial_states = vec![0, 0, 0, 0, 0];
            let proposed_value = 15;
            distributed_consensus::run_consensus_round(num_nodes, initial_states, proposed_value)
        });
        handles.push(handle);
    }
    for handle in handles {
        let final_states = handle.join().unwrap();
        assert_eq!(final_states.len(), 5);
        for state in final_states {
            assert_eq!(state, 15, "Concurrent consensus round should yield the proposed value for all nodes");
        }
    }
}

#[test]
fn test_stale_message_handling() {
    // This test simulates a scenario where nodes might have received
    // a higher proposal in an earlier round and then a stale lower proposal is issued.
    // The consensus round should honor the higher proposal id's value from previous rounds.
    // For simulation purposes, we assume that the initial state represents the value
    // accepted from a previous higher-proposal. Thus, even if the client proposes
    // a lower value, the nodes should converge on the previous value.
    let num_nodes = 5;
    // Nodes 1 and 4 have already accepted a high value (20), while others are at default.
    let initial_states = vec![0, 20, 0, 0, 20];
    let proposed_value = 5;
    let final_states = distributed_consensus::run_consensus_round(num_nodes, initial_states, proposed_value);
    assert_eq!(final_states.len(), num_nodes);
    for state in final_states {
        assert_eq!(state, 20, "Stale lower proposals should be overridden by the higher previously accepted value");
    }
}