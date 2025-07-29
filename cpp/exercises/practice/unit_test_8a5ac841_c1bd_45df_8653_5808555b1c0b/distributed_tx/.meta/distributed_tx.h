#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <vector>
#include <memory>

namespace distributed_tx {

// Forward declaration of implementation class
class TransactionCoordinatorImpl;

class TransactionCoordinator {
public:
    // Constructor that initializes the coordinator with the number of shards in the system
    explicit TransactionCoordinator(int n);
    
    // Destructor to clean up resources
    ~TransactionCoordinator();
    
    // Prevent copying and assignment
    TransactionCoordinator(const TransactionCoordinator&) = delete;
    TransactionCoordinator& operator=(const TransactionCoordinator&) = delete;
    
    // Registers a new transaction
    void BeginTransaction(int txID, const std::vector<int>& shardIDs, int commitWeight);
    
    // Processes a prepare vote from a shard
    void Prepare(int txID, int shardID, bool vote);
    
    // Attempts to commit a transaction
    // Returns true if the transaction was successfully committed, false otherwise
    bool CommitTransaction(int txID);
    
    // Forces a transaction to rollback
    // Returns true if the transaction was successfully rolled back, false otherwise
    bool RollbackTransaction(int txID);
    
    // Returns the txID of the undecided transaction with the highest commitWeight
    // Returns -1 if no undecided transactions exist
    int GetHeaviestUndecidedTransaction();
    
private:
    TransactionCoordinatorImpl* pImpl;  // Pointer to implementation (Pimpl pattern)
};

}  // namespace distributed_tx

#endif  // DISTRIBUTED_TX_H