#include "txn_manager.h"
#include <algorithm>

TxnManager::TxnManager(int n) : num_nodes(n) {
    for (int i = 0; i < n; ++i) {
        nodes.push_back(std::make_unique<NodeData>());
    }
}

bool TxnManager::begin(int tid) {
    std::lock_guard<std::mutex> lock(txn_mutex);
    if (transactions.find(tid) != transactions.end()) {
        return false;
    }
    transactions[tid] = std::make_unique<Transaction>();
    transactions[tid]->active = true;
    return true;
}

bool TxnManager::write(int tid, int node, const std::string& key, int value) {
    if (node < 0 || node >= num_nodes) {
        return false;
    }

    std::lock_guard<std::mutex> lock(txn_mutex);
    auto it = transactions.find(tid);
    if (it == transactions.end() || !it->second->active) {
        return false;
    }

    std::lock_guard<std::mutex> txn_lock(it->second->mutex);
    it->second->writes[node][key] = value;
    return true;
}

int TxnManager::read(int tid, int node, const std::string& key) {
    if (node < 0 || node >= num_nodes) {
        return -1;
    }

    std::lock_guard<std::mutex> lock(txn_mutex);
    auto it = transactions.find(tid);
    if (it == transactions.end() || !it->second->active) {
        return -1;
    }

    std::lock_guard<std::mutex> txn_lock(it->second->mutex);
    
    // First check if the value exists in the transaction's write set
    auto& writes = it->second->writes;
    auto write_it = writes.find(node);
    if (write_it != writes.end()) {
        auto key_it = write_it->second.find(key);
        if (key_it != write_it->second.end()) {
            return key_it->second;
        }
    }

    // If not in write set, read from the node
    std::shared_lock<std::shared_mutex> node_lock(nodes[node]->mutex);
    auto& node_data = nodes[node]->data;
    auto node_it = node_data.find(key);
    if (node_it == node_data.end()) {
        return -1;
    }

    it->second->reads.insert({node, key});
    return node_it->second;
}

bool TxnManager::validateTransaction(Transaction* txn) {
    for (const auto& read : txn->reads) {
        int node = read.first;
        const std::string& key = read.second;

        std::shared_lock<std::shared_mutex> node_lock(nodes[node]->mutex);
        auto& node_data = nodes[node]->data;
        
        // Check if the key exists and has the same value
        auto write_it = txn->writes.find(node);
        if (write_it != txn->writes.end()) {
            auto key_it = write_it->second.find(key);
            if (key_it != write_it->second.end()) {
                continue;  // Skip validation for keys we've written to
            }
        }

        auto node_it = node_data.find(key);
        if (node_it == node_data.end()) {
            return false;  // Key was deleted
        }
    }
    return true;
}

bool TxnManager::commit(int tid) {
    std::lock_guard<std::mutex> lock(txn_mutex);
    auto it = transactions.find(tid);
    if (it == transactions.end() || !it->second->active) {
        return false;
    }

    std::lock_guard<std::mutex> txn_lock(it->second->mutex);
    
    // Validate the transaction
    if (!validateTransaction(it->second.get())) {
        cleanupTransaction(tid);
        return false;
    }

    // Phase 1: Lock all affected nodes
    std::vector<std::unique_lock<std::shared_mutex>> node_locks;
    for (const auto& write : it->second->writes) {
        node_locks.emplace_back(nodes[write.first]->mutex);
    }

    // Phase 2: Apply all writes
    for (const auto& write : it->second->writes) {
        int node = write.first;
        for (const auto& kv : write.second) {
            nodes[node]->data[kv.first] = kv.second;
        }
    }

    cleanupTransaction(tid);
    return true;
}

bool TxnManager::rollback(int tid) {
    std::lock_guard<std::mutex> lock(txn_mutex);
    auto it = transactions.find(tid);
    if (it == transactions.end() || !it->second->active) {
        return false;
    }

    cleanupTransaction(tid);
    return true;
}

void TxnManager::cleanupTransaction(int tid) {
    auto it = transactions.find(tid);
    if (it != transactions.end()) {
        it->second->active = false;
        it->second->writes.clear();
        it->second->reads.clear();
        transactions.erase(it);
    }
}