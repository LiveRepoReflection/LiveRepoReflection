#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <vector>
#include <string>

namespace distributed_tx {

class TransactionCoordinator {
public:
    // Constructor that initializes the coordinator with the number of shards in the system
    TransactionCoordinator(int n);
    
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
};

}  // namespace distributed_tx

#endif  // DISTRIBUTED_TX_H