#include "distributed_tx.h"
#include <future>
#include <chrono>
#include <thread>
#include <string>

namespace {
    // Simulate a service call for a given phase.
    // phase can be "prepare", "commit", or "abort".
    bool simulateServiceCall(const std::string& service, const std::string& phase, int timeout_ms) {
        if (phase == "prepare") {
            if (service.find("fail") != std::string::npos) {
                // Simulate a failed prepare quickly.
                std::this_thread::sleep_for(std::chrono::milliseconds(50));
                return false;
            } else if (service.find("timeout") != std::string::npos) {
                // Simulate a timeout by sleeping longer than the allowed timeout.
                std::this_thread::sleep_for(std::chrono::milliseconds(timeout_ms + 200));
                return false;
            } else {
                // Simulate a successful prepare.
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                return true;
            }
        } else if (phase == "commit") {
            // Simulate processing for commit.
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            return true;
        } else if (phase == "abort") {
            // Simulate processing for abort.
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            return true;
        }
        return false;
    }
}

bool TransactionManager::executeTransaction(const Transaction& tx) {
    // Phase 1: Prepare Phase
    std::vector<std::future<bool>> prepare_futures;
    
    for (const auto& service : tx.services) {
        prepare_futures.push_back(std::async(std::launch::async, [service, &tx]() {
            return simulateServiceCall(service, "prepare", tx.timeout_ms);
        }));
    }
    
    bool all_prepared = true;
    for (auto& fut : prepare_futures) {
        if (fut.wait_for(std::chrono::milliseconds(tx.timeout_ms)) == std::future_status::timeout) {
            all_prepared = false;
            break;
        }
        if (!fut.get()) {
            all_prepared = false;
            break;
        }
    }
    
    if (!all_prepared) {
        // If prepare phase failed or timed out, send Abort to all services.
        std::vector<std::future<bool>> abort_futures;
        for (const auto& service : tx.services) {
            abort_futures.push_back(std::async(std::launch::async, [service, &tx]() {
                return simulateServiceCall(service, "abort", tx.timeout_ms);
            }));
        }
        for (auto& fut : abort_futures) {
            fut.wait();
        }
        return false;
    }
    
    // Phase 2: Commit Phase
    std::vector<std::future<bool>> commit_futures;
    for (const auto& service : tx.services) {
        commit_futures.push_back(std::async(std::launch::async, [service, &tx]() {
            return simulateServiceCall(service, "commit", tx.timeout_ms);
        }));
    }
    
    bool all_committed = true;
    for (auto& fut : commit_futures) {
        if (fut.wait_for(std::chrono::milliseconds(tx.timeout_ms)) == std::future_status::timeout) {
            all_committed = false;
            break;
        }
        if (!fut.get()) {
            all_committed = false;
            break;
        }
    }
    
    return all_committed;
}