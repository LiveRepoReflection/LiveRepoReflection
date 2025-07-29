use std::collections::HashMap;
use std::sync::{Mutex, OnceLock};
use std::sync::atomic::{AtomicU64, Ordering};

pub type TransactionId = u64;
pub type ResourceManagerId = u64;

#[derive(PartialEq)]
enum TransactionStatus {
    Pending,
    Committed,
    RolledBack,
}

struct Transaction {
    id: TransactionId,
    // writes: resource_manager_id -> (key -> value)
    writes: HashMap<ResourceManagerId, HashMap<String, String>>,
    status: TransactionStatus,
}

impl Transaction {
    fn new(id: TransactionId) -> Self {
        Transaction {
            id,
            writes: HashMap::new(),
            status: TransactionStatus::Pending,
        }
    }
}

struct ResourceManager {
    id: ResourceManagerId,
    store: HashMap<String, String>,
    // in-flight writes: transaction_id -> (key -> value)
    in_flight: HashMap<TransactionId, HashMap<String, String>>,
    #[cfg(feature = "simulate_failure")]
    failure: bool,
}

impl ResourceManager {
    fn new(id: ResourceManagerId) -> Self {
        ResourceManager {
            id,
            store: HashMap::new(),
            in_flight: HashMap::new(),
            #[cfg(feature = "simulate_failure")]
            failure: false,
        }
    }

    // Simulated prepare: if failure flag is set, preparation fails.
    fn prepare(&mut self, tx_id: TransactionId, changes: &HashMap<String, String>) -> bool {
        #[cfg(feature = "simulate_failure")]
        {
            if self.failure {
                return false;
            }
        }
        // For simulation, simply store the changes in in-flight.
        self.in_flight.insert(tx_id, changes.clone());
        true
    }

    // Commit the changes stored in in-flight into the store.
    fn commit(&mut self, tx_id: TransactionId) {
        if let Some(changes) = self.in_flight.remove(&tx_id) {
            for (k, v) in changes.into_iter() {
                self.store.insert(k, v);
            }
        }
    }

    // Rollback: discard the in-flight writes.
    fn rollback(&mut self, tx_id: TransactionId) {
        self.in_flight.remove(&tx_id);
    }

    // Read a key from the committed store.
    fn get_value(&self, key: &str) -> Option<String> {
        self.store.get(key).cloned()
    }
}

static TRANSACTION_COUNTER: AtomicU64 = AtomicU64::new(1);
static TRANSACTIONS: OnceLock<Mutex<HashMap<TransactionId, Transaction>>> = OnceLock::new();
static RESOURCE_MANAGERS: OnceLock<Mutex<HashMap<ResourceManagerId, ResourceManager>>> = OnceLock::new();

fn init_transactions() -> &'static Mutex<HashMap<TransactionId, Transaction>> {
    TRANSACTIONS.get_or_init(|| Mutex::new(HashMap::new()))
}

fn init_resource_managers() -> &'static Mutex<HashMap<ResourceManagerId, ResourceManager>> {
    RESOURCE_MANAGERS.get_or_init(|| Mutex::new(HashMap::new()))
}

/// Begin a new transaction and return a unique TransactionId.
pub fn begin_transaction() -> TransactionId {
    let tx_id = TRANSACTION_COUNTER.fetch_add(1, Ordering::SeqCst);
    let tx = Transaction::new(tx_id);
    let transactions = init_transactions();
    let mut tx_lock = transactions.lock().unwrap();
    tx_lock.insert(tx_id, tx);
    tx_id
}

/// Write a key-value pair for a specific resource manager within the given transaction.
pub fn write(transaction_id: TransactionId, resource_manager_id: ResourceManagerId, key: String, value: String) {
    let transactions = init_transactions();
    let mut tx_lock = transactions.lock().unwrap();
    if let Some(tx) = tx_lock.get_mut(&transaction_id) {
        if tx.status != TransactionStatus::Pending {
            return;
        }
        let entry = tx.writes.entry(resource_manager_id).or_insert_with(HashMap::new);
        entry.insert(key, value);
    }
}

/// Read a key from a specific resource manager within the context of a transaction.
pub fn read(transaction_id: TransactionId, resource_manager_id: ResourceManagerId, key: String) -> Option<String> {
    // First check if the transaction has a pending write for that key.
    let transactions = init_transactions();
    let tx_lock = transactions.lock().unwrap();
    if let Some(tx) = tx_lock.get(&transaction_id) {
        if let Some(writes) = tx.writes.get(&resource_manager_id) {
            if let Some(val) = writes.get(&key) {
                return Some(val.clone());
            }
        }
    }
    // Otherwise, read from the resource manager's committed store.
    let rms = init_resource_managers();
    let rms_lock = rms.lock().unwrap();
    let rm = rms_lock.get(&resource_manager_id);
    if let Some(rm) = rm {
        return rm.get_value(&key);
    }
    None
}

/// Attempt to commit the transaction using a two-phase commit protocol.
/// Returns true if commit succeeds on all resource managers, false otherwise.
pub fn commit_transaction(transaction_id: TransactionId) -> bool {
    // Get the transaction.
    let transactions = init_transactions();
    let mut tx_lock = transactions.lock().unwrap();
    let tx = match tx_lock.get_mut(&transaction_id) {
        Some(t) if t.status == TransactionStatus::Pending => t,
        _ => {
            // Either doesn't exist or already committed/rolled back.
            return false;
        }
    };

    // Prepare phase: For each resource manager involved, call prepare.
    let mut prepared_rms: Vec<ResourceManagerId> = Vec::new();
    {
        let mut rms = init_resource_managers().lock().unwrap();
        for (&rm_id, changes) in tx.writes.iter() {
            // Get or create the resource manager.
            let rm = rms.entry(rm_id).or_insert_with(|| ResourceManager::new(rm_id));
            let success = rm.prepare(transaction_id, changes);
            if !success {
                // Prepare failed.
                // Rollback already prepared resource managers.
                for &prepared_rm_id in &prepared_rms {
                    if let Some(prepared_rm) = rms.get_mut(&prepared_rm_id) {
                        prepared_rm.rollback(transaction_id);
                    }
                }
                tx.status = TransactionStatus::RolledBack;
                return false;
            }
            prepared_rms.push(rm_id);
        }
    }

    // Commit phase: Commit changes on all resource managers.
    {
        let mut rms = init_resource_managers().lock().unwrap();
        for &rm_id in &prepared_rms {
            if let Some(rm) = rms.get_mut(&rm_id) {
                rm.commit(transaction_id);
            }
        }
    }
    tx.status = TransactionStatus::Committed;
    true
}

/// Rollback the transaction in all involved resource managers.
pub fn rollback_transaction(transaction_id: TransactionId) {
    let transactions = init_transactions();
    let mut tx_lock = transactions.lock().unwrap();
    if let Some(tx) = tx_lock.get_mut(&transaction_id) {
        if tx.status != TransactionStatus::Pending {
            // Already committed or rolled back.
            return;
        }
        let mut rms = init_resource_managers().lock().unwrap();
        for (&rm_id, _changes) in tx.writes.iter() {
            let rm = rms.entry(rm_id).or_insert_with(|| ResourceManager::new(rm_id));
            rm.rollback(transaction_id);
        }
        tx.status = TransactionStatus::RolledBack;
    }
}

#[cfg(feature = "simulate_failure")]
/// Set the failure flag for a given resource manager.
pub fn set_resource_failure(resource_manager_id: ResourceManagerId, failure: bool) {
    let mut rms = init_resource_managers().lock().unwrap();
    let rm = rms.entry(resource_manager_id).or_insert_with(|| ResourceManager::new(resource_manager_id));
    rm.failure = failure;
}

#[cfg(feature = "recovery")]
/// Recover orphaned transactions by rolling back those still pending.
pub fn recover_orphaned_transactions() {
    let transactions = init_transactions();
    let mut tx_lock = transactions.lock().unwrap();
    let mut rms = init_resource_managers().lock().unwrap();
    let orphaned_tx_ids: Vec<TransactionId> = tx_lock.iter()
        .filter(|(_id, tx)| tx.status == TransactionStatus::Pending)
        .map(|(&id, _)| id)
        .collect();
    for tx_id in orphaned_tx_ids {
        if let Some(tx) = tx_lock.get_mut(&tx_id) {
            // Rollback on each resource manager.
            for (&rm_id, _changes) in tx.writes.iter() {
                let rm = rms.entry(rm_id).or_insert_with(|| ResourceManager::new(rm_id));
                rm.rollback(tx_id);
            }
            tx.status = TransactionStatus::RolledBack;
        }
    }
}