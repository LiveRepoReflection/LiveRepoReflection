#include "distributed_tx.h"
#include <mutex>
#include <unordered_map>
#include <vector>
#include <atomic>
#include <exception>

namespace distributed_tx {

struct Operation {
    std::function<bool()> commit;
    std::function<void()> rollback;
};

struct Transaction {
    // Stores operations in order of registration
    std::vector<Operation> ops;
};

std::atomic<TransactionID> globalTxID{0};
std::mutex globalMutex;
// Mapping from TransactionID to Transaction data.
std::unordered_map<TransactionID, Transaction> txMap;

TransactionID beginTransaction() {
    TransactionID newTxID = ++globalTxID;
    std::lock_guard<std::mutex> lock(globalMutex);
    txMap[newTxID] = Transaction{};
    return newTxID;
}

bool registerOperation(TransactionID txID, std::function<bool()> commit, std::function<void()> rollback) {
    if (!commit || !rollback) {
        return false;
    }
    std::lock_guard<std::mutex> lock(globalMutex);
    auto it = txMap.find(txID);
    if (it == txMap.end()) {
        return false;
    }
    Operation op;
    op.commit = commit;
    op.rollback = rollback;
    it->second.ops.push_back(op);
    return true;
}

bool commitTransaction(TransactionID txID) {
    // Remove transaction from map first to prevent further modifications.
    Transaction txn;
    {
        std::lock_guard<std::mutex> lock(globalMutex);
        auto it = txMap.find(txID);
        if (it == txMap.end()) {
            return false;
        }
        txn = std::move(it->second);
        txMap.erase(it);
    }
    // Vector to track indices of successfully executed commit operations.
    std::vector<size_t> successfulCommits;
    for (size_t i = 0; i < txn.ops.size(); ++i) {
        bool commitResult = false;
        try {
            commitResult = txn.ops[i].commit();
        } catch (...) {
            commitResult = false;
        }
        if (!commitResult) {
            // Rollback previously committed operations in reverse order.
            for (int j = static_cast<int>(successfulCommits.size()) - 1; j >= 0; --j) {
                try {
                    txn.ops[successfulCommits[j]].rollback();
                } catch (...) {
                    // Swallow exceptions during rollback.
                }
            }
            return false;
        }
        successfulCommits.push_back(i);
    }
    return true;
}

void abortTransaction(TransactionID txID) {
    Transaction txn;
    {
        std::lock_guard<std::mutex> lock(globalMutex);
        auto it = txMap.find(txID);
        if (it == txMap.end()) {
            return;
        }
        txn = std::move(it->second);
        txMap.erase(it);
    }
    // Rollback all operations in reverse order.
    for (int i = static_cast<int>(txn.ops.size()) - 1; i >= 0; --i) {
        try {
            txn.ops[i].rollback();
        } catch (...) {
            // Swallow exceptions during rollback.
        }
    }
}

}  // namespace distributed_tx