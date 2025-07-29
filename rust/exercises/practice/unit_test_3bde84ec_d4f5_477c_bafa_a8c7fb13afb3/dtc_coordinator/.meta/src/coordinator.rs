use std::collections::HashMap;
use std::sync::{RwLock};
use std::sync::atomic::{AtomicUsize, Ordering};

#[derive(Debug, PartialEq)]
enum TransactionState {
    Active,
    Committed,
    RolledBack,
}

impl TransactionState {
    fn as_str(&self) -> &'static str {
        match self {
            TransactionState::Active => "Active",
            TransactionState::Committed => "Committed",
            TransactionState::RolledBack => "RolledBack",
        }
    }
}

struct Transaction {
    state: TransactionState,
    // Mapping from node id to its prepare status:
    // None indicates that prepare was not called yet.
    // Some(true) indicates prepared (ready to commit).
    // Some(false) indicates that node is not ready and wants to rollback.
    nodes: HashMap<String, Option<bool>>,
}

impl Transaction {
    fn new() -> Self {
        Transaction {
            state: TransactionState::Active,
            nodes: HashMap::new(),
        }
    }
}

pub struct Coordinator {
    transactions: RwLock<HashMap<String, Transaction>>,
    counter: AtomicUsize,
}

impl Coordinator {
    pub fn new() -> Self {
        Coordinator {
            transactions: RwLock::new(HashMap::new()),
            counter: AtomicUsize::new(1),
        }
    }

    // Initiates a new transaction and returns a unique transaction id.
    pub fn begin_transaction(&self) -> String {
        let tx_id = self.counter.fetch_add(1, Ordering::SeqCst);
        let tx_id_str = tx_id.to_string();
        let transaction = Transaction::new();
        let mut transactions = self.transactions.write().unwrap();
        transactions.insert(tx_id_str.clone(), transaction);
        tx_id_str
    }

    // Enlists a node in the transaction.
    // Returns Ok(()) if successful, or Err(String) with a description if the node is already enlisted
    // or the transaction does not exist or is not active.
    pub fn enlist_resource(&self, tx_id: &String, node_id: String) -> Result<(), String> {
        let mut transactions = self.transactions.write().unwrap();
        match transactions.get_mut(tx_id) {
            Some(tx) => {
                if tx.nodes.contains_key(&node_id) {
                    return Err(format!("Node {} already enlisted in transaction {}", node_id, tx_id));
                }
                if tx.state != TransactionState::Active {
                    return Err(format!("Cannot enlist node to transaction {} in state {}", tx_id, tx.state.as_str()));
                }
                tx.nodes.insert(node_id, None);
                Ok(())
            },
            None => Err(format!("Transaction {} does not exist", tx_id)),
        }
    }

    // Simulates the prepare phase for a node.
    // Returns Ok(true) if prepared, Ok(false) if node is not ready, or Err(String) if the node or transaction
    // does not exist or if the transaction is not active.
    // For simulation purposes, we assume that if the node_id contains "fail", it fails to prepare.
    pub fn prepare(&self, tx_id: &String, node_id: String) -> Result<bool, String> {
        let mut transactions = self.transactions.write().unwrap();
        match transactions.get_mut(tx_id) {
            Some(tx) => {
                if !tx.nodes.contains_key(&node_id) {
                    return Err(format!("Node {} not enlisted in transaction {}", node_id, tx_id));
                }
                if tx.state != TransactionState::Active {
                    return Err(format!("Transaction {} is not active", tx_id));
                }
                // Simulate preparation result: if node_id contains "fail", then it fails to prepare.
                let readiness = if node_id.contains("fail") {
                    false
                } else {
                    true
                };
                tx.nodes.insert(node_id, Some(readiness));
                Ok(readiness)
            },
            None => Err(format!("Transaction {} does not exist", tx_id)),
        }
    }

    // Commits the transaction if all enlisted nodes have prepared successfully (i.e. Some(true)).
    // If any node failed to prepare or did not prepare at all, returns Err(String).
    // The operation is idempotent if the transaction is already committed.
    pub fn commit(&self, tx_id: &String) -> Result<(), String> {
        let mut transactions = self.transactions.write().unwrap();
        let tx = transactions.get_mut(tx_id).ok_or_else(|| format!("Transaction {} does not exist", tx_id))?;
        if tx.state == TransactionState::Committed {
            return Ok(());
        }
        if tx.state == TransactionState::RolledBack {
            return Err(format!("Cannot commit transaction {} as it is already rolled back", tx_id));
        }
        for (node, prep) in tx.nodes.iter() {
            match prep {
                Some(true) => {},
                Some(false) => return Err(format!("Node {} failed to prepare", node)),
                None => return Err(format!("Node {} did not prepare", node)),
            }
        }
        tx.state = TransactionState::Committed;
        Ok(())
    }

    // Rolls back the transaction.
    // This operation is idempotent.
    pub fn rollback(&self, tx_id: &String) -> Result<(), String> {
        let mut transactions = self.transactions.write().unwrap();
        let tx = transactions.get_mut(tx_id).ok_or_else(|| format!("Transaction {} does not exist", tx_id))?;
        if tx.state == TransactionState::RolledBack {
            return Ok(());
        }
        tx.state = TransactionState::RolledBack;
        Ok(())
    }

    // Returns the current state of the transaction as an Option<String>.
    // If the transaction does not exist, returns None.
    pub fn get_transaction_state(&self, tx_id: &String) -> Option<String> {
        let transactions = self.transactions.read().unwrap();
        transactions.get(tx_id).map(|tx| tx.state.as_str().to_string())
    }
}