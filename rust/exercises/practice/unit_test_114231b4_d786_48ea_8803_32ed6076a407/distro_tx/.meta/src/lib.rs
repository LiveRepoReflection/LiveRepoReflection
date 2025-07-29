use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::sync::mpsc;
use std::time::{Duration, Instant};

pub trait Resource: Send {
    fn prepare(&self) -> Result<(), String>;
    fn commit(&self) -> Result<(), String>;
    fn rollback(&self) -> Result<(), String>;
}

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum TransactionStatus {
    Pending,
    Prepared,
    Committed,
    Aborted,
}

struct TransactionRecord {
    pub status: TransactionStatus,
    pub resources: Vec<Box<dyn Resource>>,
}

pub struct TransactionManager {
    transactions: HashMap<u64, TransactionRecord>,
    next_tx_id: u64,
    timeout: Duration,
}

impl TransactionManager {
    pub fn new() -> Self {
        TransactionManager {
            transactions: HashMap::new(),
            next_tx_id: 1,
            timeout: Duration::from_secs(1),
        }
    }

    pub fn set_timeout(&mut self, duration: Duration) {
        self.timeout = duration;
    }

    pub fn initiate_transaction(&mut self) -> u64 {
        let txid = self.next_tx_id;
        self.next_tx_id += 1;
        self.transactions.insert(
            txid,
            TransactionRecord {
                status: TransactionStatus::Pending,
                resources: Vec::new(),
            },
        );
        txid
    }

    pub fn register_resource(&mut self, txid: u64, resource: Box<dyn Resource>) -> Result<(), String> {
        if let Some(tx) = self.transactions.get_mut(&txid) {
            tx.resources.push(resource);
            Ok(())
        } else {
            Err(format!("Transaction {} not found", txid))
        }
    }

    pub fn get_status(&self, txid: u64) -> TransactionStatus {
        if let Some(tx) = self.transactions.get(&txid) {
            tx.status
        } else {
            TransactionStatus::Aborted
        }
    }

    pub fn prepare(&mut self, txid: u64) -> Result<(), String> {
        if let Some(tx) = self.transactions.get_mut(&txid) {
            if tx.status == TransactionStatus::Prepared || tx.status == TransactionStatus::Committed {
                return Ok(());
            }
            // For each resource, run prepare sequentially with timeout simulation.
            for (index, resource) in tx.resources.iter().enumerate() {
                let start = Instant::now();
                let res = resource.prepare();
                let elapsed = start.elapsed();
                if elapsed > self.timeout {
                    tx.status = TransactionStatus::Aborted;
                    return Err(format!(
                        "Timeout while preparing resource at index {}",
                        index
                    ));
                }
                if let Err(err) = res {
                    tx.status = TransactionStatus::Aborted;
                    return Err(format!(
                        "Resource at index {} failed during prepare: {}",
                        index, err
                    ));
                }
            }
            tx.status = TransactionStatus::Prepared;
            Ok(())
        } else {
            Err(format!("Transaction {} not found", txid))
        }
    }

    pub fn commit(&mut self, txid: u64) -> Result<(), String> {
        if let Some(tx) = self.transactions.get_mut(&txid) {
            if tx.status == TransactionStatus::Committed {
                return Ok(());
            }
            if tx.status != TransactionStatus::Prepared {
                return Err("Cannot commit: Transaction not prepared".to_string());
            }
            for (index, resource) in tx.resources.iter().enumerate() {
                let res = resource.commit();
                if let Err(err) = res {
                    return Err(format!(
                        "Resource commit failed at index {}: {}",
                        index, err
                    ));
                }
            }
            tx.status = TransactionStatus::Committed;
            Ok(())
        } else {
            Err(format!("Transaction {} not found", txid))
        }
    }

    pub fn rollback(&mut self, txid: u64) -> Result<(), String> {
        if let Some(tx) = self.transactions.get_mut(&txid) {
            if tx.status == TransactionStatus::Aborted {
                return Ok(());
            }
            for (index, resource) in tx.resources.iter().enumerate() {
                let res = resource.rollback();
                if let Err(err) = res {
                    return Err(format!(
                        "Resource rollback failed at index {}: {}",
                        index, err
                    ));
                }
            }
            tx.status = TransactionStatus::Aborted;
            Ok(())
        } else {
            Err(format!("Transaction {} not found", txid))
        }
    }

    pub fn persist(&self) -> Result<(), String> {
        let mut file = File::create("transaction_manager_state.dat")
            .map_err(|e| format!("Failed to create state file: {}", e))?;
        // Write timeout in milliseconds.
        writeln!(file, "timeout:{}", self.timeout.as_millis())
            .map_err(|e| format!("Failed to write timeout: {}", e))?;
        for (txid, record) in &self.transactions {
            let status_num = match record.status {
                TransactionStatus::Pending => 0,
                TransactionStatus::Prepared => 1,
                TransactionStatus::Committed => 2,
                TransactionStatus::Aborted => 3,
            };
            writeln!(file, "{}:{}", txid, status_num)
                .map_err(|e| format!("Failed to write transaction {}: {}", txid, e))?;
        }
        Ok(())
    }

    pub fn recover(&mut self) -> Result<(), String> {
        let file = File::open("transaction_manager_state.dat")
            .map_err(|e| format!("Failed to open state file: {}", e))?;
        let reader = BufReader::new(file);
        let mut transactions: HashMap<u64, TransactionRecord> = HashMap::new();
        for line in reader.lines() {
            let line = line.map_err(|e| format!("Error reading state file: {}", e))?;
            if line.starts_with("timeout:") {
                let parts: Vec<&str> = line.split(':').collect();
                if parts.len() == 2 {
                    if let Ok(ms) = parts[1].parse::<u64>() {
                        self.timeout = Duration::from_millis(ms);
                    }
                }
            } else {
                let parts: Vec<&str> = line.split(':').collect();
                if parts.len() == 2 {
                    let txid = parts[0]
                        .parse::<u64>()
                        .map_err(|e| format!("Invalid txid: {}", e))?;
                    let status_num = parts[1]
                        .parse::<u8>()
                        .map_err(|e| format!("Invalid status: {}", e))?;
                    let status = match status_num {
                        0 => TransactionStatus::Pending,
                        1 => TransactionStatus::Prepared,
                        2 => TransactionStatus::Committed,
                        3 => TransactionStatus::Aborted,
                        _ => TransactionStatus::Aborted,
                    };
                    transactions.insert(
                        txid,
                        TransactionRecord {
                            status,
                            resources: Vec::new(),
                        },
                    );
                    if txid >= self.next_tx_id {
                        self.next_tx_id = txid + 1;
                    }
                }
            }
        }
        self.transactions = transactions;
        Ok(())
    }
}