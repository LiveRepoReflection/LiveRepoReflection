#include "distributed_tx.h"
#include <algorithm>
#include <iostream>

TransactionCoordinator::TransactionCoordinator(
    size_t maxParticipants,
    std::chrono::milliseconds timeout
) : maxParticipants_(maxParticipants), timeout_(timeout) {}

bool TransactionCoordinator::validateParticipants(
    const std::vector<std::shared_ptr<IParticipant>>& participants
) {
    if (participants.empty() || participants.size() > maxParticipants_) {
        return false;
    }

    return std::all_of(
        participants.begin(),
        participants.end(),
        [](const auto& p) { return p != nullptr; }
    );
}

PrepareResult TransactionCoordinator::preparePhase(
    const std::vector<std::shared_ptr<IParticipant>>& participants
) {
    std::vector<std::future<PrepareResult>> futures;
    
    // Launch prepare operations asynchronously
    for (const auto& participant : participants) {
        futures.push_back(std::async(
            std::launch::async,
            [participant]() { return participant->prepare(); }
        ));
    }
    
    // Wait for all prepare results
    for (auto& future : futures) {
        if (future.wait_for(timeout_) == std::future_status::timeout) {
            return PrepareResult::TIMEOUT;
        }
        
        auto result = future.get();
        if (result != PrepareResult::READY) {
            return result;
        }
    }
    
    return PrepareResult::READY;
}

TransactionResult TransactionCoordinator::commitPhase(
    const std::vector<std::shared_ptr<IParticipant>>& participants
) {
    std::vector<std::future<bool>> futures;
    
    // Launch commit operations asynchronously
    for (const auto& participant : participants) {
        futures.push_back(std::async(
            std::launch::async,
            [participant]() { return participant->commit(); }
        ));
    }
    
    // Wait for all commit results
    bool allCommitted = true;
    for (auto& future : futures) {
        if (future.wait_for(timeout_) == std::future_status::timeout) {
            allCommitted = false;
            break;
        }
        
        if (!future.get()) {
            allCommitted = false;
            break;
        }
    }
    
    if (!allCommitted) {
        rollbackAll(participants);
        return TransactionResult::ABORTED;
    }
    
    return TransactionResult::COMMITTED;
}

void TransactionCoordinator::rollbackAll(
    const std::vector<std::shared_ptr<IParticipant>>& participants
) {
    std::vector<std::future<bool>> futures;
    
    // Launch rollback operations asynchronously
    for (const auto& participant : participants) {
        futures.push_back(std::async(
            std::launch::async,
            [participant]() { return participant->rollback(); }
        ));
    }
    
    // Wait for all rollbacks to complete
    for (auto& future : futures) {
        try {
            if (future.wait_for(timeout_) == std::future_status::timeout) {
                std::cerr << "Warning: Rollback timeout" << std::endl;
                continue;
            }
            if (!future.get()) {
                std::cerr << "Warning: Rollback failed" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cerr << "Error during rollback: " << e.what() << std::endl;
        }
    }
}

TransactionResult TransactionCoordinator::executeTransaction(
    const std::vector<std::shared_ptr<IParticipant>>& participants
) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (!validateParticipants(participants)) {
        return TransactionResult::INVALID;
    }
    
    // Phase 1: Prepare
    auto prepareResult = preparePhase(participants);
    
    if (prepareResult == PrepareResult::TIMEOUT) {
        rollbackAll(participants);
        return TransactionResult::TIMEOUT;
    }
    
    if (prepareResult == PrepareResult::ABORT) {
        rollbackAll(participants);
        return TransactionResult::ABORTED;
    }
    
    // Phase 2: Commit
    return commitPhase(participants);
}