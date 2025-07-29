use std::collections::HashMap;
use std::sync::{Arc, Mutex, RwLock, OnceLock, Barrier};
use std::sync::atomic::{AtomicU64, Ordering};

// Global key-value store: key -> (value, version)
static STORE: OnceLock<Arc<RwLock<HashMap<String, (String, u64)>>>> = OnceLock::new();
// Global transactions: tx_id -> Transaction
static TRANSACTIONS: OnceLock<Arc<Mutex<HashMap<u64, Transaction>>>> = OnceLock::new();
// Global atomic transaction id counter
static TX_COUNTER: AtomicU64 = AtomicU64::new(1);

fn init_globals() {
    STORE.get_or_init(|| Arc::new(RwLock::new(HashMap::new())));
    TRANSACTIONS.get_or_init(|| Arc::new(Mutex::new(HashMap::new())));
}

pub type TransactionId = u64;

#[derive(Clone)]
struct Transaction {
    id: TransactionId,
    writes: HashMap<String, String>,
    snapshot: HashMap<String, u64>,
}

fn conflict_resolution(existing: &str, new_value: &str) -> String {
    // Deterministically merge the two values: existing value comes first.
    format!("{}|{}", existing, new_value)
}

pub fn begin_transaction() -> TransactionId {
    init_globals();
    let store = STORE.get().unwrap();
    let store_read = store.read().unwrap();
    let mut snapshot = HashMap::new();
    for (key, &(_, version)) in store_read.iter() {
        snapshot.insert(key.clone(), version);
    }
    drop(store_read);
    let id = TX_COUNTER.fetch_add(1, Ordering::SeqCst);
    let tx = Transaction {
        id,
        writes: HashMap::new(),
        snapshot,
    };
    let transactions = TRANSACTIONS.get().unwrap();
    let mut tx_map = transactions.lock().unwrap();
    tx_map.insert(id, tx);
    id
}

pub fn read(transaction_id: TransactionId, key: &str) -> Option<String> {
    init_globals();
    let transactions = TRANSACTIONS.get().unwrap();
    let tx_map = transactions.lock().unwrap();
    if let Some(tx) = tx_map.get(&transaction_id) {
        if let Some(local_value) = tx.writes.get(key) {
            return Some(local_value.clone());
        }
    }
    let store = STORE.get().unwrap();
    let store_read = store.read().unwrap();
    if let Some((value, _version)) = store_read.get(key) {
        Some(value.clone())
    } else {
        None
    }
}

pub fn write(transaction_id: TransactionId, key: &str, value: &str) {
    init_globals();
    let transactions = TRANSACTIONS.get().unwrap();
    let mut tx_map = transactions.lock().unwrap();
    if let Some(tx) = tx_map.get_mut(&transaction_id) {
        tx.writes.insert(key.to_string(), value.to_string());
    }
}

pub fn commit_transaction(transaction_id: TransactionId) -> Result<(), String> {
    init_globals();
    // Remove the transaction from active transactions and commit its writes.
    let tx = {
        let transactions = TRANSACTIONS.get().unwrap();
        let mut tx_map = transactions.lock().unwrap();
        match tx_map.remove(&transaction_id) {
            Some(tx) => tx,
            None => return Err("Transaction not found".to_string()),
        }
    };
    let store = STORE.get().unwrap();
    let mut store_write = store.write().unwrap();
    for (key, new_value) in tx.writes.iter() {
        let snapshot_version = tx.snapshot.get(key).cloned().unwrap_or(0);
        let (store_value, store_version) = store_write.get(key).cloned().unwrap_or((String::new(), 0));
        if store_version == snapshot_version {
            let updated_version = store_version.wrapping_add(1);
            store_write.insert(key.clone(), (new_value.clone(), updated_version));
        } else {
            // Conflict detected; apply conflict resolution.
            let merged = conflict_resolution(&store_value, new_value);
            let updated_version = store_version.wrapping_add(1);
            store_write.insert(key.clone(), (merged, updated_version));
        }
    }
    Ok(())
}

pub fn abort_transaction(transaction_id: TransactionId) -> Result<(), String> {
    init_globals();
    let transactions = TRANSACTIONS.get().unwrap();
    let mut tx_map = transactions.lock().unwrap();
    if tx_map.remove(&transaction_id).is_some() {
        Ok(())
    } else {
        Err("Transaction not found".to_string())
    }
}