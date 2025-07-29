#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <shared_mutex>
#include <atomic>
#include <condition_variable>
#include <sstream>

// Forward declarations
class Shard;
class Transaction;

// Transaction status enum
enum class TransactionStatus {
    ACTIVE,
    PREPARING,
    PREPARED,
    COMMITTING,
    COMMITTED,
    ABORTING,
    ABORTED
};

// Class representing a transaction in the system
class Transaction {
public:
    explicit Transaction(int txId);
    
    int getId() const;
    TransactionStatus getStatus() const;
    void setStatus(TransactionStatus status);
    void addShard(int shardId);
    bool containsShard(int shardId) const;
    const std::vector<int>& getInvolvedShards() const;
    
private:
    int id;
    TransactionStatus status;
    std::vector<int> involvedShards;
    mutable std::shared_mutex mutex;
};

// Class representing a data shard
class Shard {
public:
    explicit Shard(int id);
    
    // Process operations on this shard
    bool update(int txId, const std::string& data);
    bool prepare(int txId);
    void commit(int txId);
    void rollback(int txId);
    std::string get() const;
    
private:
    int id;
    std::string currentData;
    std::unordered_map<int, std::string> pendingUpdates;
    std::unordered_map<int, std::string> preparedUpdates;
    mutable std::shared_mutex mutex;
};

// Main transaction manager class
class TransactionManager {
public:
    explicit TransactionManager(int numShards);
    
    // Process a command from the input and return result for GET commands
    std::string processCommand(const std::string& command);
    
private:
    // Command handlers
    void handleBegin(int txId);
    void handleUpdate(int txId, int shardId, const std::string& data);
    void handlePrepare(int txId);
    void handleCommit(int txId);
    void handleRollback(int txId);
    std::string handleGet(int shardId);
    
    // Get transaction by ID, creating if needed
    std::shared_ptr<Transaction> getTransaction(int txId);
    
    // Data members
    std::vector<std::unique_ptr<Shard>> shards;
    std::unordered_map<int, std::shared_ptr<Transaction>> transactions;
    std::mutex txMutex;
};