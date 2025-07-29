use std::collections::HashMap;
use std::time::{Duration, Instant};
use std::fs::{File, OpenOptions};
use std::io::{Write, Read};

pub trait Participant {
    fn prepare(&self) -> Result<(), String>;
    fn commit(&self) -> Result<(), String>;
    fn rollback(&self) -> Result<(), String>;
}

#[derive(Clone, Debug, PartialEq)]
pub enum TransactionState {
    Preparing,
    Prepared,
    Committed,
    Aborted,
}

pub struct Coordinator {
    participants: HashMap<String, Box<dyn Participant + Send>>,
    transactions: HashMap<String, TransactionState>,
    log_file: String,
}

impl Coordinator {
    pub fn new() -> Self {
        Self {
            participants: HashMap::new(),
            transactions: HashMap::new(),
            log_file: "dtm_log.txt".to_string(),
        }
    }

    pub fn register_participant(&mut self, id: String, p: Box<dyn Participant + Send>) {
        self.participants.insert(id, p);
    }

    pub fn execute_transaction(&mut self, tx_id: String) -> Result<(), String> {
        // Start transaction and mark as Preparing
        self.transactions.insert(tx_id.clone(), TransactionState::Preparing);
        self.append_log(&tx_id, "PREPARING")?;

        let start = Instant::now();

        // Two-Phase Commit: Phase 1: Prepare
        for (_id, participant) in self.participants.iter() {
            if start.elapsed() > Duration::from_secs(60) {
                self.transactions.insert(tx_id.clone(), TransactionState::Aborted);
                self.append_log(&tx_id, "ABORTED")?;
                // Rollback all participants
                for (_rid, p) in self.participants.iter() {
                    let _ = p.rollback();
                }
                return Err("Transaction timed out during prepare".to_string());
            }
            match participant.prepare() {
                Ok(_) => {},
                Err(e) => {
                    self.transactions.insert(tx_id.clone(), TransactionState::Aborted);
                    self.append_log(&tx_id, "ABORTED")?;
                    // Rolling back all participants if any prepare fails.
                    for (_rid, p) in self.participants.iter() {
                        let _ = p.rollback();
                    }
                    return Err(e);
                }
            }
        }

        self.transactions.insert(tx_id.clone(), TransactionState::Prepared);
        self.append_log(&tx_id, "PREPARED")?;

        // Two-Phase Commit: Phase 2: Commit
        for (_id, participant) in self.participants.iter() {
            if start.elapsed() > Duration::from_secs(60) {
                self.transactions.insert(tx_id.clone(), TransactionState::Aborted);
                self.append_log(&tx_id, "ABORTED")?;
                // Rollback due to timeout during commit phase.
                for (_rid, p) in self.participants.iter() {
                    let _ = p.rollback();
                }
                return Err("Transaction timed out during commit".to_string());
            }
            match participant.commit() {
                Ok(_) => {},
                Err(e) => {
                    self.transactions.insert(tx_id.clone(), TransactionState::Aborted);
                    self.append_log(&tx_id, "ABORTED")?;
                    // Rollback in case any commit fails.
                    for (_rid, p) in self.participants.iter() {
                        let _ = p.rollback();
                    }
                    return Err(e);
                }
            }
        }

        self.transactions.insert(tx_id.clone(), TransactionState::Committed);
        self.append_log(&tx_id, "COMMITTED")?;
        Ok(())
    }

    pub fn get_transaction_state(&self, tx_id: &String) -> Option<TransactionState> {
        self.transactions.get(tx_id).cloned()
    }

    // Append a log entry to the log file in the format: "tx_id state\n"
    pub fn append_log(&self, tx_id: &String, state: &str) -> Result<(), String> {
        let mut file = OpenOptions::new()
            .append(true)
            .create(true)
            .open(&self.log_file)
            .map_err(|e| e.to_string())?;
        let log_line = format!("{} {}\n", tx_id, state);
        file.write_all(log_line.as_bytes())
            .map_err(|e| e.to_string())
    }

    // Persist all current transaction states to the log file.
    pub fn persist_state(&self) -> Result<(), String> {
        let mut file = File::create(&self.log_file)
            .map_err(|e| e.to_string())?;
        for (tx, state) in self.transactions.iter() {
            let state_str = match state {
                TransactionState::Preparing => "PREPARING",
                TransactionState::Prepared => "PREPARED",
                TransactionState::Committed => "COMMITTED",
                TransactionState::Aborted => "ABORTED",
            };
            let log_line = format!("{} {}\n", tx, state_str);
            file.write_all(log_line.as_bytes())
                .map_err(|e| e.to_string())?;
        }
        Ok(())
    }

    // Recover coordinator state from the log file.
    pub fn recover_state() -> Result<Self, String> {
        let log_file = "dtm_log.txt".to_string();
        let mut transactions = HashMap::new();
        let mut file = OpenOptions::new()
            .read(true)
            .open(&log_file)
            .map_err(|e| e.to_string())?;
        let mut content = String::new();
        file.read_to_string(&mut content)
            .map_err(|e| e.to_string())?;
        for line in content.lines() {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() == 2 {
                let tx_id = parts[0].to_string();
                let state = match parts[1] {
                    "PREPARING" => TransactionState::Preparing,
                    "PREPARED" => TransactionState::Prepared,
                    "COMMITTED" => TransactionState::Committed,
                    "ABORTED" => TransactionState::Aborted,
                    _ => continue,
                };
                transactions.insert(tx_id, state);
            }
        }
        Ok(Coordinator {
            participants: HashMap::new(),
            transactions,
            log_file,
        })
    }
}