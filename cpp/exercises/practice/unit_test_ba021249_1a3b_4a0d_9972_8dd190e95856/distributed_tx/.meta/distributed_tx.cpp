#include "distributed_tx.h"
#include <iostream>
#include <sstream>
#include <algorithm>

// Transaction implementation
Transaction::Transaction(int txId) : id(txId), status(TransactionStatus::ACTIVE) {}

int Transaction::getId() const {
    return id;
}

TransactionStatus Transaction::getStatus() const {
    std::shared_lock<std::shared_mutex> lock(mutex);
    return status;
}

void Transaction::setStatus(TransactionStatus newStatus) {
    std::unique_lock<std::shared_mutex> lock(mutex);
    status = newStatus;
}

void Transaction::addShard(int shardId) {
    std::unique_lock<std::shared_mutex> lock(mutex);
    if (std::find(involvedShards.begin(), involvedShards.end(), shardId) == involvedShards.end()) {
        involvedShards.push_back(shardId);
    }
}

bool Transaction::containsShard(int shardId) const {
    std::shared_lock<std::shared_mutex> lock(mutex);
    return std::find(involvedShards.begin(), involvedShards.end(), shardId) != involvedShards.end();
}

const std::vector<int>& Transaction::getInvolvedShards() const {
    std::shared_lock<std::shared_mutex> lock(mutex);
    return involvedShards;
}

// Shard implementation
Shard::Shard(int shardId) : id(shardId) {}

bool Shard::update(int txId, const std::string& data) {
    std::unique_lock<std::shared_mutex> lock(mutex);
    pendingUpdates[txId] = data;
    return true;
}

bool Shard::prepare(int txId) {
    std::unique_lock<std::shared_mutex> lock(mutex);
    auto it = pendingUpdates.find(txId);
    if (it != pendingUpdates.end()) {
        preparedUpdates[txId] = it->second;
        pendingUpdates.erase(it);
        return true;
    }
    return false; // No pending updates for this transaction
}

void Shard::commit(int txId) {
    std::unique_lock<std::shared_mutex> lock(mutex);
    auto it = preparedUpdates.find(txId);
    if (it != preparedUpdates.end()) {
        currentData = it->second;
        preparedUpdates.erase(it);
    }
}

void Shard::rollback(int txId) {
    std::unique_lock<std::shared_mutex> lock(mutex);
    pendingUpdates.erase(txId);
    preparedUpdates.erase(txId);
}

std::string Shard::get() const {
    std::shared_lock<std::shared_mutex> lock(mutex);
    return currentData.empty() ? "NULL" : currentData;
}

// Transaction Manager implementation
TransactionManager::TransactionManager(int numShards) {
    shards.reserve(numShards);
    for (int i = 0; i < numShards; ++i) {
        shards.push_back(std::make_unique<Shard>(i));
    }
}

std::string TransactionManager::processCommand(const std::string& command) {
    std::istringstream iss(command);
    std::string operation;
    iss >> operation;

    if (operation == "BEGIN") {
        int txId;
        iss >> txId;
        handleBegin(txId);
        return "";
    } else if (operation == "UPDATE") {
        int txId, shardId;
        iss >> txId >> shardId;
        
        // Extract the rest of the line as the data (preserving spaces)
        std::string data;
        iss >> std::ws; // Skip any leading whitespace
        std::getline(iss, data);
        
        // Remove quotes if present
        if (data.size() >= 2 && data.front() == '"' && data.back() == '"') {
            data = data.substr(1, data.size() - 2);
        }
        
        handleUpdate(txId, shardId, data);
        return "";
    } else if (operation == "PREPARE") {
        int txId;
        iss >> txId;
        handlePrepare(txId);
        return "";
    } else if (operation == "COMMIT") {
        int txId;
        iss >> txId;
        handleCommit(txId);
        return "";
    } else if (operation == "ROLLBACK") {
        int txId;
        iss >> txId;
        handleRollback(txId);
        return "";
    } else if (operation == "GET") {
        int shardId;
        iss >> shardId;
        return handleGet(shardId);
    }
    
    return "ERROR: Unknown command";
}

void TransactionManager::handleBegin(int txId) {
    std::lock_guard<std::mutex> lock(txMutex);
    transactions[txId] = std::make_shared<Transaction>(txId);
}

void TransactionManager::handleUpdate(int txId, int shardId, const std::string& data) {
    if (shardId < 0 || shardId >= static_cast<int>(shards.size())) {
        return; // Invalid shard ID
    }
    
    auto tx = getTransaction(txId);
    if (!tx || tx->getStatus() != TransactionStatus::ACTIVE) {
        return; // Transaction doesn't exist or is not active
    }
    
    tx->addShard(shardId);
    shards[shardId]->update(txId, data);
}

void TransactionManager::handlePrepare(int txId) {
    auto tx = getTransaction(txId);
    if (!tx || tx->getStatus() != TransactionStatus::ACTIVE) {
        return; // Transaction doesn't exist or is not active
    }
    
    tx->setStatus(TransactionStatus::PREPARING);
    
    bool allPrepared = true;
    for (int shardId : tx->getInvolvedShards()) {
        if (!shards[shardId]->prepare(txId)) {
            allPrepared = false;
            break;
        }
    }
    
    if (allPrepared) {
        tx->setStatus(TransactionStatus::PREPARED);
    } else {
        // If any shard fails to prepare, abort the transaction
        tx->setStatus(TransactionStatus::ABORTING);
        for (int shardId : tx->getInvolvedShards()) {
            shards[shardId]->rollback(txId);
        }
        tx->setStatus(TransactionStatus::ABORTED);
    }
}

void TransactionManager::handleCommit(int txId) {
    auto tx = getTransaction(txId);
    if (!tx || tx->getStatus() != TransactionStatus::PREPARED) {
        return; // Transaction doesn't exist or is not prepared
    }
    
    tx->setStatus(TransactionStatus::COMMITTING);
    
    for (int shardId : tx->getInvolvedShards()) {
        shards[shardId]->commit(txId);
    }
    
    tx->setStatus(TransactionStatus::COMMITTED);
}

void TransactionManager::handleRollback(int txId) {
    auto tx = getTransaction(txId);
    if (!tx) {
        return; // Transaction doesn't exist
    }
    
    tx->setStatus(TransactionStatus::ABORTING);
    
    for (int shardId : tx->getInvolvedShards()) {
        shards[shardId]->rollback(txId);
    }
    
    tx->setStatus(TransactionStatus::ABORTED);
}

std::string TransactionManager::handleGet(int shardId) {
    if (shardId < 0 || shardId >= static_cast<int>(shards.size())) {
        return "ERROR: Invalid shard ID";
    }
    
    return shards[shardId]->get();
}

std::shared_ptr<Transaction> TransactionManager::getTransaction(int txId) {
    std::lock_guard<std::mutex> lock(txMutex);
    auto it = transactions.find(txId);
    if (it != transactions.end()) {
        return it->second;
    }
    return nullptr;
}