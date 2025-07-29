use std::collections::HashMap;
use std::sync::Mutex;

pub trait Participant {
    fn prepare(&self, tx_id: &str) -> Result<(), ()>;
    fn commit(&self, tx_id: &str) -> Result<(), ()>;
    fn abort(&self, tx_id: &str) -> Result<(), ()>;
}

#[derive(Debug, PartialEq)]
pub enum TransactionError {
    Abort,
}

#[derive(PartialEq)]
enum TransactionStatus {
    Pending,
    Committed,
    Aborted,
}

struct TransactionRecord {
    participants: Vec<Box<dyn Participant + Send>>,
    status: TransactionStatus,
}

pub struct Coordinator {
    transactions: Mutex<HashMap<String, TransactionRecord>>,
    tx_counter: Mutex<u64>,
    timeout_ms: u64,
}

impl Coordinator {
    pub fn new() -> Self {
        Self {
            transactions: Mutex::new(HashMap::new()),
            tx_counter: Mutex::new(0),
            timeout_ms: 150,
        }
    }

    pub fn start_transaction(&mut self, participants: Vec<Box<dyn Participant + Send>>) -> String {
        let mut counter = self.tx_counter.lock().unwrap();
        *counter += 1;
        let tx_id = format!("tx_{}", *counter);
        let record = TransactionRecord {
            participants,
            status: TransactionStatus::Pending,
        };

        let mut tx_map = self.transactions.lock().unwrap();
        tx_map.insert(tx_id.clone(), record);
        tx_id
    }

    pub fn complete_transaction(&mut self, tx_id: &str) -> Result<(), TransactionError> {
        let mut tx_map = self.transactions.lock().unwrap();
        if let Some(record) = tx_map.get_mut(tx_id) {
            if record.status != TransactionStatus::Pending {
                // If already finalized, return corresponding result.
                return match record.status {
                    TransactionStatus::Committed => Ok(()),
                    TransactionStatus::Aborted => Err(TransactionError::Abort),
                    _ => Err(TransactionError::Abort),
                };
            }
            // Phase 1: Prepare
            let mut all_prepared = true;
            for participant in record.participants.iter() {
                // We simulate a timeout by using std::time.
                // Since we cannot control real asynchronous timeout,
                // we assume that the participant's prepare method will return Err if it fails or times out.
                if participant.prepare(tx_id).is_err() {
                    all_prepared = false;
                    break;
                }
            }

            // Phase 2: Commit or Abort
            if all_prepared {
                for participant in record.participants.iter() {
                    let _ = participant.commit(tx_id);
                }
                record.status = TransactionStatus::Committed;
                Ok(())
            } else {
                for participant in record.participants.iter() {
                    let _ = participant.abort(tx_id);
                }
                record.status = TransactionStatus::Aborted;
                Err(TransactionError::Abort)
            }
        } else {
            Err(TransactionError::Abort)
        }
    }

    pub fn recover(&mut self) {
        let mut tx_map = self.transactions.lock().unwrap();
        let tx_ids: Vec<String> = tx_map.keys().cloned().collect();
        for tx_id in tx_ids {
            if let Some(record) = tx_map.get_mut(&tx_id) {
                if record.status == TransactionStatus::Pending {
                    let mut all_prepared = true;
                    for participant in record.participants.iter() {
                        if participant.prepare(&tx_id).is_err() {
                            all_prepared = false;
                            break;
                        }
                    }
                    if all_prepared {
                        for participant in record.participants.iter() {
                            let _ = participant.commit(&tx_id);
                        }
                        record.status = TransactionStatus::Committed;
                    } else {
                        for participant in record.participants.iter() {
                            let _ = participant.abort(&tx_id);
                        }
                        record.status = TransactionStatus::Aborted;
                    }
                }
            }
        }
    }

    pub fn get_transaction_status(&self, tx_id: &str) -> Option<&'static str> {
        let tx_map = self.transactions.lock().unwrap();
        tx_map.get(tx_id).map(|record| match record.status {
            TransactionStatus::Pending => "pending",
            TransactionStatus::Committed => "committed",
            TransactionStatus::Aborted => "aborted",
        })
    }
}