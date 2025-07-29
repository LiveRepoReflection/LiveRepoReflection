use std::collections::HashMap;
use std::sync::{Mutex, RwLock};

pub type NodeId = usize;
pub type TransactionId = usize;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Vote {
    Commit,
    Abort,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TransactionState {
    Pending,
    Committed,
    Aborted,
}

struct Transaction {
    participants: Vec<NodeId>,
    votes: HashMap<NodeId, Vote>,
    state: TransactionState,
}

impl Transaction {
    fn new(participants: Vec<NodeId>) -> Self {
        Transaction {
            participants,
            votes: HashMap::new(),
            state: TransactionState::Pending,
        }
    }
}

pub struct Coordinator {
    num_nodes: usize,
    transactions: RwLock<HashMap<TransactionId, Mutex<Transaction>>>,
}

impl Coordinator {
    pub fn new(num_nodes: usize) -> Self {
        Coordinator {
            num_nodes,
            transactions: RwLock::new(HashMap::new()),
        }
    }

    pub fn start_transaction(&self, transaction_id: TransactionId, participating_nodes: Vec<NodeId>) -> Result<(), String> {
        // Validate participating nodes are within range.
        for &node in &participating_nodes {
            if node == 0 || node > self.num_nodes {
                return Err(format!("Node {} is out of valid range", node));
            }
        }
        let mut tx_map = self.transactions.write().map_err(|_| "Lock poisoned".to_string())?;
        if tx_map.contains_key(&transaction_id) {
            return Err("Transaction ID already exists".to_string());
        }
        tx_map.insert(transaction_id, Mutex::new(Transaction::new(participating_nodes)));
        Ok(())
    }

    pub fn receive_vote(&self, transaction_id: TransactionId, node_id: NodeId, vote: Vote) -> Result<(), String> {
        let tx_map = self.transactions.read().map_err(|_| "Lock poisoned".to_string())?;
        let transaction_mutex = tx_map.get(&transaction_id).ok_or("Transaction not found".to_string())?;
        let mut transaction = transaction_mutex.lock().map_err(|_| "Lock poisoned".to_string())?;
        if transaction.state != TransactionState::Pending {
            return Err("Transaction is not in Pending state".to_string());
        }
        if !transaction.participants.contains(&node_id) {
            return Err("Node is not a participant in this transaction".to_string());
        }
        // If a vote from this node already exists, disallow duplicate vote.
        if transaction.votes.contains_key(&node_id) {
            return Err("Vote from this node already recorded".to_string());
        }
        transaction.votes.insert(node_id, vote);
        Ok(())
    }

    pub fn make_decision(&self, transaction_id: TransactionId) -> Result<TransactionState, String> {
        let tx_map = self.transactions.read().map_err(|_| "Lock poisoned".to_string())?;
        let transaction_mutex = tx_map.get(&transaction_id).ok_or("Transaction not found".to_string())?;
        let mut transaction = transaction_mutex.lock().map_err(|_| "Lock poisoned".to_string())?;
        if transaction.state != TransactionState::Pending {
            return Err("Decision already made for this transaction".to_string());
        }
        if transaction.votes.len() != transaction.participants.len() {
            return Err("Not all votes received".to_string());
        }
        // Determine the decision: if any vote is Abort, abort the transaction.
        let mut decision = TransactionState::Committed;
        for &vote in transaction.votes.values() {
            if vote == Vote::Abort {
                decision = TransactionState::Aborted;
                break;
            }
        }
        transaction.state = decision;
        Ok(decision)
    }

    pub fn get_transaction_state(&self, transaction_id: TransactionId) -> Result<TransactionState, String> {
        let tx_map = self.transactions.read().map_err(|_| "Lock poisoned".to_string())?;
        let transaction_mutex = tx_map.get(&transaction_id).ok_or("Transaction not found".to_string())?;
        let transaction = transaction_mutex.lock().map_err(|_| "Lock poisoned".to_string())?;
        Ok(transaction.state)
    }
}