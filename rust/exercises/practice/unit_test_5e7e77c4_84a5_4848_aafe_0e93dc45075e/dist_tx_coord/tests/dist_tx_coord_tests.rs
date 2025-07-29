use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use dist_tx_coord::{Coordinator, Node, Operation, TransactionOutcome};

// Helper function to initialize a coordinator with a set of nodes.
fn setup_coordinator(nodes: Vec<Node>, timeout: Duration) -> Coordinator {
    let mut coord = Coordinator::new(timeout);
    for node in nodes.into_iter() {
        coord.add_node(node);
    }
    coord
}

#[test]
fn test_commit_transaction() {
    // All nodes can commit the increment operation.
    // We start with state 10 in each node and increment by 5.
    let nodes = vec![
        Node::new(1, 10, 0.0, 0.0), 
        Node::new(2, 10, 0.0, 0.0),
        Node::new(3, 10, 0.0, 0.0)
    ];
    let timeout = Duration::from_millis(500);
    let coord = setup_coordinator(nodes, timeout);
    
    let node_ids = vec![1, 2, 3];
    let outcome = coord.execute_transaction(Operation::Increment, 5, node_ids.clone());
    
    assert_eq!(outcome, TransactionOutcome::Committed);
    
    // Check updated states for each node.
    for node_id in node_ids.into_iter() {
        let state = coord.get_node_state(node_id);
        assert_eq!(state, 15);
    }
}

#[test]
fn test_abort_transaction_due_to_insufficient_state() {
    // One node does not have enough state to support a decrement operation.
    // Node 2 only has 3 while the decrement operation will subtract 5.
    let nodes = vec![
        Node::new(1, 10, 0.0, 0.0), 
        Node::new(2, 3, 0.0, 0.0),  // insufficient state for decrement.
        Node::new(3, 10, 0.0, 0.0)
    ];
    let timeout = Duration::from_millis(500);
    let coord = setup_coordinator(nodes, timeout);
    
    let node_ids = vec![1, 2, 3];
    let outcome = coord.execute_transaction(Operation::Decrement, 5, node_ids.clone());
    
    assert_eq!(outcome, TransactionOutcome::Aborted);
    
    // Check that none of the nodes have changed their state.
    for node_id in node_ids.into_iter() {
        let state = coord.get_node_state(node_id);
        if node_id == 2 {
            assert_eq!(state, 3);
        } else {
            assert_eq!(state, 10);
        }
    }
}

#[test]
fn test_timeout_transaction() {
    // Simulate a slow node by using a delay longer than the coordinator timeout.
    // The slow node will force a timeout, causing the transaction to abort.
    let nodes = vec![
        Node::new(1, 20, 0.0, 0.0),
        Node::new(2, 20, 0.0, 0.0),
        // Node 3 will delay its prepare response.
        Node::new_with_delay(3, 20, 0.0, 0.0, Duration::from_millis(600))
    ];
    let timeout = Duration::from_millis(300);
    let coord = setup_coordinator(nodes, timeout);
    
    let node_ids = vec![1, 2, 3];
    let start = Instant::now();
    let outcome = coord.execute_transaction(Operation::Increment, 5, node_ids.clone());
    let duration = start.elapsed();
    
    // Transaction should abort because of timeout.
    assert_eq!(outcome, TransactionOutcome::Aborted);
    // Ensure that the transaction did not wait for the slow node beyond a reasonable timeout.
    assert!(duration < Duration::from_millis(1000));
    
    // Check that none of the nodes have their state changed.
    for node_id in node_ids.into_iter() {
        let state = coord.get_node_state(node_id);
        assert_eq!(state, 20);
    }
}

#[test]
fn test_concurrent_transactions() {
    // Test handling of multiple concurrent transactions.
    // We create a coordinator shared among threads, running transactions concurrently.
    let nodes = vec![
        Node::new(1, 100, 0.0, 0.0),
        Node::new(2, 100, 0.0, 0.0),
        Node::new(3, 100, 0.0, 0.0),
        Node::new(4, 100, 0.0, 0.0),
        Node::new(5, 100, 0.0, 0.0),
    ];
    let timeout = Duration::from_millis(500);
    let coord = Arc::new(Mutex::new(setup_coordinator(nodes, timeout)));
    let mut handles = vec![];

    // Launch 10 concurrent transactions.
    for i in 0..10 {
        let coord_clone = Arc::clone(&coord);
        handles.push(thread::spawn(move || {
            // Alternate between increment and decrement.
            let op = if i % 2 == 0 { Operation::Increment } else { Operation::Decrement };
            let delta = 5;
            let node_ids = vec![1, 2, 3, 4, 5];
            let outcome;
            {
                // Lock the coordinator for execution.
                let coord_locked = coord_clone.lock().unwrap();
                outcome = coord_locked.execute_transaction(op, delta, node_ids.clone());
            }
            outcome
        }));
    }
    
    let mut commit_count = 0;
    let mut abort_count = 0;
    for handle in handles {
        let outcome = handle.join().unwrap();
        match outcome {
            TransactionOutcome::Committed => commit_count += 1,
            TransactionOutcome::Aborted => abort_count += 1,
        }
    }
    // At least some transactions should commit.
    assert!(commit_count > 0);
    // Because operations run concurrently, some might abort because of temporary inconsistencies.
    // Total transactions must sum to 10.
    assert_eq!(commit_count + abort_count, 10);
    
    // Verify final states of nodes are within expected range.
    let final_states = {
        let coord_locked = coord.lock().unwrap();
        vec![
            coord_locked.get_node_state(1),
            coord_locked.get_node_state(2),
            coord_locked.get_node_state(3),
            coord_locked.get_node_state(4),
            coord_locked.get_node_state(5),
        ]
    };
    // Since each successful transaction adds or subtracts 5 from all nodes, and some transactions might abort,
    // final state should be around 100 with increments of 5. We simply check for multiple of 5.
    for state in final_states.into_iter() {
        assert_eq!(state % 5, 0);
    }
}