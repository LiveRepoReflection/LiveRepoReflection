#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <memory>
#include <vector>
#include <unordered_map>
#include <mutex>
#include <shared_mutex>
#include <condition_variable>
#include <atomic>
#include <thread>
#include <future>
#include <stdexcept>

// Service interface that must be implemented by participating services
class Service {
public:
    virtual bool Prepare() = 0; // Returns true if the service is ready to commit
    virtual void Commit() = 0;  // Commits the changes
    virtual void Rollback() = 0; // Rolls back any changes
    virtual ~Service() {}
};

// The DistributedTransactionManager class to be implemented
class DistributedTransactionManager {
public:
    // Constructor
    DistributedTransactionManager(int timeoutMs = 10000);  // Default 10 second timeout
    
    // Destructor
    virtual ~DistributedTransactionManager();

    // Starts a new transaction and returns a unique transaction ID
    // Returns: A positive integer representing the transaction ID
    virtual int BeginTransaction();
    
    // Enlists a service in a transaction
    // Parameters:
    //   tid: The transaction ID
    //   service: A shared pointer to the service to enlist
    // Returns: true if the service was successfully enlisted, false otherwise
    virtual bool Enlist(int tid, std::shared_ptr<Service> service);
    
    // Prepares all enlisted services for commit
    // Parameters:
    //   tid: The transaction ID
    // Returns: true if all services were successfully prepared, false otherwise
    virtual bool Prepare(int tid);
    
    // Commits the transaction if all services were successfully prepared
    // Parameters:
    //   tid: The transaction ID
    // Returns: true if the transaction was committed, false otherwise
    virtual bool Commit(int tid);
    
    // Rolls back the transaction
    // Parameters:
    //   tid: The transaction ID
    // Returns: true if the transaction was rolled back, false otherwise
    virtual bool Rollback(int tid);

private:
    enum class TransactionState {
        ACTIVE,      // Transaction has been created but not yet prepared
        PREPARING,   // Transaction is in the process of preparing
        PREPARED,    // All services have been successfully prepared
        COMMITTING,  // Transaction is in the process of committing
        COMMITTED,   // Transaction has been successfully committed
        ROLLING_BACK, // Transaction is in the process of rolling back
        ROLLED_BACK, // Transaction has been rolled back
        FAILED       // Transaction has failed
    };

    struct Transaction {
        int id;
        TransactionState state;
        std::vector<std::shared_ptr<Service>> services;
        std::mutex mtx;  // For operations specific to this transaction
        std::condition_variable cv;  // For coordinating concurrent operations on this transaction
    };

    // Internal helper methods
    std::shared_ptr<Transaction> getTransaction(int tid);
    bool executePrepareSafe(std::shared_ptr<Transaction> tx);
    bool executeCommitSafe(std::shared_ptr<Transaction> tx);
    bool executeRollbackSafe(std::shared_ptr<Transaction> tx);

    // Member variables
    std::atomic<int> nextTid_;
    std::unordered_map<int, std::shared_ptr<Transaction>> transactions_;
    std::shared_mutex txMapMutex_;  // Reader-writer lock for transactions_ map
    int timeoutMs_;
};

#endif