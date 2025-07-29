#include "distributed_tx.h"
#include <unordered_map>
#include <set>
#include <queue>
#include <algorithm>
#include <limits>

namespace distributed_tx {

// Structure to hold transaction information
struct Transaction {
    int txID;
    int commitWeight;
    std::vector<int> involvedShards;
    std::unordered_map<int, bool> shardVotes;  // Map of shardID to vote
    bool isActive;  // Transaction is still in progress
    bool isDecided; // All shards have voted
    bool isCommitted;  // Transaction has been committed
    bool isRolledBack;  // Transaction has been explicitly rolled back
    
    Transaction(int id, const std::vector<int>& shards, int weight)
        : txID(id), commitWeight(weight), involvedShards(shards),
          isActive(true), isDecided(false), isCommitted(false), isRolledBack(false) {
        // For transactions with empty shard list, mark as decided
        if (involvedShards.empty()) {
            isDecided = true;
        }
    }
};

// Custom comparator for the priority queue
struct TransactionComparator {
    bool operator()(const Transaction* t1, const Transaction* t2) const {
        if (t1->commitWeight != t2->commitWeight) {
            return t1->commitWeight < t2->commitWeight;  // Higher weight has higher priority
        }
        return t1->txID > t2->txID;  // In case of tie, lower txID has higher priority
    }
};

class TransactionCoordinatorImpl {
public:
    explicit TransactionCoordinatorImpl(int n) : numShards(n) {}
    
    void BeginTransaction(int txID, const std::vector<int>& shardIDs, int commitWeight) {
        // If transaction already exists, ignore the duplicate request
        if (transactions.find(txID) != transactions.end()) {
            return;
        }
        
        // Create and store new transaction
        Transaction* tx = new Transaction(txID, shardIDs, commitWeight);
        transactions[txID] = tx;
        
        // Add to undecided transactions if it has involved shards
        if (!shardIDs.empty()) {
            undecidedTransactions.push(tx);
        }
    }
    
    void Prepare(int txID, int shardID, bool vote) {
        // Find the transaction
        auto it = transactions.find(txID);
        if (it == transactions.end()) {
            return;  // Transaction doesn't exist, ignore
        }
        
        Transaction* tx = it->second;
        
        // If the transaction is already committed or rolled back, ignore
        if (!tx->isActive || tx->isCommitted || tx->isRolledBack) {
            return;
        }
        
        // Check if the shard is involved in this transaction
        if (std::find(tx->involvedShards.begin(), tx->involvedShards.end(), shardID) 
            == tx->involvedShards.end()) {
            return;  // Shard not involved, ignore
        }
        
        // Check if the shard has already voted
        if (tx->shardVotes.find(shardID) != tx->shardVotes.end()) {
            return;  // Already voted, ignore
        }
        
        // Record the vote
        tx->shardVotes[shardID] = vote;
        
        // Check if all shards have voted
        if (tx->shardVotes.size() == tx->involvedShards.size()) {
            tx->isDecided = true;
            
            // Rebuild the undecided transactions priority queue without this transaction
            std::priority_queue<Transaction*, std::vector<Transaction*>, TransactionComparator> tempQueue;
            while (!undecidedTransactions.empty()) {
                Transaction* t = undecidedTransactions.top();
                undecidedTransactions.pop();
                if (t->txID != txID && !t->isDecided && !t->isCommitted && !t->isRolledBack) {
                    tempQueue.push(t);
                }
            }
            undecidedTransactions = std::move(tempQueue);
        }
    }
    
    bool CommitTransaction(int txID) {
        // Find the transaction
        auto it = transactions.find(txID);
        if (it == transactions.end()) {
            return false;  // Transaction doesn't exist
        }
        
        Transaction* tx = it->second;
        
        // If the transaction is already committed or rolled back, return appropriate status
        if (tx->isCommitted) {
            return false;  // Already committed
        }
        if (tx->isRolledBack) {
            return false;  // Already rolled back
        }
        
        // For empty shard lists, commit automatically
        if (tx->involvedShards.empty()) {
            tx->isCommitted = true;
            tx->isActive = false;
            return true;
        }
        
        // Check if all shards have voted
        if (tx->shardVotes.size() != tx->involvedShards.size()) {
            return false;  // Not all shards have voted
        }
        
        // Check if any shard voted to abort
        for (const auto& vote : tx->shardVotes) {
            if (!vote.second) {
                tx->isActive = false;
                return false;  // Abort due to negative vote
            }
        }
        
        // All shards voted to commit
        tx->isCommitted = true;
        tx->isActive = false;
        return true;
    }
    
    bool RollbackTransaction(int txID) {
        // Find the transaction
        auto it = transactions.find(txID);
        if (it == transactions.end()) {
            return false;  // Transaction doesn't exist
        }
        
        Transaction* tx = it->second;
        
        // If the transaction is already committed or rolled back, return appropriate status
        if (tx->isCommitted) {
            return false;  // Already committed
        }
        if (tx->isRolledBack) {
            return false;  // Already rolled back
        }
        
        // Mark as rolled back
        tx->isRolledBack = true;
        tx->isActive = false;
        
        // Remove from undecided transactions
        if (!tx->isDecided) {
            std::priority_queue<Transaction*, std::vector<Transaction*>, TransactionComparator> tempQueue;
            while (!undecidedTransactions.empty()) {
                Transaction* t = undecidedTransactions.top();
                undecidedTransactions.pop();
                if (t->txID != txID && !t->isDecided && !t->isCommitted && !t->isRolledBack) {
                    tempQueue.push(t);
                }
            }
            undecidedTransactions = std::move(tempQueue);
        }
        
        return true;
    }
    
    int GetHeaviestUndecidedTransaction() {
        // Clean up the priority queue
        while (!undecidedTransactions.empty() && 
              (undecidedTransactions.top()->isDecided || 
               undecidedTransactions.top()->isCommitted || 
               undecidedTransactions.top()->isRolledBack)) {
            undecidedTransactions.pop();
        }
        
        if (undecidedTransactions.empty()) {
            return -1;  // No undecided transactions
        }
        
        return undecidedTransactions.top()->txID;
    }
    
    ~TransactionCoordinatorImpl() {
        // Clean up allocated memory
        for (auto& pair : transactions) {
            delete pair.second;
        }
    }
    
private:
    int numShards;
    std::unordered_map<int, Transaction*> transactions;
    std::priority_queue<Transaction*, std::vector<Transaction*>, TransactionComparator> undecidedTransactions;
};

// Implementation of the public interface
TransactionCoordinator::TransactionCoordinator(int n) 
    : pImpl(new TransactionCoordinatorImpl(n)) {}

void TransactionCoordinator::BeginTransaction(int txID, const std::vector<int>& shardIDs, int commitWeight) {
    pImpl->BeginTransaction(txID, shardIDs, commitWeight);
}

void TransactionCoordinator::Prepare(int txID, int shardID, bool vote) {
    pImpl->Prepare(txID, shardID, vote);
}

bool TransactionCoordinator::CommitTransaction(int txID) {
    return pImpl->CommitTransaction(txID);
}

bool TransactionCoordinator::RollbackTransaction(int txID) {
    return pImpl->RollbackTransaction(txID);
}

int TransactionCoordinator::GetHeaviestUndecidedTransaction() {
    return pImpl->GetHeaviestUndecidedTransaction();
}

TransactionCoordinator::~TransactionCoordinator() {
    delete pImpl;
}

}  // namespace distributed_tx