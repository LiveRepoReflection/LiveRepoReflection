#include "distributed_tx.h"
#include <fstream>
#include <sstream>
#include <iterator>
#include <ctime>
#include <thread>
#include <chrono>
#include <iostream>

namespace distributed_tx {

Coordinator::Coordinator() : next_tx_id(1), prepare_timeout_ms(100), stop_monitor(false) {
    monitor_thread = std::thread(&Coordinator::monitorTransactions, this);
}

Coordinator::~Coordinator() {
    {
        std::lock_guard<std::mutex> lock(mtx);
        stop_monitor = true;
    }
    if (monitor_thread.joinable()) {
        monitor_thread.join();
    }
}

std::string Coordinator::BeginTransaction() {
    std::lock_guard<std::mutex> lock(mtx);
    std::ostringstream oss;
    oss << "tx" << next_tx_id++;
    std::string tx_id = oss.str();
    Transaction tx;
    tx.id = tx_id;
    tx.status = TxStatus::PENDING;
    tx.start_time = std::chrono::steady_clock::now();
    transactions[tx_id] = tx;
    logTransaction(tx_id, "pending");
    return tx_id;
}

void Coordinator::RegisterParticipant(const std::string& transaction_id, const std::string& service_id, const std::string& rollback_endpoint) {
    std::lock_guard<std::mutex> lock(mtx);
    auto it = transactions.find(transaction_id);
    if(it == transactions.end()) {
        throw std::invalid_argument("Transaction ID does not exist");
    }
    Transaction &tx = it->second;
    if(tx.participants.count(service_id) > 0) {
        throw std::invalid_argument("Participant already registered");
    }
    tx.participants[service_id] = rollback_endpoint;
    // No vote submitted at registration.
}

void Coordinator::ReportVote(const std::string& transaction_id, const std::string& service_id, bool voteCommit) {
    std::lock_guard<std::mutex> lock(mtx);
    auto it = transactions.find(transaction_id);
    if(it == transactions.end()) {
        throw std::invalid_argument("Transaction ID does not exist");
    }
    Transaction &tx = it->second;
    if(tx.participants.find(service_id) == tx.participants.end()) {
        throw std::invalid_argument("Participant not registered in transaction");
    }
    // Record the vote.
    tx.votes[service_id] = voteCommit;

    // If any vote is false, immediately rollback.
    if(!voteCommit) {
        if(tx.status == TxStatus::PENDING) {
            finalizeTransaction(tx, TxStatus::ROLLED_BACK);
        }
        return;
    }
    // Check if all participants have voted.
    if(tx.votes.size() == tx.participants.size()) {
        // All votes are present and none were false.
        bool allCommit = true;
        for(const auto &vote_pair : tx.votes) {
            if(vote_pair.second == false) {
                allCommit = false;
                break;
            }
        }
        if(allCommit && tx.status == TxStatus::PENDING) {
            finalizeTransaction(tx, TxStatus::COMMITTED);
        }
    }
}

std::string Coordinator::GetTransactionStatus(const std::string& transaction_id) {
    std::lock_guard<std::mutex> lock(mtx);
    auto it = transactions.find(transaction_id);
    if(it == transactions.end()) {
        throw std::invalid_argument("Transaction ID does not exist");
    }
    Transaction &tx = it->second;
    switch(tx.status) {
        case TxStatus::PENDING:
            return "pending";
        case TxStatus::COMMITTED:
            return "committed";
        case TxStatus::ROLLED_BACK:
            return "rolled_back";
    }
    return "unknown";
}

void Coordinator::SetPrepareTimeout(int milliseconds) {
    std::lock_guard<std::mutex> lock(mtx);
    prepare_timeout_ms = milliseconds;
}

void Coordinator::monitorTransactions() {
    while (true) {
        {
            std::lock_guard<std::mutex> lock(mtx);
            if(stop_monitor) {
                break;
            }
            auto now = std::chrono::steady_clock::now();
            for(auto &pair : transactions) {
                Transaction &tx = pair.second;
                if(tx.status == TxStatus::PENDING) {
                    auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - tx.start_time).count();
                    if(elapsed > prepare_timeout_ms) {
                        // If not all participants have voted in prepare phase, rollback.
                        if(tx.votes.size() < tx.participants.size()) {
                            finalizeTransaction(tx, TxStatus::ROLLED_BACK);
                        }
                    }
                }
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
}

void Coordinator::finalizeTransaction(Transaction& tx, TxStatus final_status) {
    tx.status = final_status;
    if(final_status == TxStatus::COMMITTED) {
        logTransaction(tx.id, "committed");
        // Simulate sending commit messages and acknowledgments.
    } else if(final_status == TxStatus::ROLLED_BACK) {
        logTransaction(tx.id, "rolled_back");
        // Simulate sending rollback messages and acknowledgments.
    }
}

void Coordinator::logTransaction(const std::string& tx_id, const std::string& status) {
    std::ofstream ofs(log_file_path, std::ios::out | std::ios::app);
    if(ofs.is_open()){
        ofs << tx_id << " " << status << std::endl;
        ofs.close();
    }
}

void Coordinator::RecoverFromLog() {
    std::lock_guard<std::mutex> lock(mtx);
    std::ifstream ifs(log_file_path);
    if(!ifs.is_open()){
        return;
    }
    std::unordered_map<std::string, std::string> log_records;
    std::string line;
    while(std::getline(ifs, line)) {
        if(line.empty()){
            continue;
        }
        std::istringstream iss(line);
        std::string tx_id, status;
        iss >> tx_id >> status;
        log_records[tx_id] = status;
    }
    ifs.close();
    // Clear current transactions map.
    transactions.clear();
    recovered_tx_ids.clear();
    // Reconstruct transactions from log.
    for(const auto &record : log_records) {
        Transaction tx;
        tx.id = record.first;
        // For recovery we assume participants were registered but if transaction was pending, we force rollback.
        if(record.second == "pending") {
            tx.status = TxStatus::ROLLED_BACK;
        } else if(record.second == "committed") {
            tx.status = TxStatus::COMMITTED;
        } else {
            tx.status = TxStatus::ROLLED_BACK;
        }
        tx.start_time = std::chrono::steady_clock::now();
        // Since we don't persist participant details, we leave participants empty.
        transactions[record.first] = tx;
        recovered_tx_ids.insert(record.first);
    }
}

std::set<std::string> Coordinator::GetRecoveredTransactionIDs() {
    std::lock_guard<std::mutex> lock(mtx);
    return recovered_tx_ids;
}

} // namespace distributed_tx