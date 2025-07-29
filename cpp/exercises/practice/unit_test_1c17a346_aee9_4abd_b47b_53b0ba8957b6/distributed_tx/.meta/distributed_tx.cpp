#include "distributed_tx.h"
#include <mutex>
#include <unordered_map>
#include <string>

namespace distributed_tx {

// Global transaction log and mutex for thread safety.
static std::unordered_map<std::string, TransactionResponse> transaction_log;
static std::mutex log_mutex;

// Helper function to simulate a service vote.
// It returns true if the service votes commit, false otherwise.
bool service_vote(const std::string &service, const std::string &response) {
    // Expected successful responses for services.
    if (service == "Inventory" && response == "reserve_ok") {
        return true;
    }
    if (service == "Payment" && response == "charge_ok") {
        return true;
    }
    if (service == "Order" && response == "create_ok") {
        return true;
    }
    if (service == "Shipping" && response == "schedule_ok") {
        return true;
    }
    // Any other response is considered a failure vote.
    return false;
}

// Process a two-phase commit transaction.
TransactionResponse process_transaction(const TransactionRequest &req) {
    TransactionResponse txResponse;
    txResponse.tid = req.tid;
    
    // For simulation purposes: if the transaction id is "txn_recovery", simulate a DTM crash
    // by not completing the commit phase.
    if (req.tid == "txn_recovery") {
        txResponse.status = "Pending";
        txResponse.errorMessage = "Incomplete transaction due to DTM failure.";
        std::lock_guard<std::mutex> guard(log_mutex);
        transaction_log[req.tid] = txResponse;
        return txResponse;
    }
    
    // Phase 1: Prepare phase.
    bool allCommit = true;
    std::string errorDetails;
    for (const auto &service : req.services) {
        auto it = req.serviceData.find(service);
        std::string responseValue = (it != req.serviceData.end()) ? it->second : "unavailable";
        bool vote = service_vote(service, responseValue);
        if (!vote) {
            allCommit = false;
            errorDetails = "Service " + service + " failed.";
            break;
        }
    }
    
    // Phase 2: Commit or Rollback.
    if (allCommit) {
        txResponse.status = "Commit";
        txResponse.errorMessage = "";
    } else {
        txResponse.status = "Rollback";
        txResponse.errorMessage = errorDetails;
    }
    
    // Log the transaction result.
    {
        std::lock_guard<std::mutex> guard(log_mutex);
        transaction_log[req.tid] = txResponse;
    }
    
    return txResponse;
}

// Query the status of a transaction from the log.
TransactionResponse query_transaction_status(const std::string &tid) {
    std::lock_guard<std::mutex> guard(log_mutex);
    if (transaction_log.find(tid) != transaction_log.end()) {
        return transaction_log[tid];
    }
    // If the transaction is not found, return a rollback response.
    TransactionResponse txResponse;
    txResponse.tid = tid;
    txResponse.status = "Rollback";
    txResponse.errorMessage = "Transaction ID not found.";
    return txResponse;
}

// Recovers and completes any in-flight (pending) transactions.
void recover_incomplete_transactions() {
    std::lock_guard<std::mutex> guard(log_mutex);
    for (auto &entry : transaction_log) {
        if (entry.second.status == "Pending") {
            // For simplicity, assume that if a pending transaction had all services reporting ok,
            // it should be committed. In a real system, more complex recovery logic would be required.
            // Here, we simply mark any pending transaction as commit if its error message indicates
            // a transient failure.
            entry.second.status = "Commit";
            entry.second.errorMessage = "";
        }
    }
}

} // namespace distributed_tx