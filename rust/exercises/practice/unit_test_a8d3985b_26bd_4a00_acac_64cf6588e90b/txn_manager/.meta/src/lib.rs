use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(PartialEq, Debug, Clone)]
pub enum TransactionState {
    Active,
    Prepared,
    Committed,
    Aborted,
    NotFound,
}

#[derive(Debug)]
pub enum PreparedResult {
    Ready,
    ReadOnly,
    Aborted(String),
}

pub trait Participant: Send + Sync {
    fn prepare(&self, transaction_id: u64) -> PreparedResult;
    fn commit(&self, transaction_id: u64);
    fn rollback(&self, transaction_id: u64);
}

struct Transaction {
    state: TransactionState,
    participants: Vec<Arc<dyn Participant>>,
}

pub struct TransactionCoordinator {
    transactions: Mutex<HashMap<u64, Transaction>>,
    counter: AtomicU64,
}

impl TransactionCoordinator {
    pub fn new() -> TransactionCoordinator {
        TransactionCoordinator {
            transactions: Mutex::new(HashMap::new()),
            counter: AtomicU64::new(1),
        }
    }

    pub fn begin_transaction(&self) -> u64 {
        let txn_id = self.counter.fetch_add(1, Ordering::SeqCst);
        let txn = Transaction {
            state: TransactionState::Active,
            participants: Vec::new(),
        };
        let mut transactions = self.transactions.lock().unwrap();
        transactions.insert(txn_id, txn);
        txn_id
    }

    pub fn register_participant(&self, transaction_id: u64, participant: Arc<dyn Participant>) {
        let mut transactions = self.transactions.lock().unwrap();
        if let Some(txn) = transactions.get_mut(&transaction_id) {
            txn.participants.push(participant);
        }
    }

    pub fn prepare_transaction(&self, transaction_id: u64) -> TransactionState {
        let mut transactions = self.transactions.lock().unwrap();
        if let Some(txn) = transactions.get_mut(&transaction_id) {
            if txn.state != TransactionState::Active {
                return txn.state.clone();
            }
            let mut abort = false;
            for participant in &txn.participants {
                match participant.prepare(transaction_id) {
                    PreparedResult::Aborted(_reason) => {
                        abort = true;
                        break;
                    },
                    _ => {}
                }
            }
            if abort {
                for participant in &txn.participants {
                    participant.rollback(transaction_id);
                }
                txn.state = TransactionState::Aborted;
            } else {
                txn.state = TransactionState::Prepared;
            }
            txn.state.clone()
        } else {
            TransactionState::NotFound
        }
    }

    pub fn commit_transaction(&self, transaction_id: u64) -> TransactionState {
        let mut transactions = self.transactions.lock().unwrap();
        if let Some(txn) = transactions.get_mut(&transaction_id) {
            if txn.state != TransactionState::Prepared {
                return txn.state.clone();
            }
            for participant in &txn.participants {
                participant.commit(transaction_id);
            }
            txn.state = TransactionState::Committed;
            txn.state.clone()
        } else {
            TransactionState::NotFound
        }
    }

    pub fn rollback_transaction(&self, transaction_id: u64) -> TransactionState {
        let mut transactions = self.transactions.lock().unwrap();
        if let Some(txn) = transactions.get_mut(&transaction_id) {
            if txn.state == TransactionState::Committed {
                return txn.state.clone();
            }
            for participant in &txn.participants {
                participant.rollback(transaction_id);
            }
            txn.state = TransactionState::Aborted;
            txn.state.clone()
        } else {
            TransactionState::NotFound
        }
    }

    pub fn get_transaction_state(&self, transaction_id: u64) -> TransactionState {
        let transactions = self.transactions.lock().unwrap();
        if let Some(txn) = transactions.get(&transaction_id) {
            txn.state.clone()
        } else {
            TransactionState::NotFound
        }
    }
}