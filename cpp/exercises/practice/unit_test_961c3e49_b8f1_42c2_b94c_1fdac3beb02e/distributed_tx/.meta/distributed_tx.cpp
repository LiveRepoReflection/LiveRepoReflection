#include "distributed_tx.h"
#include <sstream>
#include <iostream>
#include <thread>
#include <algorithm>

TransactionCoordinator::TransactionCoordinator() {
    log_file_.open("coordinator.log", std::ios::app);
}

TransactionCoordinator::~TransactionCoordinator() {
    log_file_.close();
}

void TransactionCoordinator::processOutput(const std::string& message) {
    std::cout << message << std::endl;
}

void TransactionCoordinator::processCommand(const std::string& command) {
    auto tokens = tokenize(command);
    if (tokens.empty()) {
        processOutput("UNKNOWN_COMMAND");
        return;
    }

    try {
        if (tokens[0] == "BEGIN") {
            handleBegin(tokens);
        } else if (tokens[0] == "PREPARED") {
            handlePrepared(tokens);
        } else if (tokens[0] == "ABORT") {
            handleAbort(tokens);
        } else if (tokens[0] == "TIMEOUT") {
            handleTimeout(tokens);
        } else if (tokens[0] == "RECOVER") {
            handleRecover();
        } else if (tokens[0] == "PRINT_LOG") {
            handlePrintLog();
        } else {
            processOutput("UNKNOWN_COMMAND");
        }
    } catch (const std::exception& e) {
        processOutput("ERROR: " + std::string(e.what()));
    }
}

std::vector<std::string> TransactionCoordinator::tokenize(const std::string& command) {
    std::vector<std::string> tokens;
    std::istringstream iss(command);
    std::string token;
    while (iss >> token) {
        tokens.push_back(token);
    }
    return tokens;
}

void TransactionCoordinator::handleBegin(const std::vector<std::string>& tokens) {
    if (tokens.size() < 3) {
        throw std::runtime_error("Invalid BEGIN command format");
    }

    int tid = std::stoi(tokens[1]);
    std::set<int> services;
    
    for (size_t i = 2; i < tokens.size(); ++i) {
        int sid = std::stoi(tokens[i]);
        if (!services.insert(sid).second) {
            throw std::runtime_error("Duplicate service ID");
        }
    }

    std::lock_guard<std::mutex> lock(mutex_);
    if (transactions_.find(tid) != transactions_.end()) {
        throw std::runtime_error("Transaction ID already exists");
    }

    transactions_[tid] = std::make_unique<Transaction>(tid, services);
    writeToLog("BEGIN " + std::to_string(tid));

    for (int sid : services) {
        processOutput("PREPARE " + std::to_string(tid) + " " + std::to_string(sid));
    }

    // Start timeout checking in a separate thread
    std::thread([this, tid]() {
        checkTimeout(tid);
    }).detach();
}

void TransactionCoordinator::handlePrepared(const std::vector<std::string>& tokens) {
    if (tokens.size() != 3) {
        throw std::runtime_error("Invalid PREPARED command format");
    }

    int tid = std::stoi(tokens[1]);
    int sid = std::stoi(tokens[2]);

    std::lock_guard<std::mutex> lock(mutex_);
    auto it = transactions_.find(tid);
    if (it == transactions_.end()) {
        throw std::runtime_error("Unknown transaction ID");
    }

    Transaction& tx = *(it->second);
    if (tx.services.find(sid) == tx.services.end()) {
        throw std::runtime_error("Invalid service ID for transaction");
    }

    writeToLog("PREPARED " + std::to_string(tid) + " " + std::to_string(sid));
    tx.prepared_services.insert(sid);

    if (tx.prepared_services == tx.services && !tx.is_aborted) {
        commitTransaction(tx);
    }
}

void TransactionCoordinator::handleAbort(const std::vector<std::string>& tokens) {
    if (tokens.size() != 3) {
        throw std::runtime_error("Invalid ABORT command format");
    }

    int tid = std::stoi(tokens[1]);
    int sid = std::stoi(tokens[2]);

    std::lock_guard<std::mutex> lock(mutex_);
    auto it = transactions_.find(tid);
    if (it == transactions_.end()) {
        throw std::runtime_error("Unknown transaction ID");
    }

    Transaction& tx = *(it->second);
    if (tx.services.find(sid) == tx.services.end()) {
        throw std::runtime_error("Invalid service ID for transaction");
    }

    writeToLog("ABORT " + std::to_string(tid) + " " + std::to_string(sid));
    rollbackTransaction(tx);
}

void TransactionCoordinator::handleTimeout(const std::vector<std::string>& tokens) {
    if (tokens.size() != 3) {
        throw std::runtime_error("Invalid TIMEOUT command format");
    }

    int tid = std::stoi(tokens[1]);
    int sid = std::stoi(tokens[2]);

    std::lock_guard<std::mutex> lock(mutex_);
    auto it = transactions_.find(tid);
    if (it == transactions_.end()) {
        throw std::runtime_error("Unknown transaction ID");
    }

    Transaction& tx = *(it->second);
    if (tx.services.find(sid) == tx.services.end()) {
        throw std::runtime_error("Invalid service ID for transaction");
    }

    writeToLog("TIMEOUT " + std::to_string(tid) + " " + std::to_string(sid));
    rollbackTransaction(tx);
}

void TransactionCoordinator::handleRecover() {
    std::lock_guard<std::mutex> lock(mutex_);
    writeToLog("RECOVER");
    // In a real implementation, we would read the log file and rebuild the state
    processOutput("Recovery initiated");
}

void TransactionCoordinator::handlePrintLog() {
    std::ifstream log("coordinator.log");
    std::string line;
    while (std::getline(log, line)) {
        processOutput(line);
    }
}

void TransactionCoordinator::commitTransaction(Transaction& tx) {
    writeToLog("COMMIT " + std::to_string(tx.id));
    tx.is_committed = true;

    for (int sid : tx.services) {
        processOutput("COMMIT " + std::to_string(tx.id) + " " + std::to_string(sid));
    }

    processOutput("TRANSACTION_COMMITTED " + std::to_string(tx.id));
}

void TransactionCoordinator::rollbackTransaction(Transaction& tx) {
    if (tx.is_aborted) return;
    
    writeToLog("ROLLBACK " + std::to_string(tx.id));
    tx.is_aborted = true;

    for (int sid : tx.services) {
        processOutput("ROLLBACK " + std::to_string(tx.id) + " " + std::to_string(sid));
    }

    processOutput("TRANSACTION_ABORTED " + std::to_string(tx.id));
}

void TransactionCoordinator::writeToLog(const std::string& entry) {
    log_file_ << entry << std::endl;
    log_file_.flush();
}

void TransactionCoordinator::checkTimeout(int transaction_id) {
    std::this_thread::sleep_for(std::chrono::milliseconds(TIMEOUT_MS));
    
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = transactions_.find(transaction_id);
    if (it != transactions_.end()) {
        Transaction& tx = *(it->second);
        if (!tx.is_committed && !tx.is_aborted && 
            tx.prepared_services.size() != tx.services.size()) {
            rollbackTransaction(tx);
        }
    }
}