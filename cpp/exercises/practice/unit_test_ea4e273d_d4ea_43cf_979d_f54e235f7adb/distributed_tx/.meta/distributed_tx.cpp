#include "distributed_tx.h"
#include <algorithm>
#include <chrono>
#include <iomanip>
#include <sstream>

std::atomic<int> TransactionCoordinator::transactionCounter_(0);

TransactionCoordinator::TransactionCoordinator()
    : state_(TransactionState::INACTIVE), transactionId_(0) {
}

TransactionCoordinator::~TransactionCoordinator() {
    // Clean up any unfinished transaction
    if (state_ == TransactionState::ACTIVE || state_ == TransactionState::COMMITTING) {
        rollback();
    }
}

void TransactionCoordinator::begin() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    // Clean up any previous transaction data
    participants_.clear();
    uniqueParticipants_.clear();
    
    // Set initial state
    state_ = TransactionState::ACTIVE;
    transactionId_ = ++transactionCounter_;
    
    logEvent("Transaction started");
}

void TransactionCoordinator::enroll(std::shared_ptr<TransactionParticipant> participant) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (state_ != TransactionState::ACTIVE) {
        logEvent("Cannot enroll participant: transaction not active");
        return;
    }
    
    if (!participant) {
        logEvent("Cannot enroll null participant");
        return;
    }
    
    // Only add participant if it's not already enrolled (to ensure idempotency)
    if (uniqueParticipants_.find(participant) == uniqueParticipants_.end()) {
        participants_.push_back(participant);
        uniqueParticipants_.insert(participant);
        logEvent("Participant enrolled");
    } else {
        logEvent("Participant already enrolled (ignored)");
    }
}

bool TransactionCoordinator::commit() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (state_ != TransactionState::ACTIVE) {
        logEvent("Cannot commit: transaction not active");
        return false;
    }
    
    if (participants_.empty()) {
        logEvent("Commit successful (no participants)");
        state_ = TransactionState::COMMITTED;
        return true;
    }
    
    state_ = TransactionState::COMMITTING;
    logEvent("Beginning commit phase");
    
    // First phase: Prepare
    logEvent("Starting prepare phase");
    size_t preparedCount = 0;
    
    for (auto& participant : participants_) {
        try {
            if (!participant->prepare()) {
                // Prepare failed, rollback already prepared participants
                logEvent("Prepare phase failed for a participant");
                
                // Compensate already prepared participants in reverse order
                for (size_t i = 0; i < preparedCount; ++i) {
                    size_t idx = preparedCount - 1 - i;
                    try {
                        participants_[idx]->compensate();
                    } catch (const std::exception& e) {
                        logEvent("Exception during compensation: " + std::string(e.what()));
                    }
                }
                
                state_ = TransactionState::ROLLED_BACK;
                return false;
            }
            preparedCount++;
        } catch (const std::exception& e) {
            logEvent("Exception during prepare: " + std::string(e.what()));
            
            // Compensate already prepared participants in reverse order
            for (size_t i = 0; i < preparedCount; ++i) {
                size_t idx = preparedCount - 1 - i;
                try {
                    participants_[idx]->compensate();
                } catch (const std::exception& e) {
                    logEvent("Exception during compensation: " + std::string(e.what()));
                }
            }
            
            state_ = TransactionState::ROLLED_BACK;
            return false;
        }
    }
    
    logEvent("Prepare phase completed successfully");
    
    // Second phase: Commit
    logEvent("Starting commit phase");
    size_t committedCount = 0;
    
    for (auto& participant : participants_) {
        try {
            if (!participant->commit()) {
                logEvent("Commit phase failed for a participant");
                
                // Compensate all participants in reverse order
                // First compensate the participant that just failed
                participant->compensate();
                
                // Then compensate already committed participants
                for (size_t i = 0; i < committedCount; ++i) {
                    size_t idx = committedCount - 1 - i;
                    try {
                        participants_[idx]->compensate();
                    } catch (const std::exception& e) {
                        logEvent("Exception during compensation: " + std::string(e.what()));
                    }
                }
                
                // Finally compensate the remaining prepared but not committed participants
                for (size_t i = committedCount + 1; i < participants_.size(); ++i) {
                    try {
                        participants_[i]->compensate();
                    } catch (const std::exception& e) {
                        logEvent("Exception during compensation: " + std::string(e.what()));
                    }
                }
                
                state_ = TransactionState::ROLLED_BACK;
                return false;
            }
            committedCount++;
        } catch (const std::exception& e) {
            logEvent("Exception during commit: " + std::string(e.what()));
            
            // Compensate all participants in reverse order
            for (int i = static_cast<int>(participants_.size()) - 1; i >= 0; --i) {
                try {
                    participants_[i]->compensate();
                } catch (const std::exception& e) {
                    logEvent("Exception during compensation: " + std::string(e.what()));
                }
            }
            
            state_ = TransactionState::ROLLED_BACK;
            return false;
        }
    }
    
    logEvent("Commit phase completed successfully");
    state_ = TransactionState::COMMITTED;
    return true;
}

bool TransactionCoordinator::rollback() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (state_ != TransactionState::ACTIVE && state_ != TransactionState::COMMITTING) {
        logEvent("Cannot rollback: transaction not active or committing");
        return false;
    }
    
    if (participants_.empty()) {
        logEvent("Rollback successful (no participants)");
        state_ = TransactionState::ROLLED_BACK;
        return true;
    }
    
    state_ = TransactionState::ROLLING_BACK;
    logEvent("Beginning rollback phase");
    
    bool allSuccessful = true;
    
    // Execute compensations in reverse order
    for (int i = static_cast<int>(participants_.size()) - 1; i >= 0; --i) {
        try {
            if (!participants_[i]->compensate()) {
                logEvent("Compensation failed for a participant");
                allSuccessful = false;
                // Continue with other compensations even if one fails
            }
        } catch (const std::exception& e) {
            logEvent("Exception during compensation: " + std::string(e.what()));
            allSuccessful = false;
            // Continue with other compensations even if one throws
        }
    }
    
    state_ = TransactionState::ROLLED_BACK;
    
    if (allSuccessful) {
        logEvent("Rollback completed successfully");
    } else {
        logEvent("Rollback completed with failures");
    }
    
    return allSuccessful;
}

void TransactionCoordinator::logEvent(const std::string& event) {
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    
    std::stringstream ss;
    ss << "[Tx-" << transactionId_ << "] " << std::put_time(std::localtime(&time), "%H:%M:%S") 
       << " - " << event;
    
    std::cout << ss.str() << std::endl;
}