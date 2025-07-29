#include "distributed_tx.h"
#include <chrono>
#include <fstream>
#include <mutex>
#include <string>
#include <thread>

namespace distributed_tx {

static std::mutex log_mutex;

void log_event(const std::string& event) {
    std::lock_guard<std::mutex> lock(log_mutex);
    std::ofstream log_file("distributed_tx.log", std::ios::app);
    if (log_file.is_open()) {
        log_file << event << std::endl;
    }
}

// Timeout threshold in milliseconds
constexpr int TIMEOUT_THRESHOLD_MS = 200;

// Inventory Service Functions
bool inventory_prepare(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Inventory prepare started.");
    // Simulate forced failure if simulate_failure is true for inventory.
    if (txn.simulate_failure) {
        log_event("Transaction " + std::to_string(txn.transaction_id) + ": Inventory prepare forced failure.");
        return false;
    }
    // Normal delay simulate
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Inventory prepared successfully.");
    return true;
}

bool inventory_commit(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Inventory commit started.");
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Inventory committed successfully.");
    return true;
}

void inventory_rollback(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Inventory rollback executed.");
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
}

// Payment Service Functions
bool payment_prepare(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Payment prepare started.");
    // Simulate a timeout if requested for payment service.
    if (txn.simulate_timeout) {
        std::this_thread::sleep_for(std::chrono::milliseconds(TIMEOUT_THRESHOLD_MS + 100));
        log_event("Transaction " + std::to_string(txn.transaction_id) + ": Payment prepare timed out.");
        return false;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Payment prepared successfully.");
    return true;
}

bool payment_commit(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Payment commit started.");
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Payment committed successfully.");
    return true;
}

void payment_rollback(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Payment rollback executed.");
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
}

// Order Service Functions
bool order_prepare(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Order prepare started.");
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Order prepared successfully.");
    return true;
}

bool order_commit(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Order commit started.");
    // Simulate partial failure during commit if requested for order service.
    if (txn.simulate_partial_failure) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        log_event("Transaction " + std::to_string(txn.transaction_id) + ": Order commit simulated failure.");
        return false;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Order committed successfully.");
    return true;
}

void order_rollback(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Order rollback executed.");
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
}

bool process_transaction(Transaction& txn) {
    log_event("Transaction " + std::to_string(txn.transaction_id) + ": Processing started.");

    bool inventoryPrepared = inventory_prepare(txn);
    bool paymentPrepared = false;
    bool orderPrepared = false;

    if (inventoryPrepared) {
        paymentPrepared = payment_prepare(txn);
        if (paymentPrepared) {
            orderPrepared = order_prepare(txn);
        }
    }

    // Two-Phase Commit: Prepare Phase failure handling.
    if (!inventoryPrepared || !paymentPrepared || !orderPrepared) {
        log_event("Transaction " + std::to_string(txn.transaction_id) + ": Prepare phase failed, initiating rollback.");
        if (orderPrepared)
            order_rollback(txn);
        if (paymentPrepared)
            payment_rollback(txn);
        if (inventoryPrepared)
            inventory_rollback(txn);
        log_event("Transaction " + std::to_string(txn.transaction_id) + ": Rollback completed.");
        return false;
    }

    // Commit Phase
    bool inventoryCommitted = inventory_commit(txn);
    bool paymentCommitted = payment_commit(txn);
    bool orderCommitted = order_commit(txn);

    if (inventoryCommitted && paymentCommitted && orderCommitted) {
        log_event("Transaction " + std::to_string(txn.transaction_id) + ": Committed successfully.");
        return true;
    } else {
        log_event("Transaction " + std::to_string(txn.transaction_id) + ": Commit phase failure, initiating rollback.");
        // Rollback on commit failure; in a real system, compensating actions would be triggered.
        if (orderCommitted == false)
            order_rollback(txn);
        if (paymentCommitted == false)
            payment_rollback(txn);
        if (inventoryCommitted == false)
            inventory_rollback(txn);
        log_event("Transaction " + std::to_string(txn.transaction_id) + ": Rollback completed after commit failure.");
        return false;
    }
}

}  // namespace distributed_tx