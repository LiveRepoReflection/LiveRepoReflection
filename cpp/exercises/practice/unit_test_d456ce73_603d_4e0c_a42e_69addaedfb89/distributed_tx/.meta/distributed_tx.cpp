#include "distributed_tx.h"
#include <algorithm>
#include <thread>
#include <sstream>
#include <iomanip>

namespace distributed_tx {

TransactionCoordinator::TransactionCoordinator()
    : commit_max_retries_(3), prepare_timeout_(std::chrono::seconds(5)) {
}

void TransactionCoordinator::set_commit_max_retries(int max_retries) {
    commit_max_retries_ = max_retries;
}

void TransactionCoordinator::set_prepare_timeout(std::chrono::seconds timeout) {
    prepare_timeout_ = timeout;
}

bool TransactionCoordinator::execute_transaction() {
    log("Starting transaction with " + std::to_string(services_.size()) + " services");
    
    if (services_.empty()) {
        log("No services to coordinate, transaction succeeds by default");
        return true;
    }
    
    // Phase 1: Prepare
    if (!prepare_phase()) {
        log("Prepare phase failed, rolling back transaction");
        rollback_all();
        return false;
    }
    
    // Phase 2: Commit
    if (!commit_phase()) {
        log("Commit phase failed after maximum retries, this is a critical error");
        // We don't rollback after a commit failure as this requires manual intervention
        return false;
    }
    
    log("Transaction completed successfully");
    return true;
}

bool TransactionCoordinator::prepare_phase() {
    log("Starting prepare phase");

    std::vector<std::future<bool>> futures;
    std::atomic<bool> any_failure{false};
    std::mutex futures_mutex;

    // Launch all prepare calls concurrently
    for (size_t i = 0; i < services_.size(); ++i) {
        std::lock_guard<std::mutex> lock(futures_mutex);
        futures.push_back(std::async(std::launch::async, [this, i, &any_failure]() -> bool {
            try {
                log("Preparing service " + service_names_[i]);
                bool result = services_[i]();
                if (!result) {
                    log("Service " + service_names_[i] + " returned false from prepare");
                    any_failure.store(true);
                }
                return result;
            } catch (const std::exception& e) {
                log("Service " + service_names_[i] + " threw an exception during prepare: " + e.what());
                any_failure.store(true);
                return false;
            } catch (...) {
                log("Service " + service_names_[i] + " threw an unknown exception during prepare");
                any_failure.store(true);
                return false;
            }
        }));
    }

    // Wait for all futures with timeout
    auto deadline = std::chrono::system_clock::now() + prepare_timeout_;
    bool all_successful = true;

    for (size_t i = 0; i < futures.size(); ++i) {
        if (any_failure.load()) {
            log("Another service already failed, skipping wait for remaining services");
            all_successful = false;
            break;
        }

        std::future_status status = futures[i].wait_until(deadline);
        if (status == std::future_status::timeout) {
            log("Timeout waiting for service " + service_names_[i] + " to prepare");
            all_successful = false;
            break;
        }

        try {
            bool result = futures[i].get();
            if (!result) {
                all_successful = false;
                // No need to break here, as we want to collect all results
            }
        } catch (const std::exception& e) {
            log("Exception occurred while getting prepare result: " + std::string(e.what()));
            all_successful = false;
        }
    }

    log("Prepare phase " + std::string(all_successful ? "successful" : "failed"));
    return all_successful;
}

bool TransactionCoordinator::commit_phase() {
    log("Starting commit phase");
    
    for (size_t i = 0; i < commits_.size(); ++i) {
        bool committed = false;
        
        for (int attempt = 0; attempt < commit_max_retries_; ++attempt) {
            try {
                log("Committing service " + service_names_[i] + " (attempt " + 
                    std::to_string(attempt + 1) + ")");
                
                commits_[i]();
                committed = true;
                break;
            } catch (const std::exception& e) {
                log("Service " + service_names_[i] + " threw an exception during commit: " + 
                    e.what());
                
                if (attempt < commit_max_retries_ - 1) {
                    log("Retrying commit for service " + service_names_[i]);
                    exponential_backoff(attempt);
                }
            } catch (...) {
                log("Service " + service_names_[i] + " threw an unknown exception during commit");
                
                if (attempt < commit_max_retries_ - 1) {
                    log("Retrying commit for service " + service_names_[i]);
                    exponential_backoff(attempt);
                }
            }
        }
        
        if (!committed) {
            log("Failed to commit service " + service_names_[i] + 
                " after " + std::to_string(commit_max_retries_) + " attempts");
            return false;
        }
    }
    
    log("Commit phase successful");
    return true;
}

void TransactionCoordinator::rollback_all() {
    log("Rolling back all services");
    
    std::vector<std::future<void>> futures;
    
    // Launch all rollback calls concurrently
    for (size_t i = 0; i < rollbacks_.size(); ++i) {
        futures.push_back(std::async(std::launch::async, [this, i]() {
            try {
                log("Rolling back service " + service_names_[i]);
                rollbacks_[i]();
            } catch (const std::exception& e) {
                log("Service " + service_names_[i] + " threw an exception during rollback: " + 
                    e.what());
            } catch (...) {
                log("Service " + service_names_[i] + " threw an unknown exception during rollback");
            }
        }));
    }
    
    // Wait for all rollbacks to complete
    for (auto& future : futures) {
        future.wait();
    }
    
    log("Rollback completed");
}

void TransactionCoordinator::exponential_backoff(int attempt) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, 100);

    // Add some randomness to prevent thundering herd problem
    int jitter_ms = dis(gen);
    
    // Calculate backoff time with jitter: 2^attempt * 100ms + jitter
    auto backoff_ms = std::chrono::milliseconds(
        (1 << attempt) * 100 + jitter_ms
    );
    
    log("Backing off for " + std::to_string(backoff_ms.count()) + "ms");
    std::this_thread::sleep_for(backoff_ms);
}

void TransactionCoordinator::log(const std::string& message) {
    auto now = std::chrono::system_clock::now();
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    
    std::stringstream ss;
    ss << "[" << std::put_time(std::localtime(&now_time_t), "%Y-%m-%d %H:%M:%S") << "] " 
       << message;
    
    std::lock_guard<std::mutex> lock(log_mutex_);
    std::cout << ss.str() << std::endl;
}

} // namespace distributed_tx