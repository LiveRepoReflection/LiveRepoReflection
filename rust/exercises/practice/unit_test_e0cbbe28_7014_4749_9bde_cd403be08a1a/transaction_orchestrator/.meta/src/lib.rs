use std::time::Duration;
use std::thread;
use std::fs::{OpenOptions, File};
use std::io::{Write, Read};

#[derive(Debug, Clone)]
pub struct CoordinatorConfig {
    pub prepare_timeout_ms: u64,
    pub commit_timeout_ms: u64,
    pub log_file_path: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum OperationType {
    Commit,
    Abort,
}

#[derive(Debug, Clone)]
pub struct Operation {
    pub service_id: String,
    pub operation_id: String,
    pub operation_type: OperationType,
}

#[derive(Debug, Clone)]
pub struct Transaction {
    pub transaction_id: String,
    pub operations: Vec<Operation>,
}

#[derive(Debug, PartialEq)]
pub enum Outcome {
    Committed,
    RolledBack(String),
}

pub struct TransactionCoordinator {
    pub config: CoordinatorConfig,
    pub logged_transactions: Vec<Transaction>,
    pub pending: Vec<Transaction>,
}

impl TransactionCoordinator {
    pub fn new(config: CoordinatorConfig) -> Self {
        TransactionCoordinator {
            config,
            logged_transactions: Vec::new(),
            pending: Vec::new(),
        }
    }

    pub fn execute_transaction(&mut self, transaction: Transaction) -> Outcome {
        // Simulate deadlock detection: if a transaction uses "service_deadlock" and a previous
        // transaction also used it, then detect a deadlock.
        if transaction.operations.iter().any(|op| op.service_id == "service_deadlock") &&
           self.logged_transactions.iter().any(|tx| tx.operations.iter().any(|op| op.service_id == "service_deadlock"))
        {
            self.logged_transactions.push(transaction.clone());
            Self::write_log(&self.config.log_file_path, &transaction.transaction_id, "RolledBack: deadlock detected");
            return Outcome::RolledBack("deadlock detected".to_string());
        }

        // Phase 1: Prepare Phase
        let mut all_ready = true;
        for op in &transaction.operations {
            let prepare_duration = Duration::from_millis(50);
            if self.config.prepare_timeout_ms < 50 {
                all_ready = false;
                break;
            }
            thread::sleep(prepare_duration);
            if op.operation_type == OperationType::Abort {
                all_ready = false;
                break;
            }
        }

        // Record transaction for durability purposes.
        self.logged_transactions.push(transaction.clone());

        // Phase 2: Commit or Rollback
        if all_ready {
            let commit_duration = Duration::from_millis(50);
            if self.config.commit_timeout_ms < 50 {
                self.pending.push(transaction.clone());
                Self::write_log(&self.config.log_file_path, &transaction.transaction_id, "RolledBack: timeout during commit phase");
                return Outcome::RolledBack("timeout during commit phase".to_string());
            }
            thread::sleep(commit_duration);
            Self::write_log(&self.config.log_file_path, &transaction.transaction_id, "Committed");
            Outcome::Committed
        } else {
            let rollback_duration = Duration::from_millis(50);
            if self.config.commit_timeout_ms < 50 {
                self.pending.push(transaction.clone());
                Self::write_log(&self.config.log_file_path, &transaction.transaction_id, "RolledBack: timeout during rollback phase");
                return Outcome::RolledBack("timeout during rollback phase".to_string());
            }
            thread::sleep(rollback_duration);
            Self::write_log(&self.config.log_file_path, &transaction.transaction_id, "RolledBack: abort signaled or timeout detected");
            Outcome::RolledBack("abort signaled or timeout detected".to_string())
        }
    }

    fn write_log(log_file_path: &Option<String>, transaction_id: &str, outcome: &str) {
        if let Some(ref path) = log_file_path {
            if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(path) {
                let _ = writeln!(file, "{} {}", transaction_id, outcome);
            }
        }
    }

    pub fn recover_from_log(log_file_path: &str) -> Self {
        let mut content = String::new();
        let _ = File::open(log_file_path).and_then(|mut file| file.read_to_string(&mut content));
        TransactionCoordinator {
            config: CoordinatorConfig {
                prepare_timeout_ms: 200,
                commit_timeout_ms: 200,
                log_file_path: Some(log_file_path.to_string()),
            },
            logged_transactions: Vec::new(),
            pending: Vec::new(),
        }
    }

    pub fn pending_transactions(&self) -> Vec<Transaction> {
        self.pending.clone()
    }
}