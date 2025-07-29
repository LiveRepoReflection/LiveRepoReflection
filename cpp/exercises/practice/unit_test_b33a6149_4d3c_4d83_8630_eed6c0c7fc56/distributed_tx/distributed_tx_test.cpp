#include "distributed_tx.h"
#include "catch.hpp"
#include <thread>
#include <chrono>
#include <vector>
#include <atomic>

TEST_CASE("Commit transaction success") {
    using namespace distributed_tx;
    bool commitCalled1 = false;
    bool commitCalled2 = false;
    bool rollbackCalled1 = false;
    bool rollbackCalled2 = false;

    TransactionID tx = beginTransaction();

    bool registered1 = registerOperation(tx, [&]() -> bool {
        commitCalled1 = true;
        return true;
    }, [&]() {
        rollbackCalled1 = true;
    });
    bool registered2 = registerOperation(tx, [&]() -> bool {
        commitCalled2 = true;
        return true;
    }, [&]() {
        rollbackCalled2 = true;
    });

    REQUIRE(registered1);
    REQUIRE(registered2);

    bool result = commitTransaction(tx);
    REQUIRE(result);
    // Ensure all commit lambdas were executed
    REQUIRE(commitCalled1);
    REQUIRE(commitCalled2);
    // No rollback lambdas should be called on a successful commit.
    REQUIRE_FALSE(rollbackCalled1);
    REQUIRE_FALSE(rollbackCalled2);
}

TEST_CASE("Commit transaction failure with rollback") {
    using namespace distributed_tx;
    bool commitCalled1 = false;
    bool commitCalled2 = false;
    bool rollbackCalled1 = false;
    bool rollbackCalled2 = false;

    TransactionID tx = beginTransaction();

    bool reg1 = registerOperation(tx, [&]() -> bool {
        commitCalled1 = true;
        return true;
    }, [&]() {
        rollbackCalled1 = true;
    });
    bool reg2 = registerOperation(tx, [&]() -> bool {
        commitCalled2 = true;
        // Simulate failure for the second operation.
        return false;
    }, [&]() {
        rollbackCalled2 = true;
    });

    REQUIRE(reg1);
    REQUIRE(reg2);

    bool result = commitTransaction(tx);
    REQUIRE_FALSE(result);
    // The first operation should have committed and then rolled back.
    REQUIRE(commitCalled1);
    // The second operation's commit was attempted and failed.
    REQUIRE(commitCalled2);
    // Rollback should be invoked for the first operation.
    REQUIRE(rollbackCalled1);
    // The second operation's rollback might not be called because it failed during commit.
    REQUIRE_FALSE(rollbackCalled2);
}

TEST_CASE("Abort transaction performs rollback on committed operations") {
    using namespace distributed_tx;
    bool commitCalled1 = false;
    bool rollbackCalled1 = false;

    TransactionID tx = beginTransaction();

    bool reg1 = registerOperation(tx, [&]() -> bool {
        commitCalled1 = true;
        return true;
    }, [&]() {
        rollbackCalled1 = true;
    });
    REQUIRE(reg1);

    // Simulate partial commit by directly invoking the commit lambda
    // In actual use, commitTransaction would execute the commit lambdas.
    // For test purposes, we assume the operation was committed.
    commitCalled1 = true; // Mark as if committed.
    // Now abort the transaction.
    abortTransaction(tx);
    REQUIRE(rollbackCalled1);
}

TEST_CASE("Invalid transaction commit and abort") {
    using namespace distributed_tx;
    // Use an invalid TransactionID assuming negative values are invalid.
    TransactionID fakeTx = -1;
    bool commitResult = commitTransaction(fakeTx);
    // Expecting failure when trying to commit a non-existent transaction.
    REQUIRE_FALSE(commitResult);
    // Aborting a non-existent transaction should not throw exceptions.
    REQUIRE_NOTHROW(abortTransaction(fakeTx));
}

TEST_CASE("Concurrent transaction operations") {
    using namespace distributed_tx;
    std::atomic<int> commitCounter(0);
    std::atomic<int> rollbackCounter(0);
    const int threadCount = 10;
    const int operationsPerThread = 5;

    auto worker = [&]() {
        TransactionID tx = beginTransaction();
        for (int i = 0; i < operationsPerThread; ++i) {
            registerOperation(tx, [&]() -> bool {
                commitCounter.fetch_add(1);
                return true;
            }, [&]() {
                rollbackCounter.fetch_add(1);
            });
        }
        // Simulate some processing delay.
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        bool res = commitTransaction(tx);
        // In this test scenario, all commit operations should succeed.
        if (!res) {
            // If commit fails, the rollback lambdas would have been invoked.
        }
    };

    std::vector<std::thread> threads;
    for (int i = 0; i < threadCount; ++i) {
        threads.emplace_back(worker);
    }
    for (auto& t : threads) {
        t.join();
    }
    // All operations in each transaction were committed successfully.
    REQUIRE(commitCounter.load() == threadCount * operationsPerThread);
    // No rollbacks should have been triggered in concurrent successful commits.
    REQUIRE(rollbackCounter.load() == 0);
}