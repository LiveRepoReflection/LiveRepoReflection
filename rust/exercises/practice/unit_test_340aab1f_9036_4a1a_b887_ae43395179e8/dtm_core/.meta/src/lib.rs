use std::collections::HashMap;
use std::sync::Mutex;

pub type TxId = u64;
pub type ResourceId = String;
pub type ServiceId = String;

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum TransactionStatus {
    Pending,
    Prepared,
    Committed,
    RolledBack,
}

#[derive(Debug)]
struct Transaction {
    id: TxId,
    status: TransactionStatus,
    resources: HashMap<ResourceId, ServiceId>,
}

#[derive(Debug)]
struct Inner {
    transactions: HashMap<TxId, Transaction>,
    next_tx_id: TxId,
}

/// Error type for DistributedTransactionManager operations
#[derive(Debug, PartialEq, Eq)]
pub enum DtmError {
    TransactionNotFound,
    InvalidState(String),
    ResourceAlreadyRegistered,
}

pub struct DistributedTransactionManager {
    inner: Mutex<Inner>,
}

impl DistributedTransactionManager {
    pub fn new() -> Self {
        DistributedTransactionManager {
            inner: Mutex::new(Inner {
                transactions: HashMap::new(),
                next_tx_id: 1,
            }),
        }
    }

    pub fn begin_transaction(&mut self) -> TxId {
        let mut inner = self.inner.lock().unwrap();
        let tx_id = inner.next_tx_id;
        inner.next_tx_id += 1;
        let transaction = Transaction {
            id: tx_id,
            status: TransactionStatus::Pending,
            resources: HashMap::new(),
        };
        inner.transactions.insert(tx_id, transaction);
        tx_id
    }

    pub fn register_resource(&mut self, tx_id: TxId, resource_id: ResourceId, service_id: ServiceId) -> Result<(), DtmError> {
        let mut inner = self.inner.lock().unwrap();
        let transaction = inner.transactions.get_mut(&tx_id).ok_or(DtmError::TransactionNotFound)?;
        if transaction.resources.contains_key(&resource_id) {
            return Err(DtmError::ResourceAlreadyRegistered);
        }
        transaction.resources.insert(resource_id, service_id);
        Ok(())
    }

    pub fn prepare(&mut self, tx_id: TxId) -> Result<(), DtmError> {
        let mut inner = self.inner.lock().unwrap();
        let transaction = inner.transactions.get_mut(&tx_id).ok_or(DtmError::TransactionNotFound)?;
        match transaction.status {
            TransactionStatus::Pending => {
                transaction.status = TransactionStatus::Prepared;
                Ok(())
            },
            _ => Err(DtmError::InvalidState("Transaction is not in Pending state".to_string())),
        }
    }

    pub fn commit(&mut self, tx_id: TxId) -> Result<(), DtmError> {
        let mut inner = self.inner.lock().unwrap();
        let transaction = inner.transactions.get_mut(&tx_id).ok_or(DtmError::TransactionNotFound)?;
        match transaction.status {
            TransactionStatus::Prepared => {
                transaction.status = TransactionStatus::Committed;
                Ok(())
            },
            _ => Err(DtmError::InvalidState("Transaction must be Prepared before commit".to_string())),
        }
    }

    pub fn rollback(&mut self, tx_id: TxId) -> Result<(), DtmError> {
        let mut inner = self.inner.lock().unwrap();
        let transaction = inner.transactions.get_mut(&tx_id).ok_or(DtmError::TransactionNotFound)?;
        match transaction.status {
            TransactionStatus::Pending | TransactionStatus::Prepared => {
                transaction.status = TransactionStatus::RolledBack;
                Ok(())
            },
            _ => Err(DtmError::InvalidState("Transaction cannot be rolled back".to_string())),
        }
    }

    pub fn get_transaction_status(&self, tx_id: TxId) -> Result<TransactionStatus, DtmError> {
        let inner = self.inner.lock().unwrap();
        let transaction = inner.transactions.get(&tx_id).ok_or(DtmError::TransactionNotFound)?;
        Ok(transaction.status.clone())
    }
}