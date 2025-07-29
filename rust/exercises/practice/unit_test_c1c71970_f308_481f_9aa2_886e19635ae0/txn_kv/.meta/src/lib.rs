use std::collections::HashMap;
use std::sync::{Mutex};
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Debug, PartialEq, Eq)]
pub enum TransactionError {
    Conflict,
    NotFound,
}

#[derive(Clone)]
struct Transaction {
    transaction_id: u64,
    snapshot: u64,
    local_writes: HashMap<String, String>,
}

pub struct KVStore {
    // Global store: each key maps to a vector of (commit_timestamp, value) pairs.
    global: Mutex<HashMap<String, Vec<(u64, String)>>>,
    // Active transactions: mapping from transaction id to Transaction.
    active_tx: Mutex<HashMap<u64, Transaction>>,
    // Counter for generating transaction ids and commit timestamps.
    counter: AtomicU64,
}

impl KVStore {
    pub fn new() -> KVStore {
        KVStore {
            global: Mutex::new(HashMap::new()),
            active_tx: Mutex::new(HashMap::new()),
            counter: AtomicU64::new(1),
        }
    }

    pub fn begin_transaction(&self) -> u64 {
        // Generate a new transaction id.
        let tx_id = self.counter.fetch_add(1, Ordering::SeqCst);
        // Set the snapshot to the current latest commit timestamp.
        // For simplicity, we use tx_id - 1 since counter is monotonically increasing.
        let snapshot = tx_id - 1;
        let tx = Transaction {
            transaction_id: tx_id,
            snapshot,
            local_writes: HashMap::new(),
        };
        self.active_tx.lock().unwrap().insert(tx_id, tx);
        tx_id
    }

    pub fn read(&self, tx_id: u64, key: &str) -> Option<String> {
        // Retrieve the active transaction.
        let tx_opt = {
            let active = self.active_tx.lock().unwrap();
            active.get(&tx_id).cloned()
        };
        let tx = match tx_opt {
            Some(tx) => tx,
            None => return None,
        };
        // First, check the transaction's local writes.
        if let Some(val) = tx.local_writes.get(key) {
            return Some(val.clone());
        }
        // Else, check the global store for a committed version visible to this transaction.
        let global = self.global.lock().unwrap();
        if let Some(versions) = global.get(key) {
            let mut candidate: Option<&(u64, String)> = None;
            for version in versions {
                if version.0 <= tx.snapshot {
                    if let Some(curr) = candidate {
                        if version.0 > curr.0 {
                            candidate = Some(version);
                        }
                    } else {
                        candidate = Some(version);
                    }
                }
            }
            if let Some(ver) = candidate {
                return Some(ver.1.clone());
            }
        }
        None
    }

    pub fn write(&self, tx_id: u64, key: &str, value: &str) {
        let mut active = self.active_tx.lock().unwrap();
        if let Some(tx) = active.get_mut(&tx_id) {
            tx.local_writes.insert(key.to_string(), value.to_string());
        }
    }

    pub fn commit_transaction(&self, tx_id: u64) -> Result<(), TransactionError> {
        // Remove the transaction from the active transactions.
        let tx = {
            let mut active = self.active_tx.lock().unwrap();
            match active.remove(&tx_id) {
                Some(tx) => tx,
                None => return Err(TransactionError::NotFound),
            }
        };

        let mut global = self.global.lock().unwrap();

        // Conflict detection: if any key written by the transaction has a committed version
        // with a commit timestamp greater than the transaction's snapshot, then there is a conflict.
        for (key, _) in &tx.local_writes {
            if let Some(versions) = global.get(key) {
                if let Some(last) = versions.last() {
                    if last.0 > tx.snapshot {
                        return Err(TransactionError::Conflict);
                    }
                }
            }
        }

        // No conflict detected, commit all writes.
        // Generate a new commit timestamp.
        let commit_ts = self.counter.fetch_add(1, Ordering::SeqCst);
        for (key, value) in tx.local_writes.into_iter() {
            global.entry(key).or_insert_with(Vec::new).push((commit_ts, value));
        }
        Ok(())
    }

    pub fn abort_transaction(&self, tx_id: u64) {
        let mut active = self.active_tx.lock().unwrap();
        active.remove(&tx_id);
    }

    pub fn garbage_collect(&self, min_transaction_id: u64) {
        let mut global = self.global.lock().unwrap();
        for (_key, versions) in global.iter_mut() {
            // Retain only versions with commit_timestamp greater than min_transaction_id.
            let filtered: Vec<(u64, String)> = versions
                .iter()
                .filter(|(ts, _)| *ts > min_transaction_id)
                .cloned()
                .collect();
            if filtered.is_empty() && !versions.is_empty() {
                // If all versions are older, keep the latest version.
                if let Some(last) = versions.last() {
                    *versions = vec![last.clone()];
                }
            } else {
                *versions = filtered;
            }
        }
    }
}