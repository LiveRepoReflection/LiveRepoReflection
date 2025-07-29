#include "dtm_banking.h"

#include <unordered_map>
#include <mutex>
#include <thread>
#include <chrono>
#include <vector>

// Global mutex to protect shared resources.
static std::mutex g_mutex;

// Simulated bank data: each server has a map of account_id to balance.
static std::unordered_map<std::string, std::unordered_map<std::string, int>> bankData = {
    { "server1", { {"accountA", 100} } },
    { "server2", { {"accountB", 100} } }
};

// Structure to represent a pending transaction record.
// It holds the original operations and the computed tentative changes for each account.
struct TransactionRecord {
    std::vector<dtm_banking::Operation> ops;
    // Map: server_id -> ( account_id -> delta )
    std::unordered_map<std::string, std::unordered_map<std::string, int>> tentativeChanges;
    bool finalized;
    std::string outcome; // "committed", "aborted", or "error"
    TransactionRecord(const std::vector<dtm_banking::Operation>& o)
        : ops(o), finalized(false), outcome("") {}
};

// Global list of pending transactions (allocated on heap).
static std::vector<TransactionRecord*> pendingTransactions;

// Finalizes a transaction record: if outcome is empty, commits it.
static void finalizeTransaction(TransactionRecord* record) {
    if (!record->finalized) {
        if(record->outcome.empty()) {
            // Commit: apply tentative changes to bankData.
            for (const auto& serverPair : record->tentativeChanges) {
                const std::string& server_id = serverPair.first;
                for (const auto& acctPair : serverPair.second) {
                    const std::string& account_id = acctPair.first;
                    int delta = acctPair.second;
                    bankData[server_id][account_id] += delta;
                }
            }
            record->outcome = "committed";
        }
        record->finalized = true;
    }
}

// Removes finalized transactions from pendingTransactions and deletes them.
static void cleanupPending() {
    auto it = pendingTransactions.begin();
    while (it != pendingTransactions.end()) {
        if ((*it)->finalized) {
            delete *it;
            it = pendingTransactions.erase(it);
        } else {
            ++it;
        }
    }
}

namespace dtm_banking {

std::string processTransaction(const std::vector<Operation>& ops) {
    TransactionRecord* record = new TransactionRecord(ops);

    {
        std::lock_guard<std::mutex> lock(g_mutex);
        // Validate each operation and build the tentativeChanges.
        for (const auto& op : ops) {
            // Check for valid server.
            if (bankData.find(op.server_id) == bankData.end()) {
                record->outcome = "error";
                record->finalized = true;
                return record->outcome;
            }
            // Check for valid account.
            if (bankData[op.server_id].find(op.account_id) == bankData[op.server_id].end()) {
                record->outcome = "error";
                record->finalized = true;
                return record->outcome;
            }
            // Initialize tentative change for this account if not already.
            int currentTentative = record->tentativeChanges[op.server_id][op.account_id];
            
            // Process operation.
            if (op.operation == "withdraw") {
                int newTentative = currentTentative - op.amount;
                // Check if the account would go negative.
                int currentBalance = bankData[op.server_id][op.account_id];
                if (currentBalance + newTentative < 0) {
                    record->outcome = "aborted";
                    record->finalized = true;
                    return record->outcome;
                }
                record->tentativeChanges[op.server_id][op.account_id] = newTentative;
            } else if (op.operation == "deposit") {
                record->tentativeChanges[op.server_id][op.account_id] = currentTentative + op.amount;
            } else {
                record->outcome = "error";
                record->finalized = true;
                return record->outcome;
            }
        }
        // At this point, prepare phase is successful.
        // Add record to pendingTransactions for potential crash recovery.
        pendingTransactions.push_back(record);
    }

    // Simulate processing delay to allow for potential crash recovery.
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    {
        std::lock_guard<std::mutex> lock(g_mutex);
        // Finalize the transaction if not already finalized by recovery.
        if (!record->finalized) {
            finalizeTransaction(record);
        }
        cleanupPending();
    }
    return record->outcome;
}

void recoverTransactions() {
    std::lock_guard<std::mutex> lock(g_mutex);
    for (auto& record : pendingTransactions) {
        if (!record->finalized) {
            finalizeTransaction(record);
        }
    }
    cleanupPending();
}

} // namespace dtm_banking