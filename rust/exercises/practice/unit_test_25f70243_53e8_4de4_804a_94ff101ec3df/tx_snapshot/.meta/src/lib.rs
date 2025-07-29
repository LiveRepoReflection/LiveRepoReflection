use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex, atomic::{AtomicU64, Ordering}};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Clone)]
pub struct Database {
    data: Arc<Mutex<HashMap<String, String>>>,
    transaction_states: Arc<Mutex<HashMap<u64, TransactionState>>>,
    active_transactions: Arc<Mutex<HashSet<u64>>>,
    transaction_counter: Arc<AtomicU64>,
}

#[derive(Clone)]
struct TransactionState {
    snapshot: HashMap<String, String>,
    writes: HashMap<String, String>,
    start_time: u128,
}

impl Database {
    pub fn new() -> Self {
        Database {
            data: Arc::new(Mutex::new(HashMap::new())),
            transaction_states: Arc::new(Mutex::new(HashMap::new())),
            active_transactions: Arc::new(Mutex::new(HashSet::new())),
            transaction_counter: Arc::new(AtomicU64::new(1)),
        }
    }

    pub fn begin(&self) -> u64 {
        let tx_id = self.transaction_counter.fetch_add(1, Ordering::SeqCst);
        let current_time = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();

        let snapshot = self.data.lock().unwrap().clone();
        let transaction_state = TransactionState {
            snapshot,
            writes: HashMap::new(),
            start_time: current_time,
        };

        self.transaction_states
            .lock()
            .unwrap()
            .insert(tx_id, transaction_state);
        self.active_transactions.lock().unwrap().insert(tx_id);

        tx_id
    }

    pub fn read(&self, transaction_id: u64, key: String) -> Option<String> {
        let states = self.transaction_states.lock().unwrap();
        let state = states.get(&transaction_id)?;

        // First check if we have written this key in the current transaction
        if let Some(value) = state.writes.get(&key) {
            return Some(value.clone());
        }

        // Otherwise return from the snapshot
        state.snapshot.get(&key).cloned()
    }

    pub fn write(&self, transaction_id: u64, key: String, value: String) {
        if let Some(state) = self.transaction_states.lock().unwrap().get_mut(&transaction_id) {
            state.writes.insert(key, value);
        }
    }

    pub fn commit(&self, transaction_id: u64) -> Result<(), String> {
        let mut states = self.transaction_states.lock().unwrap();
        let state = match states.get(&transaction_id) {
            Some(s) => s,
            None => return Err("Invalid transaction ID".to_string()),
        };

        // Check for write conflicts
        let mut data = self.data.lock().unwrap();
        for (key, _) in &state.writes {
            if let Some(current_value) = data.get(key) {
                if current_value != state.snapshot.get(key).unwrap_or(&String::new()) {
                    return Err("Write conflict detected".to_string());
                }
            }
        }

        // Apply changes
        for (key, value) in &state.writes {
            data.insert(key.clone(), value.clone());
        }

        // Cleanup
        states.remove(&transaction_id);
        self.active_transactions.lock().unwrap().remove(&transaction_id);

        Ok(())
    }

    pub fn rollback(&self, transaction_id: u64) {
        self.transaction_states.lock().unwrap().remove(&transaction_id);
        self.active_transactions.lock().unwrap().remove(&transaction_id);
    }
}

impl Default for Database {
    fn default() -> Self {
        Self::new()
    }
}