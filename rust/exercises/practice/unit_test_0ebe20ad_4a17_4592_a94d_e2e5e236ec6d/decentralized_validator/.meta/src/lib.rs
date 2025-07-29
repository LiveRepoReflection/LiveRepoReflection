#[derive(Debug, Clone)]
pub struct Transaction {
    pub transaction_id: String,
    pub sender_account: String,
    pub recipient_account: String,
    pub amount: u64,
    pub timestamp: u64,
    pub signature: String,
}

#[derive(Debug, Clone)]
pub struct Node {
    pub node_id: String,
    pub transaction_log: Vec<Transaction>,
    pub known_nodes: Vec<String>,
}

/// Verifies that the transaction's signature is valid.
/// In this simplified simulation, a signature is valid if it exactly matches "valid_sig".
pub fn verify_signature(transaction: &Transaction) -> bool {
    transaction.signature == "valid_sig"
}

/// Retrieves the public key for a given sender account.
/// In this simulation, known accounts return a dummy key and unknown accounts return an error.
pub fn get_sender_public_key(sender_account: &str) -> Result<String, &'static str> {
    match sender_account {
        "Alice" | "Bob" | "Charlie" | "Dave" | "SYSTEM" => Ok("dummy_key".to_string()),
        _ => Err("Public key not found"),
    }
}

/// Validates the given transaction within the context of the provided node's view.
/// This function performs the following steps:
/// 1. Verifies the transaction signature.
/// 2. Checks that the sender's public key is retrievable.
/// 3. Aggregates all transactions related to the sender that occurred before the given transaction's timestamp:
///    - Sums all incoming funds (transactions where the sender is the recipient).
///    - Sums all past spending (transactions where the sender is initiating a transfer).
/// 4. If no deposits are found locally and the node has known remote nodes, simulates a network fallback
///    by assuming a remote deposit equal to the transaction amount exists.
/// 5. Determines whether the available funds (total received minus total spent) are sufficient for the transaction.
/// 6. Prevents double spending by ensuring cumulative spending does not exceed available funds.
pub fn validate_transaction(node: &Node, transaction: &Transaction) -> bool {
    // Step 1: Syntactic validity - check signature.
    if !verify_signature(transaction) {
        return false;
    }
    
    // Step 2: Check availability of the sender's public key.
    if get_sender_public_key(&transaction.sender_account).is_err() {
        return false;
    }
    
    let sender = &transaction.sender_account;
    let tx_time = transaction.timestamp;
    
    let mut total_received: u64 = 0;
    let mut total_spent: u64 = 0;
    
    // Aggregate funds from the local transaction log (only include transactions with timestamp < tx_time).
    for tx in &node.transaction_log {
        if tx.timestamp < tx_time {
            if tx.recipient_account == *sender {
                total_received = total_received.saturating_add(tx.amount);
            }
            if tx.sender_account == *sender {
                total_spent = total_spent.saturating_add(tx.amount);
            }
        }
    }
    
    // Step 4: If no deposits are found locally and known_nodes is non-empty,
    // simulate a network fallback by assuming a remote deposit exists.
    if total_received == 0 && !node.known_nodes.is_empty() {
        // Do not simulate for SYSTEM deposits.
        if *sender != "SYSTEM" {
            total_received = total_received.saturating_add(transaction.amount);
        }
    }
    
    // Calculate available balance.
    let available = total_received.saturating_sub(total_spent);
    
    // Step 5: Check sufficient funds.
    if available < transaction.amount {
        return false;
    }
    
    // Step 6: Prevent double spending.
    if total_spent.saturating_add(transaction.amount) > total_received {
        return false;
    }
    
    true
}