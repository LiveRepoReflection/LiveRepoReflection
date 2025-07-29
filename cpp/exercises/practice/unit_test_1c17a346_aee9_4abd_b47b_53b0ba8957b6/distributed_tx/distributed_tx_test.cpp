#include "catch.hpp"
#include "distributed_tx.h"

#include <thread>
#include <vector>
#include <chrono>
#include <atomic>

// Helper function to create a transaction request for testing.
distributed_tx::TransactionRequest createRequest(const std::string& tid,
                                                   const std::vector<std::string>& services,
                                                   const std::map<std::string, std::string>& serviceData = {}) {
    distributed_tx::TransactionRequest req;
    req.tid = tid;
    req.services = services;
    req.serviceData = serviceData;
    return req;
}

TEST_CASE("Successful Two-Phase Commit Transaction", "[distributed_tx]") {
    // All services return commit vote.
    auto req = createRequest("txn_001",
                             {"Inventory", "Payment", "Order", "Shipping"},
                             { {"Inventory", "reserve_ok"},
                               {"Payment", "charge_ok"},
                               {"Order", "create_ok"},
                               {"Shipping", "schedule_ok"} });
    distributed_tx::TransactionResponse res = distributed_tx::process_transaction(req);
    REQUIRE(res.status == "Commit");
    REQUIRE(res.errorMessage.empty());
}

TEST_CASE("Abort Transaction on Participant Vote Abort", "[distributed_tx]") {
    // Payment service votes abort.
    auto req = createRequest("txn_002",
                             {"Inventory", "Payment", "Order", "Shipping"},
                             { {"Inventory", "reserve_ok"},
                               {"Payment", "fail_charge"},
                               {"Order", "create_ok"},
                               {"Shipping", "schedule_ok"} });
    distributed_tx::TransactionResponse res = distributed_tx::process_transaction(req);
    REQUIRE(res.status == "Rollback");
    REQUIRE(!res.errorMessage.empty());
}

TEST_CASE("Rollback Transaction on Service Unavailability", "[distributed_tx]") {
    // Simulate Inventory service as temporarily unavailable.
    auto req = createRequest("txn_003",
                             {"Inventory", "Payment", "Order", "Shipping"},
                             { {"Inventory", "unavailable"},
                               {"Payment", "charge_ok"},
                               {"Order", "create_ok"},
                               {"Shipping", "schedule_ok"} });
    distributed_tx::TransactionResponse res = distributed_tx::process_transaction(req);
    REQUIRE(res.status == "Rollback");
    REQUIRE(!res.errorMessage.empty());
}

TEST_CASE("Idempotency: Repeated Transaction Execution Yields Same Result", "[distributed_tx]") {
    // The same transaction executed twice should produce the same outcome.
    auto req = createRequest("txn_004",
                             {"Inventory", "Payment", "Order", "Shipping"},
                             { {"Inventory", "reserve_ok"},
                               {"Payment", "charge_ok"},
                               {"Order", "create_ok"},
                               {"Shipping", "schedule_ok"} });
    distributed_tx::TransactionResponse res1 = distributed_tx::process_transaction(req);
    distributed_tx::TransactionResponse res2 = distributed_tx::process_transaction(req);
    // Both executions should commit
    REQUIRE(res1.status == "Commit");
    REQUIRE(res2.status == "Commit");
}

TEST_CASE("Concurrent Transactions Processing", "[distributed_tx]") {
    std::atomic<int> commitCount(0);
    std::atomic<int> rollbackCount(0);
    const int numTransactions = 20;
    std::vector<std::thread> threads;
    
    for (int i = 0; i < numTransactions; i++) {
        threads.emplace_back([i, &commitCount, &rollbackCount]() {
            std::string tid = "txn_concurrent_" + std::to_string(i);
            std::vector<std::string> services = {"Inventory", "Payment", "Order", "Shipping"};
            std::map<std::string, std::string> data;
            // For even-indexed transactions, simulate a commit, otherwise simulate failure in one service.
            if (i % 2 == 0) {
                data = { {"Inventory", "reserve_ok"},
                         {"Payment", "charge_ok"},
                         {"Order", "create_ok"},
                         {"Shipping", "schedule_ok"} };
            } else {
                data = { {"Inventory", "reserve_ok"},
                         {"Payment", "fail_charge"},
                         {"Order", "create_ok"},
                         {"Shipping", "schedule_ok"} };
            }
            auto req = createRequest(tid, services, data);
            distributed_tx::TransactionResponse res = distributed_tx::process_transaction(req);
            if (res.status == "Commit") {
                commitCount++;
            } else {
                rollbackCount++;
            }
        });
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    // Verify that we have expected counts.
    REQUIRE(commitCount == numTransactions / 2);
    REQUIRE(rollbackCount == numTransactions / 2);
}

TEST_CASE("Recovery Simulation: Completing In-Flight Transaction After DTM Failure", "[distributed_tx]") {
    // Simulate a scenario where the DTM recovers and must complete a pending transaction.
    // First, we simulate the logging of an in-flight transaction.
    auto req = createRequest("txn_recovery",
                             {"Inventory", "Payment", "Order", "Shipping"},
                             { {"Inventory", "reserve_ok"},
                               {"Payment", "charge_ok"},
                               {"Order", "create_ok"},
                               {"Shipping", "schedule_ok"} });
    // Assume process_transaction logs the transaction but interrupts before final commit.
    distributed_tx::TransactionResponse interimRes = distributed_tx::process_transaction(req);
    
    // Simulate DTM recovery process.
    distributed_tx::recover_incomplete_transactions();
    
    // After recovery, querying the transaction status should yield final resolution.
    distributed_tx::TransactionResponse finalRes = distributed_tx::query_transaction_status("txn_recovery");
    REQUIRE(finalRes.status == "Commit");
}
