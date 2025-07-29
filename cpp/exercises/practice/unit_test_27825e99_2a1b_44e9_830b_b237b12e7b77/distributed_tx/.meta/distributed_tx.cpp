#include "distributed_tx.h"
#include <algorithm>
#include <cassert>
#include <chrono>

DistributedTransactionManager::DistributedTransactionManager(int timeoutMs) 
    : nextTid_(1), timeoutMs_(timeoutMs) {
}

DistributedTransactionManager::~DistributedTransactionManager() {
    // Attempt to clean up any active transactions by rolling them back
    std::unique_lock<std::shared_mutex> lock(txMapMutex_);
    for (auto& pair : transactions_) {
        auto tx = pair.second;
        std::unique_lock<std::mutex> txLock(tx->mtx);
        if (tx->state != TransactionState::COMMITTED && 
            tx->state != TransactionState::ROLLED_BACK) {
            tx->state = TransactionState::ROLLING_BACK;
            txLock.unlock(); // Release lock before potentially slow operation
            
            // No need to be safe here as we're cleaning up and don't care about
            // return value - we want to try to rollback as much as possible
            for (auto& service : tx->services) {
                try {
                    service->Rollback();
                } catch (...) {
                    // Ignore exceptions during cleanup
                }
            }
            
            txLock.lock();
            tx->state = TransactionState::ROLLED_BACK;
            tx->cv.notify_all();
        }
    }
}

int DistributedTransactionManager::BeginTransaction() {
    int tid = nextTid_++;
    
    auto tx = std::make_shared<Transaction>();
    tx->id = tid;
    tx->state = TransactionState::ACTIVE;
    
    // Lock for writing to the map
    std::unique_lock<std::shared_mutex> lock(txMapMutex_);
    transactions_[tid] = tx;
    
    return tid;
}

bool DistributedTransactionManager::Enlist(int tid, std::shared_ptr<Service> service) {
    if (tid <= 0 || !service) {
        return false;
    }
    
    auto tx = getTransaction(tid);
    if (!tx) {
        return false;
    }
    
    std::unique_lock<std::mutex> lock(tx->mtx);
    
    // Check if the transaction is in a valid state for enlisting
    if (tx->state != TransactionState::ACTIVE) {
        return false;
    }
    
    // Check if the service is already enlisted
    auto it = std::find_if(tx->services.begin(), tx->services.end(), 
                          [&service](const std::shared_ptr<Service>& s) {
                              return s.get() == service.get();
                          });
    
    if (it != tx->services.end()) {
        return false;  // Service is already enlisted
    }
    
    tx->services.push_back(service);
    return true;
}

bool DistributedTransactionManager::Prepare(int tid) {
    auto tx = getTransaction(tid);
    if (!tx) {
        return false;
    }
    
    std::unique_lock<std::mutex> lock(tx->mtx);
    
    // Check if the transaction is in a valid state for preparing
    if (tx->state != TransactionState::ACTIVE) {
        return false;
    }
    
    // Change state to PREPARING
    tx->state = TransactionState::PREPARING;
    lock.unlock(); // Release lock before potentially slow operation
    
    bool success = executePrepareSafe(tx);
    
    lock.lock();
    if (success) {
        tx->state = TransactionState::PREPARED;
    } else {
        // If prepare failed, roll back automatically
        tx->state = TransactionState::ROLLING_BACK;
        lock.unlock();
        
        executeRollbackSafe(tx);
        
        lock.lock();
        tx->state = TransactionState::ROLLED_BACK;
    }
    
    tx->cv.notify_all();
    return success;
}

bool DistributedTransactionManager::Commit(int tid) {
    auto tx = getTransaction(tid);
    if (!tx) {
        return false;
    }
    
    std::unique_lock<std::mutex> lock(tx->mtx);
    
    // Check if the transaction is prepared
    if (tx->state != TransactionState::PREPARED) {
        return false;
    }
    
    // Change state to COMMITTING
    tx->state = TransactionState::COMMITTING;
    lock.unlock(); // Release lock before potentially slow operation
    
    bool success = executeCommitSafe(tx);
    
    lock.lock();
    if (success) {
        tx->state = TransactionState::COMMITTED;
    } else {
        // If commit failed (which shouldn't happen in 2PC after successful prepare),
        // mark as failed
        tx->state = TransactionState::FAILED;
    }
    
    tx->cv.notify_all();
    return success;
}

bool DistributedTransactionManager::Rollback(int tid) {
    auto tx = getTransaction(tid);
    if (!tx) {
        return false;
    }
    
    std::unique_lock<std::mutex> lock(tx->mtx);
    
    // Can only rollback if not already committed or rolled back
    if (tx->state == TransactionState::COMMITTED || 
        tx->state == TransactionState::ROLLED_BACK ||
        tx->state == TransactionState::ROLLING_BACK) {
        return false;
    }
    
    // Change state to ROLLING_BACK
    tx->state = TransactionState::ROLLING_BACK;
    lock.unlock(); // Release lock before potentially slow operation
    
    bool success = executeRollbackSafe(tx);
    
    lock.lock();
    if (success) {
        tx->state = TransactionState::ROLLED_BACK;
    } else {
        // If rollback failed, mark as failed
        tx->state = TransactionState::FAILED;
    }
    
    tx->cv.notify_all();
    return success;
}

std::shared_ptr<DistributedTransactionManager::Transaction> DistributedTransactionManager::getTransaction(int tid) {
    // Acquire a read lock
    std::shared_lock<std::shared_mutex> lock(txMapMutex_);
    
    auto it = transactions_.find(tid);
    if (it == transactions_.end()) {
        return nullptr;
    }
    
    return it->second;
}

bool DistributedTransactionManager::executePrepareSafe(std::shared_ptr<Transaction> tx) {
    if (tx->services.empty()) {
        return true;  // No services to prepare, trivially successful
    }
    
    // Create futures for each service's prepare operation
    std::vector<std::future<bool>> futures;
    for (auto& service : tx->services) {
        futures.push_back(std::async(std::launch::async, [&service]() {
            try {
                return service->Prepare();
            } catch (...) {
                return false;  // Any exception is treated as a prepare failure
            }
        }));
    }
    
    // Wait for all services to prepare with timeout
    auto startTime = std::chrono::steady_clock::now();
    bool allPrepared = true;
    
    for (auto& future : futures) {
        if (future.wait_for(std::chrono::milliseconds(timeoutMs_)) == std::future_status::timeout) {
            // Timeout occurred
            allPrepared = false;
            break;
        }
        
        try {
            if (!future.get()) {
                // One service failed to prepare
                allPrepared = false;
                break;
            }
        } catch (...) {
            // Handle any exceptions from future.get()
            allPrepared = false;
            break;
        }
        
        // Check if we've exceeded the overall timeout
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - startTime).count();
        if (elapsed > timeoutMs_) {
            allPrepared = false;
            break;
        }
    }
    
    return allPrepared;
}

bool DistributedTransactionManager::executeCommitSafe(std::shared_ptr<Transaction> tx) {
    // Create futures for each service's commit operation
    std::vector<std::future<void>> futures;
    for (auto& service : tx->services) {
        futures.push_back(std::async(std::launch::async, [&service]() {
            service->Commit();
        }));
    }
    
    // Wait for all services to commit with timeout
    auto startTime = std::chrono::steady_clock::now();
    bool allCommitted = true;
    
    for (auto& future : futures) {
        if (future.wait_for(std::chrono::milliseconds(timeoutMs_)) == std::future_status::timeout) {
            // Timeout occurred
            allCommitted = false;
            break;
        }
        
        try {
            future.get();  // This will rethrow any exception that occurred in the service->Commit() call
        } catch (...) {
            // Handle any exceptions from future.get()
            allCommitted = false;
            break;
        }
        
        // Check if we've exceeded the overall timeout
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - startTime).count();
        if (elapsed > timeoutMs_) {
            allCommitted = false;
            break;
        }
    }
    
    return allCommitted;
}

bool DistributedTransactionManager::executeRollbackSafe(std::shared_ptr<Transaction> tx) {
    // Create futures for each service's rollback operation
    std::vector<std::future<void>> futures;
    for (auto& service : tx->services) {
        futures.push_back(std::async(std::launch::async, [&service]() {
            service->Rollback();
        }));
    }
    
    // Wait for all services to rollback with timeout
    auto startTime = std::chrono::steady_clock::now();
    bool allRolledBack = true;
    
    for (auto& future : futures) {
        if (future.wait_for(std::chrono::milliseconds(timeoutMs_)) == std::future_status::timeout) {
            // Timeout occurred
            allRolledBack = false;
            break;
        }
        
        try {
            future.get();  // This will rethrow any exception that occurred in the service->Rollback() call
        } catch (...) {
            // Handle any exceptions from future.get()
            allRolledBack = false;
            break;
        }
        
        // Check if we've exceeded the overall timeout
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - startTime).count();
        if (elapsed > timeoutMs_) {
            allRolledBack = false;
            break;
        }
    }
    
    return allRolledBack;
}