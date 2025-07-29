use std::collections::{HashMap, HashSet};
use std::fmt;
use std::sync::{Arc, Mutex, RwLock};
use std::time::{Duration, Instant};
use uuid::Uuid;

/// Status of a transaction
#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum TransactionStatus {
    Preparing,
    Committed,
    RolledBack,
}

/// Response from a participant during the prepare phase
#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum ParticipantResponse {
    ACK,
    NAK,
}

/// Errors returned by the DTC operations
#[derive(Debug)]
pub enum DTCError {
    UnknownTransaction,
    UnknownParticipant,
    ParticipantAlreadyRegistered,
    InvalidTransactionState,
    TransactionInProgress,
    NoParticipantsRegistered,
    NotAllParticipantsResponded,
    Timeout,
    Internal(String),
}

impl fmt::Display for DTCError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            DTCError::UnknownTransaction => write!(f, "Unknown transaction"),
            DTCError::UnknownParticipant => write!(f, "Unknown participant"),
            DTCError::ParticipantAlreadyRegistered => write!(f, "Participant already registered"),
            DTCError::InvalidTransactionState => write!(f, "Invalid transaction state"),
            DTCError::TransactionInProgress => write!(f, "Transaction is still in progress"),
            DTCError::NoParticipantsRegistered => write!(f, "No participants registered"),
            DTCError::NotAllParticipantsResponded => write!(f, "Not all participants have responded"),
            DTCError::Timeout => write!(f, "Transaction timed out"),
            DTCError::Internal(msg) => write!(f, "Internal error: {}", msg),
        }
    }
}

impl std::error::Error for DTCError {}

/// Participant struct representing a service that can participate in a transaction
pub struct Participant {
    name: String,
}

impl Participant {
    fn new(name: String) -> Self {
        Participant { name }
    }
}

/// Transaction struct that holds the state of a transaction
struct Transaction {
    id: String,
    status: TransactionStatus,
    participants: HashSet<String>,
    ack_responses: HashSet<String>,
    nak_responses: HashSet<String>,
    created_at: Instant,
}

impl Transaction {
    fn new(id: String, participants: HashSet<String>) -> Self {
        Transaction {
            id,
            status: TransactionStatus::Preparing,
            participants,
            ack_responses: HashSet::new(),
            nak_responses: HashSet::new(),
            created_at: Instant::now(),
        }
    }

    fn is_complete(&self) -> bool {
        self.status == TransactionStatus::Committed || self.status == TransactionStatus::RolledBack
    }

    fn can_commit(&self) -> bool {
        // Can commit if all participants have acknowledged
        self.ack_responses.len() == self.participants.len()
    }

    fn should_rollback(&self) -> bool {
        // Should rollback if any participant has rejected
        !self.nak_responses.is_empty()
    }

    fn has_all_responses(&self) -> bool {
        // All participants have either acknowledged or rejected
        (self.ack_responses.len() + self.nak_responses.len()) == self.participants.len()
    }

    fn is_timed_out(&self, timeout: Duration) -> bool {
        self.created_at.elapsed() > timeout
    }
}

/// Distributed Transaction Coordinator
pub struct DTC {
    participants: RwLock<HashMap<String, Arc<Participant>>>,
    transactions: RwLock<HashMap<String, Arc<Mutex<Transaction>>>>,
    timeout: Duration,
}

impl DTC {
    /// Create a new DTC with default timeout (5 seconds)
    pub fn new() -> Self {
        DTC {
            participants: RwLock::new(HashMap::new()),
            transactions: RwLock::new(HashMap::new()),
            timeout: Duration::from_secs(5),
        }
    }

    /// Create a new DTC with a custom timeout
    pub fn new_with_timeout(timeout: Duration) -> Self {
        DTC {
            participants: RwLock::new(HashMap::new()),
            transactions: RwLock::new(HashMap::new()),
            timeout,
        }
    }

    /// Register a new participant with the DTC
    pub fn register_participant(&self, name: String) -> Result<(), DTCError> {
        let mut participants = self.participants.write().unwrap();
        
        if participants.contains_key(&name) {
            return Err(DTCError::ParticipantAlreadyRegistered);
        }
        
        participants.insert(name.clone(), Arc::new(Participant::new(name)));
        
        println!("Registered participant: {}", participants.len());
        Ok(())
    }

    /// Start a new transaction
    pub fn start_transaction(&self) -> Result<String, DTCError> {
        let participants = self.participants.read().unwrap();
        
        if participants.is_empty() {
            return Err(DTCError::NoParticipantsRegistered);
        }
        
        let transaction_id = Uuid::new_v4().to_string();
        
        let participant_names: HashSet<String> = participants.keys().cloned().collect();
        
        let transaction = Transaction::new(transaction_id.clone(), participant_names);
        
        let mut transactions = self.transactions.write().unwrap();
        transactions.insert(transaction_id.clone(), Arc::new(Mutex::new(transaction)));
        
        println!("Started transaction: {}", transaction_id);
        Ok(transaction_id)
    }

    /// Submit a participant's response to a transaction
    pub fn participant_response(
        &self,
        tx_id: &str,
        participant: String,
        response: ParticipantResponse,
    ) -> Result<(), DTCError> {
        // Check if participant exists
        let participants = self.participants.read().unwrap();
        if !participants.contains_key(&participant) {
            return Err(DTCError::UnknownParticipant);
        }
        
        // Check if transaction exists
        let transactions = self.transactions.read().unwrap();
        let transaction = match transactions.get(tx_id) {
            Some(tx) => tx.clone(),
            None => return Err(DTCError::UnknownTransaction),
        };
        
        let mut tx = transaction.lock().unwrap();
        
        // Check if transaction is still in preparing phase
        if tx.status != TransactionStatus::Preparing {
            return Err(DTCError::InvalidTransactionState);
        }
        
        // Check if participant is part of this transaction
        if !tx.participants.contains(&participant) {
            return Err(DTCError::UnknownParticipant);
        }
        
        // Record the response
        match response {
            ParticipantResponse::ACK => {
                tx.nak_responses.remove(&participant); // Handle idempotency
                tx.ack_responses.insert(participant.clone());
                println!("Participant {} ACKed transaction {}", participant, tx_id);
            }
            ParticipantResponse::NAK => {
                tx.ack_responses.remove(&participant); // Handle idempotency
                tx.nak_responses.insert(participant.clone());
                println!("Participant {} NAKed transaction {}", participant, tx_id);
            }
        }
        
        Ok(())
    }

    /// Drive the transaction to completion if possible
    pub fn drive_transaction_completion(&self, tx_id: &str) -> Result<(), DTCError> {
        // Check if transaction exists
        let transactions = self.transactions.read().unwrap();
        let transaction = match transactions.get(tx_id) {
            Some(tx) => tx.clone(),
            None => return Err(DTCError::UnknownTransaction),
        };
        
        let mut tx = transaction.lock().unwrap();
        
        // If transaction is already complete, return error
        if tx.is_complete() {
            return Err(DTCError::InvalidTransactionState);
        }
        
        // Check for timeout
        if tx.is_timed_out(self.timeout) {
            println!("Transaction {} timed out - rolling back", tx_id);
            tx.status = TransactionStatus::RolledBack;
            return Ok(());
        }
        
        // If not all participants have responded and no NAKs, return error
        if !tx.has_all_responses() && !tx.should_rollback() {
            return Err(DTCError::NotAllParticipantsResponded);
        }
        
        // Determine if we should commit or rollback
        if tx.should_rollback() {
            println!("Rolling back transaction {}", tx_id);
            tx.status = TransactionStatus::RolledBack;
        } else if tx.can_commit() {
            println!("Committing transaction {}", tx_id);
            tx.status = TransactionStatus::Committed;
        } else {
            return Err(DTCError::Internal("Transaction in invalid state".to_string()));
        }
        
        Ok(())
    }

    /// Get the current status of a transaction
    pub fn get_transaction_status(&self, tx_id: &str) -> Result<TransactionStatus, DTCError> {
        let transactions = self.transactions.read().unwrap();
        
        let transaction = match transactions.get(tx_id) {
            Some(tx) => tx.clone(),
            None => return Err(DTCError::UnknownTransaction),
        };
        
        let tx = transaction.lock().unwrap();
        Ok(tx.status)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_register_participant() {
        let dtc = DTC::new();
        assert!(dtc.register_participant("service1".to_string()).is_ok());
        assert!(dtc.register_participant("service2".to_string()).is_ok());
        assert!(dtc.register_participant("service1".to_string()).is_err());
    }

    #[test]
    fn test_start_transaction() {
        let dtc = DTC::new();
        dtc.register_participant("service1".to_string()).unwrap();
        
        let tx_id = dtc.start_transaction().unwrap();
        assert!(Uuid::parse_str(&tx_id).is_ok());
        
        let status = dtc.get_transaction_status(&tx_id).unwrap();
        assert_eq!(status, TransactionStatus::Preparing);
    }

    #[test]
    fn test_successful_transaction() {
        let dtc = DTC::new();
        dtc.register_participant("service1".to_string()).unwrap();
        dtc.register_participant("service2".to_string()).unwrap();
        
        let tx_id = dtc.start_transaction().unwrap();
        
        dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
        dtc.participant_response(&tx_id, "service2".to_string(), ParticipantResponse::ACK).unwrap();
        
        dtc.drive_transaction_completion(&tx_id).unwrap();
        
        let status = dtc.get_transaction_status(&tx_id).unwrap();
        assert_eq!(status, TransactionStatus::Committed);
    }

    #[test]
    fn test_failed_transaction() {
        let dtc = DTC::new();
        dtc.register_participant("service1".to_string()).unwrap();
        dtc.register_participant("service2".to_string()).unwrap();
        
        let tx_id = dtc.start_transaction().unwrap();
        
        dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
        dtc.participant_response(&tx_id, "service2".to_string(), ParticipantResponse::NAK).unwrap();
        
        dtc.drive_transaction_completion(&tx_id).unwrap();
        
        let status = dtc.get_transaction_status(&tx_id).unwrap();
        assert_eq!(status, TransactionStatus::RolledBack);
    }
}