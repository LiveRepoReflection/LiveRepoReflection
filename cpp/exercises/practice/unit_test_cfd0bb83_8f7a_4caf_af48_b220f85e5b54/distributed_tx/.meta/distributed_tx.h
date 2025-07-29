#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <string>
#include <unordered_map>
#include <unordered_set>
#include <set>
#include <mutex>
#include <thread>
#include <chrono>
#include <stdexcept>

namespace distributed_tx {

class Coordinator {
public:
    Coordinator();
    ~Coordinator();

    // Initiates a new transaction and returns a unique transaction ID.
    std::string BeginTransaction();

    // Registers a participant for a transaction.
    // Throws std::invalid_argument if the transaction does not exist or participant already registered.
    void RegisterParticipant(const std::string& transaction_id, const std::string& service_id, const std::string& rollback_endpoint);

    // Reports a vote from a participant.
    // voteCommit=true means vote to commit, false means vote to abort.
    // Throws std::invalid_argument if the transaction does not exist or participant is not registered.
    void ReportVote(const std::string& transaction_id, const std::string& service_id, bool voteCommit);

    // Returns the current status of the transaction: "pending", "committed", or "rolled_back".
    // Throws std::invalid_argument if the transaction does not exist.
    std::string GetTransactionStatus(const std::string& transaction_id);

    // Sets the prepare phase timeout in milliseconds.
    void SetPrepareTimeout(int milliseconds);

    // Recovers in-flight transactions from persistent log.
    void RecoverFromLog();

    // Returns a set of recovered transaction IDs.
    std::set<std::string> GetRecoveredTransactionIDs();

private:
    enum class TxStatus { PENDING, COMMITTED, ROLLED_BACK };

    struct Transaction {
        std::string id;
        std::unordered_map<std::string, std::string> participants; // service_id -> rollback_endpoint
        std::unordered_map<std::string, bool> votes; // service_id -> vote (true for commit, false for abort)
        TxStatus status;
        std::chrono::steady_clock::time_point start_time;
    };

    // Log file path for persistence.
    const std::string log_file_path = "distributed_tx_log.txt";

    // Mutex to protect transactions map.
    std::mutex mtx;
    std::unordered_map<std::string, Transaction> transactions;
    int next_tx_id;
    int prepare_timeout_ms;

    // Background thread for monitoring timeouts.
    std::thread monitor_thread;
    bool stop_monitor;

    // Set of transaction IDs recovered via RecoverFromLog.
    std::set<std::string> recovered_tx_ids;

    // Internal helper functions.
    void monitorTransactions();
    void finalizeTransaction(Transaction& tx, TxStatus final_status);
    void logTransaction(const std::string& tx_id, const std::string& status);
};

} // namespace distributed_tx

#endif