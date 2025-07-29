use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use dist_txcoord::{Coordinator, Participant, TransactionError};

#[derive(Clone)]
enum Behavior {
    Commit,
    Abort,
    Timeout,
}

struct MockParticipant {
    id: usize,
    behavior: Behavior,
    log: Arc<Mutex<Vec<String>>>,
}

impl MockParticipant {
    fn new(id: usize, behavior: Behavior, log: Arc<Mutex<Vec<String>>>) -> Self {
        Self { id, behavior, log }
    }
}

impl Participant for MockParticipant {
    fn prepare(&self, tx_id: &str) -> Result<(), ()> {
        match self.behavior {
            Behavior::Timeout => {
                // Simulate a timeout by sleeping longer than the coordinator timeout threshold
                thread::sleep(Duration::from_millis(200));
                let mut log = self.log.lock().unwrap();
                log.push(format!("Participant {} timeout in prepare for tx {}", self.id, tx_id));
                Err(())
            }
            Behavior::Abort => {
                let mut log = self.log.lock().unwrap();
                log.push(format!("Participant {} votes abort for tx {}", self.id, tx_id));
                Err(())
            }
            Behavior::Commit => {
                let mut log = self.log.lock().unwrap();
                log.push(format!("Participant {} votes commit for tx {}", self.id, tx_id));
                Ok(())
            }
        }
    }
    
    fn commit(&self, tx_id: &str) -> Result<(), ()> {
        let mut log = self.log.lock().unwrap();
        log.push(format!("Participant {} commits tx {}", self.id, tx_id));
        Ok(())
    }
    
    fn abort(&self, tx_id: &str) -> Result<(), ()> {
        let mut log = self.log.lock().unwrap();
        log.push(format!("Participant {} aborts tx {}", self.id, tx_id));
        Ok(())
    }
}

#[test]
fn test_successful_transaction() {
    let log = Arc::new(Mutex::new(Vec::new()));
    let participant1 = Box::new(MockParticipant::new(1, Behavior::Commit, Arc::clone(&log)));
    let participant2 = Box::new(MockParticipant::new(2, Behavior::Commit, Arc::clone(&log)));
    let participants: Vec<Box<dyn Participant + Send>> = vec![participant1, participant2];
    
    let mut coord = Coordinator::new();
    let tx_id = coord.start_transaction(participants);
    
    // Execute the transaction; expecting a commit since all participants vote commit.
    let result = coord.complete_transaction(&tx_id);
    assert!(result.is_ok(), "Transaction should commit successfully");

    let log_data = log.lock().unwrap();
    assert!(log_data.iter().any(|entry| entry.contains("votes commit")),
            "At least one participant should vote commit");
    assert!(log_data.iter().any(|entry| entry.contains("commits tx")),
            "Participants should commit transaction");
}

#[test]
fn test_abort_transaction_due_to_abort_vote() {
    let log = Arc::new(Mutex::new(Vec::new()));
    // First participant votes commit, second votes abort.
    let participant1 = Box::new(MockParticipant::new(1, Behavior::Commit, Arc::clone(&log)));
    let participant2 = Box::new(MockParticipant::new(2, Behavior::Abort, Arc::clone(&log)));
    let participants: Vec<Box<dyn Participant + Send>> = vec![participant1, participant2];
    
    let mut coord = Coordinator::new();
    let tx_id = coord.start_transaction(participants);
    
    let result = coord.complete_transaction(&tx_id);
    assert!(result.is_err(), "Transaction should abort due to an abort vote");

    let log_data = log.lock().unwrap();
    assert!(log_data.iter().any(|entry| entry.contains("votes abort")),
            "A participant should vote abort");
    assert!(log_data.iter().any(|entry| entry.contains("aborts tx")),
            "Participants should execute an abort operation");
}

#[test]
fn test_timeout_causes_transaction_abort() {
    let log = Arc::new(Mutex::new(Vec::new()));
    // First participant votes commit, second simulates a timeout.
    let participant1 = Box::new(MockParticipant::new(1, Behavior::Commit, Arc::clone(&log)));
    let participant2 = Box::new(MockParticipant::new(2, Behavior::Timeout, Arc::clone(&log)));
    let participants: Vec<Box<dyn Participant + Send>> = vec![participant1, participant2];
    
    let mut coord = Coordinator::new();
    let tx_id = coord.start_transaction(participants);
    
    let start = Instant::now();
    let result = coord.complete_transaction(&tx_id);
    let duration = start.elapsed();
    
    // Ensure that the timeout occurred within an appropriate duration.
    assert!(duration < Duration::from_millis(300), "Timeout should occur promptly");
    assert!(result.is_err(), "Transaction should abort due to a timeout");
    
    let log_data = log.lock().unwrap();
    assert!(log_data.iter().any(|entry| entry.contains("timeout")),
            "Timeout event should be logged by a participant");
    assert!(log_data.iter().any(|entry| entry.contains("aborts tx")),
            "Participants should abort transaction due to timeout");
}

#[test]
fn test_concurrent_transactions() {
    let transaction_count = 50;
    let mut handles = Vec::new();
    
    for i in 0..transaction_count {
        let handle = thread::spawn(move || {
            let log = Arc::new(Mutex::new(Vec::new()));
            // For even-indexed transactions, all participants commit.
            // For odd-indexed transactions, one participant votes abort.
            let behavior = if i % 2 == 0 { Behavior::Commit } else { Behavior::Abort };
            let participant1 = Box::new(MockParticipant::new(1, behavior.clone(), Arc::clone(&log)));
            let participant2 = Box::new(MockParticipant::new(2, Behavior::Commit, Arc::clone(&log)));
            let participants: Vec<Box<dyn Participant + Send>> = vec![participant1, participant2];
            
            let mut coord = Coordinator::new();
            let tx_id = coord.start_transaction(participants);
            let result = coord.complete_transaction(&tx_id);
            
            (i, result, log)
        });
        handles.push(handle);
    }
    
    for handle in handles {
        let (i, result, log) = handle.join().expect("Thread panicked");
        if i % 2 == 0 {
            assert!(result.is_ok(), "Even transaction should commit");
            let log_data = log.lock().unwrap();
            assert!(log_data.iter().any(|entry| entry.contains("commits tx")),
                    "Commit should be logged for even transaction");
        } else {
            assert!(result.is_err(), "Odd transaction should abort");
            let log_data = log.lock().unwrap();
            assert!(log_data.iter().any(|entry| entry.contains("votes abort") || entry.contains("aborts tx")),
                    "Abort should be logged for odd transaction");
        }
    }
}

#[test]
fn test_recovery_from_coordinator_failure() {
    let log = Arc::new(Mutex::new(Vec::new()));
    let participant1 = Box::new(MockParticipant::new(1, Behavior::Commit, Arc::clone(&log)));
    let participant2 = Box::new(MockParticipant::new(2, Behavior::Commit, Arc::clone(&log)));
    let participants: Vec<Box<dyn Participant + Send>> = vec![participant1, participant2];
    
    // Start a transaction but simulate a coordinator failure by not calling complete_transaction.
    let mut coord = Coordinator::new();
    let tx_id = coord.start_transaction(participants);
    
    // Simulate failure recovery.
    coord.recover();
    
    // After recovery, assume that the transaction status is resolved.
    let status = coord.get_transaction_status(&tx_id).expect("Transaction should exist after recovery");
    assert_eq!(status, "committed", "Recovered transaction should be committed");
    
    let log_data = log.lock().unwrap();
    assert!(log_data.iter().any(|entry| entry.contains("commits tx")),
            "Participants should eventually commit transaction after recovery");
}