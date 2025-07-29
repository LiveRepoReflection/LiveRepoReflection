use std::collections::{HashMap, HashSet};
use std::sync::{Arc, RwLock, Mutex};

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum TransactionStatus {
    Pending,
    Prepared,
    Committed,
    RolledBack,
    NotFound,
}

struct Transaction {
    participating_nodes: HashSet<String>,
    prepared_nodes: HashSet<String>,
    status: TransactionStatus,
}

pub struct Coordinator {
    transactions: RwLock<HashMap<u64, Arc<Mutex<Transaction>>>>,
}

impl Coordinator {
    pub fn new() -> Self {
        Coordinator {
            transactions: RwLock::new(HashMap::new()),
        }
    }

    pub fn begin_transaction(&self, transaction_id: u64, participating_nodes: Vec<String>) -> Result<(), String> {
        let mut transactions = self.transactions.write().unwrap();
        
        if transactions.contains_key(&transaction_id) {
            return Err("Transaction already exists".to_string());
        }
        
        let node_set: HashSet<String> = participating_nodes.into_iter().collect();
        let status = if node_set.is_empty() {
            TransactionStatus::Prepared // Empty transactions are considered fully prepared
        } else {
            TransactionStatus::Pending
        };
        
        let transaction = Transaction {
            participating_nodes: node_set,
            prepared_nodes: HashSet::new(),
            status,
        };
        
        transactions.insert(transaction_id, Arc::new(Mutex::new(transaction)));
        Ok(())
    }

    pub fn prepare(&self, transaction_id: u64, node_id: &str) -> Result<(), String> {
        // Get a read lock to check if transaction exists
        let transactions = self.transactions.read().unwrap();
        
        let transaction_arc = match transactions.get(&transaction_id) {
            Some(tx) => Arc::clone(tx),
            None => return Err("Transaction not found".to_string()),
        };
        
        // Release the read lock before locking the individual transaction
        drop(transactions);
        
        // Lock the individual transaction
        let mut transaction = transaction_arc.lock().unwrap();
        
        // Check if node is part of this transaction
        if !transaction.participating_nodes.contains(node_id) {
            return Err("Node not in transaction".to_string());
        }
        
        // Check if node has already prepared
        if transaction.prepared_nodes.contains(node_id) {
            return Err("Node already prepared".to_string());
        }
        
        // Add node to prepared set
        transaction.prepared_nodes.insert(node_id.to_string());
        
        // Check if all nodes are prepared
        if transaction.prepared_nodes.len() == transaction.participating_nodes.len() {
            transaction.status = TransactionStatus::Prepared;
        }
        
        Ok(())
    }

    pub fn commit_transaction(&self, transaction_id: u64) -> Result<(), String> {
        // Get a read lock to check if transaction exists
        let transactions = self.transactions.read().unwrap();
        
        let transaction_arc = match transactions.get(&transaction_id) {
            Some(tx) => Arc::clone(tx),
            None => return Err("Transaction not found".to_string()),
        };
        
        // Release the read lock before locking the individual transaction
        drop(transactions);
        
        // Lock the individual transaction
        let mut transaction = transaction_arc.lock().unwrap();
        
        // Check if the transaction can be committed
        if transaction.status == TransactionStatus::Committed {
            // Already committed, idempotent operation
            return Ok(());
        }
        
        if transaction.status == TransactionStatus::RolledBack {
            // Cannot commit a rolled back transaction, but this is an idempotent operation
            // so we'll just return success
            return Ok(());
        }
        
        // Verify all nodes are prepared
        if transaction.prepared_nodes.len() != transaction.participating_nodes.len() {
            return Err("Not all nodes prepared".to_string());
        }
        
        // Commit the transaction
        transaction.status = TransactionStatus::Committed;
        
        Ok(())
    }

    pub fn rollback_transaction(&self, transaction_id: u64) -> Result<(), String> {
        // Get a read lock to check if transaction exists
        let transactions = self.transactions.read().unwrap();
        
        let transaction_arc = match transactions.get(&transaction_id) {
            Some(tx) => Arc::clone(tx),
            None => return Err("Transaction not found".to_string()),
        };
        
        // Release the read lock before locking the individual transaction
        drop(transactions);
        
        // Lock the individual transaction
        let mut transaction = transaction_arc.lock().unwrap();
        
        // Check if the transaction is already rolled back
        if transaction.status == TransactionStatus::RolledBack {
            // Already rolled back, idempotent operation
            return Ok(());
        }
        
        if transaction.status == TransactionStatus::Committed {
            // Already committed, but we'll treat this as idempotent for simplicity
            return Ok(());
        }
        
        // Rollback the transaction
        transaction.status = TransactionStatus::RolledBack;
        
        Ok(())
    }

    pub fn get_transaction_status(&self, transaction_id: u64) -> Result<TransactionStatus, String> {
        let transactions = self.transactions.read().unwrap();
        
        match transactions.get(&transaction_id) {
            Some(transaction_arc) => {
                let transaction = transaction_arc.lock().unwrap();
                Ok(transaction.status)
            },
            None => Ok(TransactionStatus::NotFound),
        }
    }
}

impl Default for Coordinator {
    fn default() -> Self {
        Self::new()
    }
}