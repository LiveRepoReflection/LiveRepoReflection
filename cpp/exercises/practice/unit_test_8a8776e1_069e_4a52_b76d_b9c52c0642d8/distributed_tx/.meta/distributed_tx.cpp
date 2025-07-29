#include "distributed_tx.h"
#include <iostream>
#include <mutex>
#include <thread>
#include <chrono>
#include <unordered_map>
#include <string>

namespace {

// Mutex for protecting commit simulation state
std::mutex commit_mutex;
// Map to keep track of commit attempts for transient failures; key is unique per transaction-service pair.
std::unordered_map<std::string, int> commit_attempts;

bool simulate_prepare(const std::string& service, const std::string& transaction_id) {
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    if (service == "service_fail_prepare") {
        std::cout << "Service " << service << " failed in prepare for transaction " << transaction_id << ".\n";
        return false;
    }
    std::cout << "Service " << service << " prepared successfully for transaction " << transaction_id << ".\n";
    return true;
}

bool simulate_commit(const std::string& service, const std::string& transaction_id) {
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    if (service == "service_retry_commit") {
        std::lock_guard<std::mutex> lock(commit_mutex);
        std::string key = transaction_id + service;
        if (commit_attempts[key] < 1) {
            commit_attempts[key]++;
            std::cout << "Service " << service << " transient failure on commit for transaction " << transaction_id << ".\n";
            return false;
        } else {
            std::cout << "Service " << service << " committed successfully on retry for transaction " << transaction_id << ".\n";
            return true;
        }
    }
    std::cout << "Service " << service << " committed successfully for transaction " << transaction_id << ".\n";
    return true;
}

bool simulate_rollback(const std::string& service, const std::string& transaction_id) {
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    std::cout << "Service " << service << " rolled back transaction " << transaction_id << ".\n";
    return true;
}

}

namespace distributed_tx {

bool process_transaction(const std::vector<std::string>& services, const std::string& user_action) {
    // Generate a unique transaction_id using user_action and current time.
    std::string transaction_id = user_action + "_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
    std::vector<std::string> preparedServices;
    
    // Prepare phase: try to prepare for all services.
    for (const auto& service : services) {
        bool prepared = simulate_prepare(service, transaction_id);
        if (!prepared) {
            // Rollback previously prepared services if any failure occurs.
            for (const auto& s : preparedServices) {
                simulate_rollback(s, transaction_id);
            }
            std::cout << "Transaction " << transaction_id << " rolled back due to prepare failure.\n";
            return false;
        }
        preparedServices.push_back(service);
    }
    
    // Commit phase: commit for each prepared service with retries for transient failures.
    for (const auto& service : preparedServices) {
        bool committed = false;
        int retries = 0;
        // Retry commit up to 3 times.
        while (!committed && retries < 3) {
            committed = simulate_commit(service, transaction_id);
            if (!committed) {
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
                retries++;
            }
        }
        if (!committed) {
            // If commit fails after retries, rollback all services.
            for (const auto& s : preparedServices) {
                simulate_rollback(s, transaction_id);
            }
            std::cout << "Transaction " << transaction_id << " rolled back due to commit failure on service " << service << ".\n";
            return false;
        }
    }
    
    std::cout << "Transaction " << transaction_id << " committed successfully.\n";
    return true;
}

int recover_transactions() {
    // In this simulation we assume recovery finds no in-doubt transactions.
    std::cout << "Recovery process invoked. No in-doubt transactions found.\n";
    return 0;
}

}