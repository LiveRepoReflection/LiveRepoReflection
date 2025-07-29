#include "tx_coordinator.h"
#include <future>
#include <chrono>
#include <mutex>
#include <unordered_map>
#include <stdexcept>

// Transaction state tracking
class TransactionState {
private:
    std::mutex mutex_;
    std::unordered_map<std::string, bool> prepared_services_;
    bool all_prepared_;
    
public:
    TransactionState() : all_prepared_(false) {}
    
    void mark_prepared(const std::string& service) {
        std::lock_guard<std::mutex> lock(mutex_);
        prepared_services_[service] = true;
    }
    
    void mark_failed() {
        std::lock_guard<std::mutex> lock(mutex_);
        all_prepared_ = false;
    }
    
    void set_all_prepared() {
        std::lock_guard<std::mutex> lock(mutex_);
        all_prepared_ = true;
    }
    
    bool is_prepared(const std::string& service) {
        std::lock_guard<std::mutex> lock(mutex_);
        return prepared_services_.count(service) > 0;
    }
    
    bool are_all_prepared() {
        std::lock_guard<std::mutex> lock(mutex_);
        return all_prepared_;
    }
};

// Validate input parameters
void validate_input(int N, 
                   const std::vector<std::string>& service_addresses,
                   const std::vector<std::function<std::string(const std::string&)>>& participant_behavior,
                   int prepare_timeout_ms,
                   int completion_timeout_ms) {
    if (N <= 0 || N > 100) {
        throw std::invalid_argument("N must be between 1 and 100");
    }
    if (service_addresses.size() != static_cast<size_t>(N)) {
        throw std::invalid_argument("Number of service addresses must match N");
    }
    if (participant_behavior.size() != static_cast<size_t>(N)) {
        throw std::invalid_argument("Number of participant behaviors must match N");
    }
    if (prepare_timeout_ms <= 0 || prepare_timeout_ms > 5000) {
        throw std::invalid_argument("prepare_timeout_ms must be between 1 and 5000");
    }
    if (completion_timeout_ms <= 0 || completion_timeout_ms > 10000) {
        throw std::invalid_argument("completion_timeout_ms must be between 1 and 10000");
    }
}

// Execute prepare phase for a single participant
std::future<std::string> prepare_participant(
    const std::function<std::string(const std::string&)>& behavior) {
    return std::async(std::launch::async, [behavior]() {
        return behavior("prepare");
    });
}

// Execute commit/rollback phase for a single participant
std::future<std::string> complete_participant(
    const std::function<std::string(const std::string&)>& behavior,
    bool should_commit) {
    return std::async(std::launch::async, [behavior, should_commit]() {
        return behavior(should_commit ? "commit" : "rollback");
    });
}

bool coordinate_transaction(
    int N,
    const std::vector<std::string>& service_addresses,
    const std::vector<std::function<std::string(const std::string&)>>& participant_behavior,
    int prepare_timeout_ms,
    int completion_timeout_ms) {
    
    // Validate input parameters
    validate_input(N, service_addresses, participant_behavior, prepare_timeout_ms, completion_timeout_ms);
    
    // Create transaction state tracker
    TransactionState tx_state;
    
    // Phase 1: Prepare phase
    std::vector<std::future<std::string>> prepare_futures;
    
    // Launch prepare phase for all participants
    for (int i = 0; i < N; ++i) {
        prepare_futures.push_back(prepare_participant(participant_behavior[i]));
    }
    
    // Wait for all prepare responses with timeout
    bool all_prepared = true;
    for (int i = 0; i < N; ++i) {
        auto prepare_status = prepare_futures[i].wait_for(std::chrono::milliseconds(prepare_timeout_ms));
        
        if (prepare_status == std::future_status::timeout) {
            all_prepared = false;
            break;
        }
        
        try {
            std::string result = prepare_futures[i].get();
            if (result != "prepared") {
                all_prepared = false;
                break;
            }
            tx_state.mark_prepared(service_addresses[i]);
        } catch (...) {
            all_prepared = false;
            break;
        }
    }
    
    if (all_prepared) {
        tx_state.set_all_prepared();
    }
    
    // Phase 2: Commit/Rollback phase
    std::vector<std::future<std::string>> completion_futures;
    bool should_commit = tx_state.are_all_prepared();
    
    // Launch completion phase for all participants
    for (int i = 0; i < N; ++i) {
        completion_futures.push_back(complete_participant(participant_behavior[i], should_commit));
    }
    
    // Wait for all completion responses
    for (int i = 0; i < N; ++i) {
        auto completion_status = completion_futures[i].wait_for(std::chrono::milliseconds(completion_timeout_ms));
        
        if (completion_status == std::future_status::timeout) {
            // If timeout during completion phase, we can't guarantee the transaction state
            return false;
        }
        
        try {
            std::string result = completion_futures[i].get();
            if (should_commit && result != "committed") {
                return false;
            }
        } catch (...) {
            return false;
        }
    }
    
    return should_commit;
}