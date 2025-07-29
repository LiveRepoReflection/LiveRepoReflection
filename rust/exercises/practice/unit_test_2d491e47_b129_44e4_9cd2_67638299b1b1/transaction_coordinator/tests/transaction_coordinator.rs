use std::collections::HashSet;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use uuid::Uuid;
use transaction_coordinator::{
    DTC, Participant, TransactionStatus, ParticipantResponse, DTCError
};

#[test]
fn test_register_participant() {
    let dtc = DTC::new();
    assert!(dtc.register_participant("service1".to_string()).is_ok());
    assert!(dtc.register_participant("service2".to_string()).is_ok());
    
    // Registering the same participant twice should fail
    assert!(dtc.register_participant("service1".to_string()).is_err());
}

#[test]
fn test_start_transaction() {
    let dtc = DTC::new();
    dtc.register_participant("service1".to_string()).unwrap();
    dtc.register_participant("service2".to_string()).unwrap();
    
    let tx_id = dtc.start_transaction().unwrap();
    assert!(uuid::Uuid::parse_str(&tx_id).is_ok());
    
    // Check transaction was created with correct status
    let status = dtc.get_transaction_status(&tx_id).unwrap();
    assert_eq!(status, TransactionStatus::Preparing);
}

#[test]
fn test_successful_transaction() {
    let dtc = DTC::new();
    dtc.register_participant("service1".to_string()).unwrap();
    dtc.register_participant("service2".to_string()).unwrap();
    
    let tx_id = dtc.start_transaction().unwrap();
    
    // Both participants acknowledge
    dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
    dtc.participant_response(&tx_id, "service2".to_string(), ParticipantResponse::ACK).unwrap();
    
    // Since all participants acknowledged, the transaction should be committed
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
    
    // One participant acknowledges, one rejects
    dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
    dtc.participant_response(&tx_id, "service2".to_string(), ParticipantResponse::NAK).unwrap();
    
    // Since one participant rejected, the transaction should be rolled back
    dtc.drive_transaction_completion(&tx_id).unwrap();
    
    let status = dtc.get_transaction_status(&tx_id).unwrap();
    assert_eq!(status, TransactionStatus::RolledBack);
}

#[test]
fn test_timeout_handling() {
    let dtc = DTC::new_with_timeout(Duration::from_millis(100));
    dtc.register_participant("service1".to_string()).unwrap();
    dtc.register_participant("service2".to_string()).unwrap();
    
    let tx_id = dtc.start_transaction().unwrap();
    
    // Only one participant responds
    dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
    
    // Wait for timeout
    thread::sleep(Duration::from_millis(200));
    
    // Transaction should be rolled back due to timeout from service2
    dtc.drive_transaction_completion(&tx_id).unwrap();
    
    let status = dtc.get_transaction_status(&tx_id).unwrap();
    assert_eq!(status, TransactionStatus::RolledBack);
}

#[test]
fn test_idempotency() {
    let dtc = DTC::new();
    dtc.register_participant("service1".to_string()).unwrap();
    
    let tx_id = dtc.start_transaction().unwrap();
    
    // Send the same response multiple times, should work fine
    dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
    dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
    
    dtc.drive_transaction_completion(&tx_id).unwrap();
    
    // Transaction should be committed
    let status = dtc.get_transaction_status(&tx_id).unwrap();
    assert_eq!(status, TransactionStatus::Committed);
}

#[test]
fn test_unknown_transaction() {
    let dtc = DTC::new();
    let random_id = Uuid::new_v4().to_string();
    
    // Attempting to get status of unknown transaction should fail
    assert!(dtc.get_transaction_status(&random_id).is_err());
    
    // Attempting to respond to unknown transaction should fail
    assert!(dtc.participant_response(&random_id, "service1".to_string(), ParticipantResponse::ACK).is_err());
}

#[test]
fn test_unknown_participant() {
    let dtc = DTC::new();
    dtc.register_participant("service1".to_string()).unwrap();
    
    let tx_id = dtc.start_transaction().unwrap();
    
    // Attempting to get response from unknown participant should fail
    assert!(dtc.participant_response(&tx_id, "unknown".to_string(), ParticipantResponse::ACK).is_err());
}

#[test]
fn test_concurrent_transactions() {
    let dtc = Arc::new(DTC::new());
    dtc.register_participant("service1".to_string()).unwrap();
    dtc.register_participant("service2".to_string()).unwrap();
    
    let num_transactions = 5;
    let tx_ids = Arc::new(Mutex::new(Vec::new()));
    
    let threads: Vec<_> = (0..num_transactions)
        .map(|_| {
            let dtc_clone = Arc::clone(&dtc);
            let tx_ids_clone = Arc::clone(&tx_ids);
            
            thread::spawn(move || {
                let tx_id = dtc_clone.start_transaction().unwrap();
                
                // Record transaction ID
                tx_ids_clone.lock().unwrap().push(tx_id.clone());
                
                // Both participants acknowledge
                dtc_clone.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
                dtc_clone.participant_response(&tx_id, "service2".to_string(), ParticipantResponse::ACK).unwrap();
                
                // Complete transaction
                dtc_clone.drive_transaction_completion(&tx_id).unwrap();
                
                // Verify transaction was committed
                let status = dtc_clone.get_transaction_status(&tx_id).unwrap();
                assert_eq!(status, TransactionStatus::Committed);
            })
        })
        .collect();
    
    // Wait for all threads to complete
    for handle in threads {
        handle.join().unwrap();
    }
    
    // Ensure all transactions were started and completed successfully
    let ids = tx_ids.lock().unwrap();
    assert_eq!(ids.len(), num_transactions);
    
    // Ensure all transaction IDs are unique
    let unique_ids: HashSet<_> = ids.iter().cloned().collect();
    assert_eq!(unique_ids.len(), num_transactions);
}

#[test]
fn test_completed_transaction_handling() {
    let dtc = DTC::new();
    dtc.register_participant("service1".to_string()).unwrap();
    
    let tx_id = dtc.start_transaction().unwrap();
    
    // Complete the transaction
    dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
    dtc.drive_transaction_completion(&tx_id).unwrap();
    
    // Try to respond to an already committed transaction
    let result = dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::NAK);
    assert!(result.is_err());
    
    // Try to complete an already completed transaction
    let result = dtc.drive_transaction_completion(&tx_id);
    assert!(result.is_err());
}

#[test]
fn test_transaction_with_multiple_participants() {
    let dtc = DTC::new();
    for i in 1..10 {
        dtc.register_participant(format!("service{}", i)).unwrap();
    }
    
    let tx_id = dtc.start_transaction().unwrap();
    
    // All participants acknowledge
    for i in 1..10 {
        dtc.participant_response(&tx_id, format!("service{}", i), ParticipantResponse::ACK).unwrap();
    }
    
    dtc.drive_transaction_completion(&tx_id).unwrap();
    
    // Transaction should be committed
    let status = dtc.get_transaction_status(&tx_id).unwrap();
    assert_eq!(status, TransactionStatus::Committed);
}

#[test]
fn test_partial_responses() {
    let dtc = DTC::new();
    dtc.register_participant("service1".to_string()).unwrap();
    dtc.register_participant("service2".to_string()).unwrap();
    dtc.register_participant("service3".to_string()).unwrap();
    
    let tx_id = dtc.start_transaction().unwrap();
    
    // Only some participants respond
    dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
    
    // Should not be able to complete yet - not all participants have responded
    let result = dtc.drive_transaction_completion(&tx_id);
    assert!(result.is_err());
    
    // Add more responses
    dtc.participant_response(&tx_id, "service2".to_string(), ParticipantResponse::ACK).unwrap();
    dtc.participant_response(&tx_id, "service3".to_string(), ParticipantResponse::ACK).unwrap();
    
    // Now should be able to complete
    dtc.drive_transaction_completion(&tx_id).unwrap();
    
    let status = dtc.get_transaction_status(&tx_id).unwrap();
    assert_eq!(status, TransactionStatus::Committed);
}

#[test]
fn test_mixed_responses() {
    let dtc = DTC::new();
    dtc.register_participant("service1".to_string()).unwrap();
    dtc.register_participant("service2".to_string()).unwrap();
    dtc.register_participant("service3".to_string()).unwrap();
    
    let tx_id = dtc.start_transaction().unwrap();
    
    // Mixed responses
    dtc.participant_response(&tx_id, "service1".to_string(), ParticipantResponse::ACK).unwrap();
    dtc.participant_response(&tx_id, "service2".to_string(), ParticipantResponse::NAK).unwrap();
    dtc.participant_response(&tx_id, "service3".to_string(), ParticipantResponse::ACK).unwrap();
    
    dtc.drive_transaction_completion(&tx_id).unwrap();
    
    // Transaction should be rolled back due to NAK
    let status = dtc.get_transaction_status(&tx_id).unwrap();
    assert_eq!(status, TransactionStatus::RolledBack);
}