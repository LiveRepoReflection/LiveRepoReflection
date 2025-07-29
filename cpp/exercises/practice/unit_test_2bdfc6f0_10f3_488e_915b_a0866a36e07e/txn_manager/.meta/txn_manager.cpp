#include "txn_manager.h"
#include <iostream>

namespace txn_manager {

DistributedTransactionManager::DistributedTransactionManager() : next_transaction_id(1) {}

int DistributedTransactionManager::begin_transaction() {
    std::lock_guard<std::mutex> lock(transactions_mutex);
    int tid = next_transaction_id++;
    transactions[tid] = std::make_shared<Transaction>(tid);
    return tid;
}

std::shared_ptr<Transaction> DistributedTransactionManager::get_transaction(int tid) {
    std::lock_guard<std::mutex> lock(transactions_mutex);
    auto it = transactions.find(tid);
    if (it == transactions.end()) {
        return nullptr;
    }
    return it->second;
}

bool DistributedTransactionManager::enlist_resource(
    int tid, int resource_id, PrepareFunction prepare_fn,
    CommitFunction commit_fn, RollbackFunction rollback_fn) {
    
    auto transaction = get_transaction(tid);
    if (!transaction) {
        return false;
    }

    std::lock_guard<std::mutex> lock(transaction->transaction_mutex);
    
    // Check for duplicate resource_id
    for (const auto& resource : transaction->resources) {
        if (resource.resource_id == resource_id) {
            return false;
        }
    }

    transaction->resources.emplace_back(resource_id, prepare_fn, commit_fn, rollback_fn);
    return true;
}

bool DistributedTransactionManager::execute_prepare_phase(Transaction& transaction) {
    bool all_prepared = true;
    
    for (const auto& resource : transaction.resources) {
        try {
            if (!resource.prepare_fn()) {
                all_prepared = false;
                break;
            }
        } catch (const std::exception& e) {
            std::cerr << "Exception during prepare phase for resource "
                      << resource.resource_id << ": " << e.what() << std::endl;
            all_prepared = false;
            break;
        }
    }
    
    return all_prepared;
}

bool DistributedTransactionManager::execute_commit_phase(Transaction& transaction) {
    bool all_committed = true;
    
    for (const auto& resource : transaction.resources) {
        try {
            if (!resource.commit_fn()) {
                all_committed = false;
                std::cerr << "Commit failed for resource " << resource.resource_id << std::endl;
            }
        } catch (const std::exception& e) {
            all_committed = false;
            std::cerr << "Exception during commit phase for resource "
                      << resource.resource_id << ": " << e.what() << std::endl;
        }
    }
    
    return all_committed;
}

bool DistributedTransactionManager::execute_rollback_phase(Transaction& transaction) {
    for (const auto& resource : transaction.resources) {
        try {
            resource.rollback_fn();
        } catch (const std::exception& e) {
            std::cerr << "Exception during rollback phase for resource "
                      << resource.resource_id << ": " << e.what() << std::endl;
        }
    }
    return true;
}

bool DistributedTransactionManager::commit_transaction(int tid) {
    auto transaction = get_transaction(tid);
    if (!transaction) {
        return false;
    }

    std::lock_guard<std::mutex> lock(transaction->transaction_mutex);

    // Empty transaction is considered successful
    if (transaction->resources.empty()) {
        return true;
    }

    // Phase 1: Prepare
    bool prepared = execute_prepare_phase(*transaction);
    
    // Phase 2: Commit or Rollback
    if (prepared) {
        bool committed = execute_commit_phase(*transaction);
        if (!committed) {
            execute_rollback_phase(*transaction);
            return false;
        }
        return true;
    } else {
        execute_rollback_phase(*transaction);
        return false;
    }
}

bool DistributedTransactionManager::rollback_transaction(int tid) {
    auto transaction = get_transaction(tid);
    if (!transaction) {
        return false;
    }

    std::lock_guard<std::mutex> lock(transaction->transaction_mutex);
    return execute_rollback_phase(*transaction);
}

}  // namespace txn_manager