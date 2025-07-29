#include "catch.hpp"
#include <thread>
#include <vector>
#include <chrono>
#include <mutex>
#include <atomic>
#include "distributed_tx.h"  // Assume the main implementation header is provided

using namespace distributed_tx;

// Helper function to create a transaction that should commit.
// All operations are normal and should result in a commit.
std::vector<Operation> createCommitTransactionOperations() {
    return {
        {1, "write", "key1", "value1"},
        {2, "write", "key2", "value2"},
        {3, "write", "key3", "value3"}
    };
}

// Helper function to create a transaction that should abort.
// One of the operations is flagged to force an abort (for instance, a special key "abort")
std::vector<Operation> createAbortTransactionOperations() {
    return {
        {1, "write", "key1", "value1"},
        {2, "write", "abort", "value2"},  // This operation will force shard 2 to vote abort.
        {3, "write", "key3", "value3"}
    };
}

// Helper function to create a transaction that will timeout.
// One of the operations is flagged to simulate a non-responsive shard (using key 'timeout')
std::vector<Operation> createTimeoutTransactionOperations() {
    return {
        {1, "write", "key1", "value1"},
        {99, "write", "timeout", "value_timeout"},  // Shard 99 will simulate non-response.
        {3, "write", "key3", "value3"}
    };
}

TEST_CASE("Successful Transaction Commit") {
    TransactionCoordinator coordinator;
    // Create a transaction with typical commit operations
    auto ops = createCommitTransactionOperations();
    bool result = coordinator.submitTransaction(ops);
    // Expect the transaction to commit successfully
    REQUIRE(result == true);
}

TEST_CASE("Transaction Abort due to Shard Vote") {
    TransactionCoordinator coordinator;
    auto ops = createAbortTransactionOperations();
    bool result = coordinator.submitTransaction(ops);
    // Expect the transaction to abort due to one shard voting abort.
    REQUIRE(result == false);
}

TEST_CASE("Transaction Rollback on Timeout") {
    TransactionCoordinator coordinator;
    auto ops = createTimeoutTransactionOperations();
    // Use a timeout value shorter than the simulated delay to trigger timeout behavior.
    bool result = coordinator.submitTransaction(ops, std::chrono::milliseconds(100));
    // Expect the transaction to rollback because one shard did not respond in time.
    REQUIRE(result == false);
}

TEST_CASE("Concurrent Transactions") {
    TransactionCoordinator coordinator;

    const int numTransactions = 50;
    std::vector<std::thread> threads;
    std::mutex resMutex;
    std::vector<bool> results;
    results.resize(numTransactions);

    // Launch a mix of commit and abort transactions concurrently.
    for (int i = 0; i < numTransactions; i++) {
        threads.emplace_back([i, &coordinator, &results]() {
            std::vector<Operation> ops;
            // Even-indexed transactions commit; odd-indexed transactions abort.
            if (i % 2 == 0) {
                ops = createCommitTransactionOperations();
            } else {
                ops = createAbortTransactionOperations();
            }
            // Use default timeout for each
            bool res = coordinator.submitTransaction(ops);
            results[i] = res;
        });
    }
    for (auto &t : threads) {
        t.join();
    }
    
    // Verify results: even indices should be true; odd indices should be false.
    for (int i = 0; i < numTransactions; i++) {
        if (i % 2 == 0) {
            REQUIRE(results[i] == true);
        } else {
            REQUIRE(results[i] == false);
        }
    }
}

TEST_CASE("Idempotency of Shard Operations") {
    TransactionCoordinator coordinator;
    auto ops = createCommitTransactionOperations();
    
    // Submit the same transaction twice. The operations should be processed idempotently.
    bool firstResult = coordinator.submitTransaction(ops);
    bool secondResult = coordinator.submitTransaction(ops);
    
    // Both should succeed independently and without causing unintended side effects.
    REQUIRE(firstResult == true);
    REQUIRE(secondResult == true);
}

TEST_CASE("Durability and Log Recovery") {
    // This test simulates a scenario where the TransactionCoordinator crashes after the prepare phase.
    // The shards should use their WAL to recover the transaction state.
    // For simulation, we assume that "recoverTransaction" can be called on the coordinator.
    TransactionCoordinator coordinator;
    auto ops = createCommitTransactionOperations();
    
    // Start a transaction and simulate a crash mid-transaction.
    // submitTransactionWithCrash simulates a crash by returning an indeterminate state.
    bool initialResult = coordinator.submitTransactionWithCrash(ops);
    // After simulating recovery, recoverTransaction should complete the final commit or rollback.
    bool recoveredResult = coordinator.recoverTransaction();
    
    // If the transaction was in-flight and all shards voted to commit, recovery should finish committing.
    // Otherwise, it should rollback. For this test, we assume a successful commit.
    REQUIRE(initialResult == false); // The initial call did not complete the transaction.
    REQUIRE(recoveredResult == true);
}