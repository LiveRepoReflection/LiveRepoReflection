#include <atomic>
#include <chrono>
#include <future>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>
#include "distributed_tx.h"

// Execute operation on each participant, returning results of both execution and prepare phases
bool Coordinator::executeTransaction(std::vector<Participant*> participants, std::string operation) {
    if (participants.empty()) {
        return true;  // No participants means successful completion by default
    }

    // Step 1: Execute the operation on all participants
    std::vector<std::future<bool>> executeFutures;
    for (size_t i = 0; i < participants.size(); ++i) {
        executeFutures.push_back(std::async(std::launch::async, [&, i]() {
            bool success = participants[i]->execute(operation);
            if (!success) {
                std::cerr << "Participant " << i << " failed to execute the operation" << std::endl;
            }
            return success;
        }));
    }

    // Wait for all execution results
    bool executeSuccess = true;
    for (size_t i = 0; i < executeFutures.size(); ++i) {
        try {
            auto status = executeFutures[i].wait_for(std::chrono::milliseconds(500));
            if (status == std::future_status::timeout) {
                std::cerr << "Participant " << i << " execution timed out" << std::endl;
                executeSuccess = false;
                continue;
            }
            if (!executeFutures[i].get()) {
                executeSuccess = false;
            }
        } catch (const std::exception& e) {
            std::cerr << "Exception during execute for participant " << i << ": " << e.what() << std::endl;
            executeSuccess = false;
        }
    }

    // If any execution failed, rollback all participants
    if (!executeSuccess) {
        rollbackAll(participants);
        return false;
    }

    // Step 2: Prepare phase
    std::vector<std::future<bool>> prepareFutures;
    std::atomic<bool> allPrepared(true);
    std::mutex preparedMutex;
    std::vector<bool> prepareResults(participants.size(), false);

    for (size_t i = 0; i < participants.size(); ++i) {
        prepareFutures.push_back(std::async(std::launch::async, [&, i]() {
            bool prepared = participants[i]->prepare();
            {
                std::lock_guard<std::mutex> lock(preparedMutex);
                prepareResults[i] = prepared;
            }
            if (!prepared) {
                std::cerr << "Participant " << i << " failed to prepare" << std::endl;
                allPrepared = false;
            }
            return prepared;
        }));
    }

    // Wait for all prepare results with timeout
    std::vector<bool> receivedPrepare(participants.size(), false);
    for (size_t i = 0; i < prepareFutures.size(); ++i) {
        try {
            auto status = prepareFutures[i].wait_for(std::chrono::milliseconds(500));
            if (status == std::future_status::timeout) {
                std::cerr << "Participant " << i << " prepare timed out" << std::endl;
                allPrepared = false;
            } else {
                receivedPrepare[i] = true;
                if (!prepareFutures[i].get()) {
                    allPrepared = false;
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "Exception during prepare for participant " << i << ": " << e.what() << std::endl;
            allPrepared = false;
        }
    }

    // If any prepare failed or timed out, rollback all participants
    if (!allPrepared.load()) {
        rollbackAll(participants);
        return false;
    }

    // Step 3: Commit phase
    std::vector<std::future<bool>> commitFutures;
    std::atomic<bool> allCommitted(true);
    
    for (size_t i = 0; i < participants.size(); ++i) {
        commitFutures.push_back(std::async(std::launch::async, [&, i]() {
            bool committed = participants[i]->commit();
            if (!committed) {
                std::cerr << "Participant " << i << " failed to commit" << std::endl;
                allCommitted = false;
            }
            return committed;
        }));
    }

    // Wait for all commit results with timeout
    for (size_t i = 0; i < commitFutures.size(); ++i) {
        try {
            auto status = commitFutures[i].wait_for(std::chrono::milliseconds(500));
            if (status == std::future_status::timeout) {
                std::cerr << "Participant " << i << " commit timed out" << std::endl;
                allCommitted = false;
            } else if (!commitFutures[i].get()) {
                allCommitted = false;
            }
        } catch (const std::exception& e) {
            std::cerr << "Exception during commit for participant " << i << ": " << e.what() << std::endl;
            allCommitted = false;
        }
    }

    // If any commit failed, attempt to rollback all participants
    if (!allCommitted.load()) {
        std::cerr << "Commit phase failed. Attempting rollback..." << std::endl;
        rollbackAll(participants);
        return false;
    }

    return true;
}

// Private helper method to rollback all participants
void Coordinator::rollbackAll(std::vector<Participant*>& participants) {
    std::vector<std::future<bool>> rollbackFutures;
    
    for (size_t i = 0; i < participants.size(); ++i) {
        rollbackFutures.push_back(std::async(std::launch::async, [&, i]() {
            bool rolled_back = participants[i]->rollback();
            if (!rolled_back) {
                std::cerr << "Failed to rollback participant " << i << std::endl;
            }
            return rolled_back;
        }));
    }

    // Wait for all rollbacks to complete - best effort
    for (size_t i = 0; i < rollbackFutures.size(); ++i) {
        try {
            auto status = rollbackFutures[i].wait_for(std::chrono::milliseconds(500));
            if (status == std::future_status::timeout) {
                std::cerr << "Rollback for participant " << i << " timed out" << std::endl;
            } else if (!rollbackFutures[i].get()) {
                std::cerr << "Rollback for participant " << i << " failed" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cerr << "Exception during rollback for participant " << i << ": " << e.what() << std::endl;
        }
    }
}