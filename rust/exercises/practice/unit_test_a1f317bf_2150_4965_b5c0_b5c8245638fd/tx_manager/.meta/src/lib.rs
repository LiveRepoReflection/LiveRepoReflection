use std::collections::HashMap;
use std::sync::{Arc, Mutex, RwLock};
use std::sync::atomic::{AtomicU64, Ordering};

pub trait ResourceManager: Send + Sync {
    fn prepare(&self) -> bool;
    fn commit(&self) -> Result<(), String>;
    fn rollback(&self) -> Result<(), String>;
    fn get_resource_id(&self) -> u64;
}

#[derive(Debug, PartialEq, Clone)]
pub enum TransactionStatus {
    Active,
    Prepared,
    Committed,
    Aborted,
    NotFound,
}

struct Transaction {
    status: TransactionStatus,
    resources: Vec<Arc<dyn ResourceManager>>,
}

pub struct TransactionManager {
    transactions: RwLock<HashMap<u64, Mutex<Transaction>>>,
    next_tid: AtomicU64,
}

impl TransactionManager {
    pub fn new() -> Self {
        TransactionManager {
            transactions: RwLock::new(HashMap::new()),
            next_tid: AtomicU64::new(1),
        }
    }

    pub fn begin_transaction(&self) -> Result<u64, String> {
        let tid = self.next_tid.fetch_add(1, Ordering::SeqCst);
        let transaction = Transaction {
            status: TransactionStatus::Active,
            resources: Vec::new(),
        };

        self.transactions
            .write()
            .unwrap()
            .insert(tid, Mutex::new(transaction));

        Ok(tid)
    }

    pub fn enlist_resource(&self, tid: u64, resource: Arc<dyn ResourceManager>) -> Result<(), String> {
        let transactions = self.transactions.read().unwrap();
        let transaction = transactions
            .get(&tid)
            .ok_or_else(|| "Transaction not found".to_string())?;
        
        let mut transaction = transaction.lock().unwrap();
        
        // Check if resource is already enlisted
        if transaction.resources.iter().any(|r| r.get_resource_id() == resource.get_resource_id()) {
            return Err("Resource already enlisted in this transaction".to_string());
        }

        transaction.resources.push(resource);
        Ok(())
    }

    pub fn prepare_transaction(&self, tid: u64) -> Result<bool, String> {
        let transactions = self.transactions.read().unwrap();
        let transaction = transactions
            .get(&tid)
            .ok_or_else(|| "Transaction not found".to_string())?;
        
        let mut transaction = transaction.lock().unwrap();
        
        if transaction.status != TransactionStatus::Active {
            return Err("Transaction is not in Active state".to_string());
        }

        // Prepare all resources concurrently
        let handles: Vec<_> = transaction
            .resources
            .iter()
            .map(|resource| {
                let resource = resource.clone();
                std::thread::spawn(move || resource.prepare())
            })
            .collect();

        // Wait for all preparations to complete
        let results: Vec<_> = handles
            .into_iter()
            .map(|handle| handle.join().unwrap())
            .collect();

        let all_prepared = results.into_iter().all(|result| result);

        if all_prepared {
            transaction.status = TransactionStatus::Prepared;
        }

        Ok(all_prepared)
    }

    pub fn commit_transaction(&self, tid: u64) -> Result<bool, String> {
        let transactions = self.transactions.read().unwrap();
        let transaction = transactions
            .get(&tid)
            .ok_or_else(|| "Transaction not found".to_string())?;
        
        let mut transaction = transaction.lock().unwrap();

        if transaction.status != TransactionStatus::Prepared {
            return Err("Transaction is not in Prepared state".to_string());
        }

        // Commit all resources concurrently
        let handles: Vec<_> = transaction
            .resources
            .iter()
            .map(|resource| {
                let resource = resource.clone();
                std::thread::spawn(move || resource.commit())
            })
            .collect();

        // Wait for all commits to complete and collect results
        let results: Vec<_> = handles
            .into_iter()
            .map(|handle| handle.join().unwrap())
            .collect();

        let all_committed = results.iter().all(|result| result.is_ok());
        
        transaction.status = TransactionStatus::Committed;
        
        Ok(all_committed)
    }

    pub fn abort_transaction(&self, tid: u64) -> Result<bool, String> {
        let transactions = self.transactions.read().unwrap();
        let transaction = transactions
            .get(&tid)
            .ok_or_else(|| "Transaction not found".to_string())?;
        
        let mut transaction = transaction.lock().unwrap();

        // Rollback all resources concurrently
        let handles: Vec<_> = transaction
            .resources
            .iter()
            .map(|resource| {
                let resource = resource.clone();
                std::thread::spawn(move || resource.rollback())
            })
            .collect();

        // Wait for all rollbacks to complete and collect results
        let results: Vec<_> = handles
            .into_iter()
            .map(|handle| handle.join().unwrap())
            .collect();

        let all_rolled_back = results.iter().all(|result| result.is_ok());
        
        transaction.status = TransactionStatus::Aborted;
        
        Ok(all_rolled_back)
    }

    pub fn get_transaction_status(&self, tid: u64) -> TransactionStatus {
        let transactions = self.transactions.read().unwrap();
        match transactions.get(&tid) {
            Some(transaction) => transaction.lock().unwrap().status.clone(),
            None => TransactionStatus::NotFound,
        }
    }
}

impl Default for TransactionManager {
    fn default() -> Self {
        Self::new()
    }
}