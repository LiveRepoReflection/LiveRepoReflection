use std::collections::{HashMap, HashSet};

/// Orchestrates a distributed transaction across multiple services.
///
/// # Arguments
///
/// * `services` - A list of service identifiers participating in the transaction
/// * `transaction_id` - Unique identifier for the transaction
/// * `prepare_order` - The order in which services should be prepared
/// * `prepare_successes` - Map of service IDs to their prepare operation success status
/// * `commit_successes` - Map of service IDs to their commit operation success status
///
/// # Returns
///
/// * `Ok(())` if the transaction completed successfully
/// * `Err(String)` with a descriptive error message if the transaction failed
pub fn orchestrate_transaction(
    services: Vec<String>,
    transaction_id: String,
    prepare_order: Vec<String>,
    prepare_successes: HashMap<String, bool>,
    commit_successes: HashMap<String, bool>,
) -> Result<(), String> {
    // Validate input parameters
    if !is_valid_permutation(&services, &prepare_order) {
        return Err(format!("Transaction {} failed: Invalid prepare order", transaction_id));
    }

    // Validate prepare and commit success maps contain all services
    for service in &services {
        if !prepare_successes.contains_key(service) {
            return Err(format!(
                "Transaction {} failed: Missing prepare success information",
                transaction_id
            ));
        }
        if !commit_successes.contains_key(service) {
            return Err(format!(
                "Transaction {} failed: Missing commit success information",
                transaction_id
            ));
        }
    }

    // Phase 1: Prepare
    let mut prepared_services = Vec::new();
    for service in &prepare_order {
        let prepare_result = prepare_service(service, &transaction_id, prepare_successes.get(service).unwrap());
        
        if prepare_result.is_ok() {
            prepared_services.push(service.clone());
        } else {
            // If prepare fails, rollback all previously prepared services in reverse order
            rollback_prepared_services(&prepared_services, &transaction_id);
            return Err(format!(
                "Transaction {} failed: Prepare failed for {}",
                transaction_id, service
            ));
        }
    }

    // Phase 2: Commit
    for service in &prepare_order {
        let commit_result = commit_service(
            service,
            &transaction_id,
            commit_successes.get(service).unwrap(),
        );
        
        if commit_result.is_err() {
            return Err(format!(
                "Transaction {} failed: Commit failed for {}",
                transaction_id, service
            ));
        }
    }

    // Transaction completed successfully
    Ok(())
}

/// Checks if prepare_order is a valid permutation of services
fn is_valid_permutation(services: &[String], prepare_order: &[String]) -> bool {
    if services.len() != prepare_order.len() {
        return false;
    }

    let services_set: HashSet<&String> = services.iter().collect();
    let prepare_order_set: HashSet<&String> = prepare_order.iter().collect();

    services_set == prepare_order_set
}

/// Simulates preparing a service for transaction
fn prepare_service(
    service: &str,
    transaction_id: &str,
    will_succeed: &bool,
) -> Result<(), String> {
    if *will_succeed {
        println!("Prepared {} for {}", service, transaction_id);
        Ok(())
    } else {
        println!("Prepare failed for {} for {}", service, transaction_id);
        Err(format!("Prepare failed for {}", service))
    }
}

/// Simulates committing a service
fn commit_service(
    service: &str,
    transaction_id: &str,
    will_succeed: &bool,
) -> Result<(), String> {
    if *will_succeed {
        println!("Committed {} for {}", service, transaction_id);
        Ok(())
    } else {
        println!("Commit failed for {} for {}", service, transaction_id);
        Err(format!("Commit failed for {}", service))
    }
}

/// Rollbacks all prepared services in reverse order
fn rollback_prepared_services(prepared_services: &[String], transaction_id: &str) {
    for service in prepared_services.iter().rev() {
        // Assume rollback always succeeds
        println!("Rolled back {} for {}", service, transaction_id);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_valid_permutation() {
        let services = vec![
            "service1".to_string(),
            "service2".to_string(),
            "service3".to_string(),
        ];

        // Valid permutation
        let valid_permutation = vec![
            "service2".to_string(),
            "service1".to_string(),
            "service3".to_string(),
        ];
        assert!(is_valid_permutation(&services, &valid_permutation));

        // Invalid permutation - different length
        let invalid_permutation1 = vec!["service1".to_string(), "service2".to_string()];
        assert!(!is_valid_permutation(&services, &invalid_permutation1));

        // Invalid permutation - different elements
        let invalid_permutation2 = vec![
            "service1".to_string(),
            "service2".to_string(),
            "service4".to_string(),
        ];
        assert!(!is_valid_permutation(&services, &invalid_permutation2));

        // Invalid permutation - duplicates
        let invalid_permutation3 = vec![
            "service1".to_string(),
            "service1".to_string(),
            "service2".to_string(),
        ];
        assert!(!is_valid_permutation(&services, &invalid_permutation3));
    }

    #[test]
    fn test_prepare_service() {
        // Success case
        let success = true;
        assert!(prepare_service("test", "tx1", &success).is_ok());

        // Failure case
        let failure = false;
        assert!(prepare_service("test", "tx1", &failure).is_err());
    }

    #[test]
    fn test_commit_service() {
        // Success case
        let success = true;
        assert!(commit_service("test", "tx1", &success).is_ok());

        // Failure case
        let failure = false;
        assert!(commit_service("test", "tx1", &failure).is_err());
    }

    #[test]
    fn test_simple_success_scenario() {
        let services = vec!["A".to_string(), "B".to_string()];
        let tx_id = "tx1".to_string();
        let prepare_order = vec!["A".to_string(), "B".to_string()];
        
        let prepare_successes = HashMap::from([
            ("A".to_string(), true),
            ("B".to_string(), true),
        ]);
        
        let commit_successes = HashMap::from([
            ("A".to_string(), true),
            ("B".to_string(), true),
        ]);

        let result = orchestrate_transaction(
            services,
            tx_id,
            prepare_order,
            prepare_successes,
            commit_successes,
        );
        
        assert!(result.is_ok());
    }

    #[test]
    fn test_prepare_failure_scenario() {
        let services = vec!["A".to_string(), "B".to_string()];
        let tx_id = "tx2".to_string();
        let prepare_order = vec!["A".to_string(), "B".to_string()];
        
        let prepare_successes = HashMap::from([
            ("A".to_string(), true),
            ("B".to_string(), false),  // B fails to prepare
        ]);
        
        let commit_successes = HashMap::from([
            ("A".to_string(), true),
            ("B".to_string(), true),
        ]);

        let result = orchestrate_transaction(
            services,
            tx_id,
            prepare_order,
            prepare_successes,
            commit_successes,
        );
        
        assert!(result.is_err());
        assert_eq!(
            result.unwrap_err(),
            "Transaction tx2 failed: Prepare failed for B"
        );
    }

    #[test]
    fn test_commit_failure_scenario() {
        let services = vec!["A".to_string(), "B".to_string()];
        let tx_id = "tx3".to_string();
        let prepare_order = vec!["A".to_string(), "B".to_string()];
        
        let prepare_successes = HashMap::from([
            ("A".to_string(), true),
            ("B".to_string(), true),
        ]);
        
        let commit_successes = HashMap::from([
            ("A".to_string(), true),
            ("B".to_string(), false),  // B fails to commit
        ]);

        let result = orchestrate_transaction(
            services,
            tx_id,
            prepare_order,
            prepare_successes,
            commit_successes,
        );
        
        assert!(result.is_err());
        assert_eq!(
            result.unwrap_err(),
            "Transaction tx3 failed: Commit failed for B"
        );
    }
}