use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex, RwLock};
use std::sync::atomic::{AtomicU64, Ordering};

/// Represents the possible states of a transaction
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TransactionState {
    Active,
    Prepared,
    Committed,
    Aborted,
}

/// Structure to store information about a single transaction
struct Transaction {
    state: TransactionState,
    resource_managers: HashSet<String>,
}

impl Transaction {
    fn new() -> Self {
        Self {
            state: TransactionState::Active,
            resource_managers: HashSet::new(),
        }
    }
}

/// The main transaction coordinator structure
pub struct TransactionCoordinator {
    // Next transaction ID to be assigned
    next_tx_id: AtomicU64,
    
    // Transactions storage with read-write lock for better concurrency
    transactions: RwLock<HashMap<u64, Arc<Mutex<Transaction>>>>,
}

impl TransactionCoordinator {
    /// Creates a new transaction coordinator
    pub fn new() -> Self {
        Self {
            next_tx_id: AtomicU64::new(1),
            transactions: RwLock::new(HashMap::new()),
        }
    }

    /// Begins a new transaction and returns a unique transaction ID
    pub fn begin_transaction(&self) -> u64 {
        // Generate a unique transaction ID
        let tx_id = self.next_tx_id.fetch_add(1, Ordering::SeqCst);
        
        // Create a new transaction
        let transaction = Arc::new(Mutex::new(Transaction::new()));
        
        // Store the transaction
        self.transactions.write().unwrap().insert(tx_id, transaction);
        
        tx_id
    }

    /// Enlists a resource manager in the transaction
    pub fn enlist_resource(&self, tx_id: u64, resource_manager: &str) -> Result<(), String> {
        // Get the transaction
        let transaction = self.get_transaction(tx_id)?;
        let mut transaction = transaction.lock().unwrap();
        
        // Validate transaction state
        if transaction.state != TransactionState::Active {
            return Err(format!("Cannot enlist resource in transaction with state {:?}", transaction.state));
        }
        
        // Check if resource manager is already enlisted
        if transaction.resource_managers.contains(resource_manager) {
            return Err(format!("Resource manager '{}' is already enlisted in transaction {}", resource_manager, tx_id));
        }
        
        // Enlist the resource manager
        transaction.resource_managers.insert(resource_manager.to_string());
        
        Ok(())
    }

    /// Prepares the transaction for commit (first phase of 2PC)
    pub fn prepare_transaction(&self, tx_id: u64) -> Result<(), String> {
        // Get the transaction
        let transaction = self.get_transaction(tx_id)?;
        let mut transaction = transaction.lock().unwrap();
        
        // Validate transaction state
        if transaction.state != TransactionState::Active {
            return Err(format!("Cannot prepare transaction with state {:?}", transaction.state));
        }
        
        // Simulate prepare phase with all resource managers
        // In a real system, we would actually contact each RM here
        
        // Update transaction state
        transaction.state = TransactionState::Prepared;
        
        Ok(())
    }

    /// Commits the transaction (second phase of 2PC)
    pub fn commit_transaction(&self, tx_id: u64) -> Result<(), String> {
        // Get the transaction
        let transaction = self.get_transaction(tx_id)?;
        let mut transaction = transaction.lock().unwrap();
        
        // Validate transaction state
        if transaction.state != TransactionState::Prepared {
            return Err(format!("Cannot commit transaction with state {:?}", transaction.state));
        }
        
        // Simulate commit phase with all resource managers
        // In a real system, we would actually contact each RM here
        
        // Update transaction state
        transaction.state = TransactionState::Committed;
        
        Ok(())
    }

    /// Aborts the transaction
    pub fn abort_transaction(&self, tx_id: u64) -> Result<(), String> {
        // Get the transaction
        let transaction = self.get_transaction(tx_id)?;
        let mut transaction = transaction.lock().unwrap();
        
        // Validate transaction state - can't abort if already committed
        if transaction.state == TransactionState::Committed {
            return Err(format!("Cannot abort a committed transaction {}", tx_id));
        }
        
        // Simulate abort with all resource managers
        // In a real system, we would actually contact each RM here
        
        // Update transaction state
        transaction.state = TransactionState::Aborted;
        
        Ok(())
    }

    /// Gets the current state of a transaction
    pub fn get_transaction_state(&self, tx_id: u64) -> Option<TransactionState> {
        // Use read lock for better concurrency
        let transactions = self.transactions.read().unwrap();
        
        // Get the transaction
        transactions.get(&tx_id).map(|tx| {
            tx.lock().unwrap().state
        })
    }

    // Helper method to get a transaction by ID
    fn get_transaction(&self, tx_id: u64) -> Result<Arc<Mutex<Transaction>>, String> {
        // Use read lock for better concurrency
        let transactions = self.transactions.read().unwrap();
        
        // Look up the transaction
        transactions.get(&tx_id)
            .cloned()
            .ok_or_else(|| format!("Transaction {} does not exist", tx_id))
    }
}

// Default implementation for TransactionCoordinator
impl Default for TransactionCoordinator {
    fn default() -> Self {
        Self::new()
    }
}