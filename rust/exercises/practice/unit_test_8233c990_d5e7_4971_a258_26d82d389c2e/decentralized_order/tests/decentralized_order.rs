use decentralized_order::{Node, Transaction};

const THRESHOLD_MILLISECONDS: u64 = 500;

fn broadcast_consensus(nodes: &mut Vec<Node>, consensus_order: Vec<u64>) {
    for node in nodes.iter_mut() {
        node.accept_proposal(consensus_order.clone());
    }
}

#[test]
fn test_final_order_consistency() {
    // Simulate a network of 5 nodes.
    let mut nodes: Vec<Node> = (0..5).map(|i| Node::new(i)).collect();

    // Create transactions with various timestamps.
    let transactions = vec![
        Transaction { id: 1, timestamp: 100 },
        Transaction { id: 2, timestamp: 700 },
        Transaction { id: 3, timestamp: 400 },
        Transaction { id: 4, timestamp: 1200 },
        Transaction { id: 5, timestamp: 900 },
    ];

    // Distribute transactions among nodes arbitrarily.
    nodes[0].receive_transaction(transactions[0].clone());
    nodes[1].receive_transaction(transactions[1].clone());
    nodes[2].receive_transaction(transactions[2].clone());
    nodes[3].receive_transaction(transactions[3].clone());
    nodes[4].receive_transaction(transactions[4].clone());

    // Each node generates its proposed order.
    let proposals: Vec<Vec<u64>> = nodes.iter().map(|node| node.propose_order()).collect();

    // For simplicity, choose the proposal from node 0 as the consensus order.
    let consensus_order = proposals[0].clone();
    broadcast_consensus(&mut nodes, consensus_order.clone());

    // Verify that all nodes have the same final order.
    for node in &nodes {
        assert_eq!(node.get_final_order(), consensus_order);
    }
}

#[test]
fn test_timestamp_ordering() {
    // A network of 3 nodes.
    let mut nodes: Vec<Node> = (0..3).map(|i| Node::new(i)).collect();

    // Create transactions with significant timestamp differences.
    // Transaction with id 10 should come before 20 (difference 600ms) and 20 before 30 (difference 700ms).
    let transactions = vec![
        Transaction { id: 10, timestamp: 100 },
        Transaction { id: 20, timestamp: 700 },
        Transaction { id: 30, timestamp: 1400 },
    ];

    // All nodes receive all transactions.
    for node in nodes.iter_mut() {
        for txn in transactions.iter() {
            node.receive_transaction(txn.clone());
        }
    }

    // Each node generates its proposed order.
    let proposals: Vec<Vec<u64>> = nodes.iter().map(|node| node.propose_order()).collect();

    // Choose the proposal from node 1 as the consensus order.
    let consensus_order = proposals[1].clone();
    broadcast_consensus(&mut nodes, consensus_order.clone());

    // The expected consensus order should reflect the timestamp order.
    let expected_order = vec![10, 20, 30];
    assert_eq!(consensus_order, expected_order);

    for node in &nodes {
        assert_eq!(node.get_final_order(), expected_order);
    }
}

#[test]
fn test_fault_tolerance() {
    // A network of 7 nodes.
    let mut nodes: Vec<Node> = (0..7).map(|i| Node::new(i)).collect();

    // Create transactions to be processed by all nodes.
    let transactions = vec![
        Transaction { id: 100, timestamp: 500 },
        Transaction { id: 200, timestamp: 1200 },
        Transaction { id: 300, timestamp: 900 },
    ];

    // Distribute transactions to every node.
    for node in nodes.iter_mut() {
        for txn in transactions.iter() {
            node.receive_transaction(txn.clone());
        }
    }

    // Simulate normal nodes (all except the faulty one) proposing an order.
    // Assume node with id 3 is acting maliciously.
    let mut normal_proposals = Vec::new();
    for (i, node) in nodes.iter().enumerate() {
        if i != 3 {
            normal_proposals.push(node.propose_order());
        }
    }

    // For consensus, choose the proposal from the first normal node.
    let consensus_order = normal_proposals[0].clone();

    // Broadcast the consensus order to all nodes, including the faulty one.
    for node in nodes.iter_mut() {
        node.accept_proposal(consensus_order.clone());
    }

    // Verify that all nodes eventually share the same final order.
    for node in &nodes {
        assert_eq!(node.get_final_order(), consensus_order);
    }
}