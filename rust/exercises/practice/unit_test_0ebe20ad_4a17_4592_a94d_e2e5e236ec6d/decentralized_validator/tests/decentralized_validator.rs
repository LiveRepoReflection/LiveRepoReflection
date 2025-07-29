use decentralized_validator::{Transaction, Node, validate_transaction};

fn create_transaction(
    transaction_id: &str,
    sender: &str,
    recipient: &str,
    amount: u64,
    timestamp: u64,
    signature: &str,
) -> Transaction {
    Transaction {
        transaction_id: transaction_id.to_string(),
        sender_account: sender.to_string(),
        recipient_account: recipient.to_string(),
        amount,
        timestamp,
        signature: signature.to_string(),
    }
}

#[test]
fn test_valid_transaction() {
    // Scenario: A valid transaction where the sender has sufficient funds,
    // the signature is correct, and there is no double spending.
    let deposit = create_transaction("tx_deposit", "SYSTEM", "Alice", 100, 1000, "valid_sig");
    let node_log = vec![deposit];
    let node = Node {
        node_id: "node_1".to_string(),
        transaction_log: node_log,
        known_nodes: vec!["node_2".to_string(), "node_3".to_string()],
    };

    let spending = create_transaction("tx_spend", "Alice", "Bob", 50, 2000, "valid_sig");
    let result = validate_transaction(&node, &spending);
    assert!(result, "Transaction should be valid when funds are sufficient and signature is correct.");
}

#[test]
fn test_invalid_signature() {
    // Scenario: The transaction has an invalid signature.
    let deposit = create_transaction("tx_deposit", "SYSTEM", "Alice", 100, 1000, "valid_sig");
    let node_log = vec![deposit];
    let node = Node {
        node_id: "node_1".to_string(),
        transaction_log: node_log,
        known_nodes: vec!["node_2".to_string()],
    };

    // The spending transaction uses an invalid signature.
    let spending = create_transaction("tx_spend", "Alice", "Bob", 50, 2000, "invalid_sig");
    let result = validate_transaction(&node, &spending);
    assert!(!result, "Transaction should be invalid due to a failed signature verification.");
}

#[test]
fn test_insufficient_funds() {
    // Scenario: The sender does not have enough funds.
    let deposit = create_transaction("tx_deposit", "SYSTEM", "Alice", 30, 1000, "valid_sig");
    let node_log = vec![deposit];
    let node = Node {
        node_id: "node_1".to_string(),
        transaction_log: node_log,
        known_nodes: vec!["node_2".to_string()],
    };

    // Attempt to spend more than the available balance.
    let spending = create_transaction("tx_spend", "Alice", "Bob", 50, 2000, "valid_sig");
    let result = validate_transaction(&node, &spending);
    assert!(!result, "Transaction should be invalid due to insufficient funds.");
}

#[test]
fn test_double_spending() {
    // Scenario: A double spending attempt where previous spending depletes the funds.
    // Alice has an initial deposit of 100 and already spent 80.
    let deposit = create_transaction("tx_deposit", "SYSTEM", "Alice", 100, 1000, "valid_sig");
    let first_spend = create_transaction("tx_spend1", "Alice", "Bob", 80, 1500, "valid_sig");
    let node_log = vec![deposit, first_spend];
    let node = Node {
        node_id: "node_1".to_string(),
        transaction_log: node_log,
        known_nodes: vec!["node_2".to_string()],
    };

    // Attempt to spend an additional 30, which would exceed the deposited amount.
    let second_spend = create_transaction("tx_spend2", "Alice", "Charlie", 30, 2000, "valid_sig");
    let result = validate_transaction(&node, &second_spend);
    assert!(!result, "Transaction should be invalid due to a double spending attempt.");
}

#[test]
fn test_network_fallback() {
    // Scenario: The local log is incomplete, but a network query (simulated via known_nodes)
    // should provide the necessary deposit information. Assume that validate_transaction internally
    // attempts to augment the local log from known nodes.
    // Here the local log is empty, but we assume the network can supply the missing deposit.
    let node = Node {
        node_id: "node_1".to_string(),
        transaction_log: Vec::new(),
        known_nodes: vec!["node_2".to_string(), "node_3".to_string()],
    };

    let spending = create_transaction("tx_spend", "Alice", "Bob", 50, 2000, "valid_sig");
    let result = validate_transaction(&node, &spending);
    // For test purposes, assume that network fallback makes the transaction valid if the deposit exists remotely.
    assert!(result, "Transaction should be valid via network fallback even if the local log is incomplete.");
}

#[test]
fn test_invalid_public_key() {
    // Scenario: The sender's public key cannot be retrieved (e.g., non-existent or error).
    // In such a case, the transaction should be invalid.
    let deposit = create_transaction("tx_deposit", "SYSTEM", "Dave", 50, 1000, "valid_sig");
    let node_log = vec![deposit];
    let node = Node {
        node_id: "node_1".to_string(),
        transaction_log: node_log,
        known_nodes: Vec::new(),
    };

    // Create a transaction from a sender whose public key is assumed to be unretrievable.
    let spending = create_transaction("tx_spend", "Eve", "Frank", 20, 2000, "valid_sig");
    let result = validate_transaction(&node, &spending);
    assert!(!result, "Transaction should be invalid if the sender's public key cannot be retrieved.");
}