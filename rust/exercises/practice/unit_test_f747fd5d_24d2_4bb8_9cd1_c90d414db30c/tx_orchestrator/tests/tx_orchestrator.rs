use std::collections::HashMap;
use tx_orchestrator::orchestrate_transaction;

#[test]
fn test_successful_transaction() {
    let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    let transaction_id = "tx123".to_string();
    let prepare_order = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    
    let prepare_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);
    
    let commit_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);

    let result = orchestrate_transaction(
        services,
        transaction_id,
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_ok());
}

#[test]
fn test_prepare_failure() {
    let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    let transaction_id = "tx123".to_string();
    let prepare_order = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    
    let prepare_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), false), // Service B fails to prepare
        ("serviceC".to_string(), true),
    ]);
    
    let commit_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);

    let result = orchestrate_transaction(
        services,
        transaction_id,
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_err());
    let error_message = result.unwrap_err();
    assert!(error_message.contains("Transaction tx123 failed: Prepare failed for serviceB"));
}

#[test]
fn test_commit_failure() {
    let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    let transaction_id = "tx123".to_string();
    let prepare_order = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    
    let prepare_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);
    
    let commit_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), false), // Service B fails to commit
        ("serviceC".to_string(), true),
    ]);

    let result = orchestrate_transaction(
        services,
        transaction_id,
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_err());
    let error_message = result.unwrap_err();
    assert!(error_message.contains("Transaction tx123 failed: Commit failed for serviceB"));
}

#[test]
fn test_different_prepare_order() {
    let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    let transaction_id = "tx123".to_string();
    // Different order for preparation
    let prepare_order = vec!["serviceC".to_string(), "serviceA".to_string(), "serviceB".to_string()];
    
    let prepare_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);
    
    let commit_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);

    let result = orchestrate_transaction(
        services,
        transaction_id,
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_ok());
}

#[test]
fn test_early_prepare_failure_with_rollback() {
    let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    let transaction_id = "tx456".to_string();
    let prepare_order = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    
    let prepare_successes = HashMap::from([
        ("serviceA".to_string(), false), // First service fails
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);
    
    let commit_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);

    let result = orchestrate_transaction(
        services,
        transaction_id,
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_err());
    let error_message = result.unwrap_err();
    assert!(error_message.contains("Transaction tx456 failed: Prepare failed for serviceA"));
    // No rollbacks should be needed since first service failed
}

#[test]
fn test_midway_prepare_failure_with_rollback() {
    let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string(), "serviceD".to_string()];
    let transaction_id = "tx789".to_string();
    let prepare_order = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string(), "serviceD".to_string()];
    
    let prepare_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), false), // Third service fails
        ("serviceD".to_string(), true),
    ]);
    
    let commit_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
        ("serviceD".to_string(), true),
    ]);

    let result = orchestrate_transaction(
        services,
        transaction_id,
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_err());
    let error_message = result.unwrap_err();
    assert!(error_message.contains("Transaction tx789 failed: Prepare failed for serviceC"));
    // Rollbacks should happen for serviceB and serviceA
}

#[test]
fn test_invalid_prepare_order() {
    let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    let transaction_id = "tx101".to_string();
    // Missing serviceC, and contains an unknown serviceD
    let prepare_order = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceD".to_string()];
    
    let prepare_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);
    
    let commit_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);

    let result = orchestrate_transaction(
        services,
        transaction_id.clone(),
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_err());
    let error_message = result.unwrap_err();
    assert!(error_message.contains(&format!("Transaction {} failed: Invalid prepare order", transaction_id)));
}

#[test]
fn test_missing_prepare_success_info() {
    let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    let transaction_id = "tx102".to_string();
    let prepare_order = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    
    // Missing information for serviceC
    let prepare_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
    ]);
    
    let commit_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);

    let result = orchestrate_transaction(
        services,
        transaction_id.clone(),
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_err());
    let error_message = result.unwrap_err();
    assert!(error_message.contains(&format!("Transaction {} failed: Missing prepare success information", transaction_id)));
}

#[test]
fn test_missing_commit_success_info() {
    let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    let transaction_id = "tx103".to_string();
    let prepare_order = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
    
    let prepare_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
        ("serviceC".to_string(), true),
    ]);
    
    // Missing information for serviceC
    let commit_successes = HashMap::from([
        ("serviceA".to_string(), true),
        ("serviceB".to_string(), true),
    ]);

    let result = orchestrate_transaction(
        services,
        transaction_id.clone(),
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_err());
    let error_message = result.unwrap_err();
    assert!(error_message.contains(&format!("Transaction {} failed: Missing commit success information", transaction_id)));
}

#[test]
fn test_empty_services() {
    let services: Vec<String> = vec![];
    let transaction_id = "tx104".to_string();
    let prepare_order: Vec<String> = vec![];
    
    let prepare_successes = HashMap::new();
    let commit_successes = HashMap::new();

    let result = orchestrate_transaction(
        services,
        transaction_id.clone(),
        prepare_order,
        prepare_successes,
        commit_successes,
    );

    assert!(result.is_ok(), "Empty services list should be valid and transaction should succeed trivially");
}