#include "transaction_orchestrator.h"
#include <thread>
#include <chrono>

TransactionOrchestrator::TransactionOrchestrator(const std::vector<ServiceInterface*>& services, int timeout_ms)
    : services_(services), timeout_ms_(timeout_ms), committed_(false), finalized_(false) {}

bool TransactionOrchestrator::runTransaction() {
    bool allReady = true;
    {
        std::lock_guard<std::mutex> lock(mtx_);
        if (finalized_) {
            return committed_;
        }
    }

    // Prepare phase: Invoke prepare on each service concurrently.
    std::vector<std::thread> threads;
    std::vector<bool> prepareResults(services_.size(), false);
    for (size_t i = 0; i < services_.size(); i++) {
        threads.emplace_back([this, i, &prepareResults]() {
            prepareResults[i] = services_[i]->prepare();
        });
    }

    // Measure the total time taken for the prepare phase.
    auto start = std::chrono::steady_clock::now();
    for (auto& t : threads) {
        if(t.joinable()) {
            t.join();
        }
    }
    auto end = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    if (duration.count() > timeout_ms_) {
        allReady = false;
    } else {
        for (bool res : prepareResults) {
            if (!res) {
                allReady = false;
                break;
            }
        }
    }

    {
        std::lock_guard<std::mutex> lock(mtx_);
        if (finalized_) {
            return committed_;
        }
        finalized_ = true;
    }

    // Final phase: Commit if all services are ready, otherwise abort.
    if (allReady) {
        for (auto service : services_) {
            service->commit();
        }
        {
            std::lock_guard<std::mutex> lock(mtx_);
            committed_ = true;
        }
    } else {
        for (auto service : services_) {
            service->abort();
        }
        {
            std::lock_guard<std::mutex> lock(mtx_);
            committed_ = false;
        }
    }

    return committed_;
}

void TransactionOrchestrator::finalizeTransaction() {
    std::lock_guard<std::mutex> lock(mtx_);
    if (finalized_) return;

    bool allReady = true;
    // Re-run prepare phase concurrently.
    std::vector<std::thread> threads;
    std::vector<bool> prepareResults(services_.size(), false);
    for (size_t i = 0; i < services_.size(); i++) {
        threads.emplace_back([this, i, &prepareResults]() {
            prepareResults[i] = services_[i]->prepare();
        });
    }
    for (auto& t : threads) {
        if(t.joinable()) {
            t.join();
        }
    }
    for (bool res : prepareResults) {
        if (!res) {
            allReady = false;
            break;
        }
    }

    if (allReady) {
        for (auto service : services_) {
            service->commit();
        }
        committed_ = true;
    } else {
        for (auto service : services_) {
            service->abort();
        }
        committed_ = false;
    }
    finalized_ = true;
}