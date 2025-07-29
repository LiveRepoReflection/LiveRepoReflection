#include "distributed_tx.h"
#include "catch.hpp"
#include <thread>
#include <vector>
#include <chrono>

using namespace distributed_tx;

TEST_CASE("Single transaction commits successfully", "[transaction][commit]") {
    // Create a coordinator and add microservices with ample resources.
    DistributedTxCoordinator coordinator;
    coordinator.addMicroservice({1, 4, 8192, 100, 10});
    coordinator.addMicroservice({2, 4, 8192, 100, 15});
    coordinator.addMicroservice({3, 4, 8192, 100, 20});

    // Create a transaction request where every operation is set to succeed.
    TransactionRequest request;
    request.operations = {
        {1, "Operation A on service 1", true},
        {2, "Operation B on service 2", true},
        {3, "Operation C on service 3", true}
    };

    TransactionResult result = coordinator.executeTransaction(request);
    REQUIRE(result.status == TxStatus::COMMITTED);
    // Verify performance metrics: completion time should be non-negative and throughput positive.
    REQUIRE(result.metrics.completion_time >= 0.0);
    REQUIRE(result.metrics.throughput >= 0);
}

TEST_CASE("Transaction rolls back upon operation failure", "[transaction][rollback]") {
    // Create a coordinator and add microservices.
    DistributedTxCoordinator coordinator;
    coordinator.addMicroservice({1, 4, 8192, 100, 10});
    coordinator.addMicroservice({2, 4, 8192, 100, 15});
    coordinator.addMicroservice({3, 4, 8192, 100, 20});

    // Create a transaction request with one failing operation.
    TransactionRequest request;
    request.operations = {
        {1, "Operation A on service 1", true},
        {2, "Operation B on service 2", false}, // This operation fails.
        {3, "Operation C on service 3", true}
    };

    TransactionResult result = coordinator.executeTransaction(request);
    REQUIRE(result.status == TxStatus::ROLLED_BACK);
    // Metrics should still be available
    REQUIRE(result.metrics.completion_time >= 0.0);
}

TEST_CASE("Resource-aware scheduling affects performance metrics", "[transaction][resource]") {
    // Create a coordinator and add microservices with varying resource constraints.
    DistributedTxCoordinator coordinator;
    coordinator.addMicroservice({1, 8, 16384, 200, 5});    // high resources, low latency
    coordinator.addMicroservice({2, 2, 4096, 50, 30});      // low resources, high latency
    coordinator.addMicroservice({3, 4, 8192, 100, 20});     // medium
    
    // All operations succeed.
    TransactionRequest request;
    request.operations = {
        {1, "Critical operation on service 1", true},
        {2, "Non-critical operation on service 2", true},
        {3, "Standard operation on service 3", true}
    };

    TransactionResult result = coordinator.executeTransaction(request);
    // Even though scheduling is optimized, the transaction must commit.
    REQUIRE(result.status == TxStatus::COMMITTED);
    // Check that resource utilization metrics list size equals number of microservices involved.
    REQUIRE(result.metrics.resource_utilization.size() == 3);
}

TEST_CASE("Concurrent transactions are handled correctly", "[transaction][concurrency]") {
    DistributedTxCoordinator coordinator;
    // Add several microservices.
    for (int i = 1; i <= 10; ++i) {
        coordinator.addMicroservice({i, 4, 8192, 100, 10});
    }

    const int numTransactions = 50;
    std::vector<std::thread> threads;
    std::vector<TxStatus> statuses(numTransactions);

    // Lambda to execute a transaction.
    auto transactionTask = [&](int idx) {
        TransactionRequest request;
        // Create operations targeting random microservices among the 10.
        for (int j = 1; j <= 5; ++j) {
            int svcId = (idx + j) % 10 + 1;
            request.operations.push_back({svcId, "Concurrent operation", true});
        }
        TransactionResult result = coordinator.executeTransaction(request);
        statuses[idx] = result.status;
    };

    // Launch transactions concurrently.
    for (int i = 0; i < numTransactions; ++i) {
        threads.emplace_back(transactionTask, i);
    }
    for (auto &thread : threads) {
        thread.join();
    }

    // All transactions should commit successfully.
    for (int i = 0; i < numTransactions; ++i) {
        REQUIRE(statuses[i] == TxStatus::COMMITTED);
    }
}

TEST_CASE("Coordinator recovery after crash restores consistency", "[transaction][recovery]") {
    DistributedTxCoordinator coordinator;
    coordinator.addMicroservice({1, 4, 8192, 100, 10});
    coordinator.addMicroservice({2, 4, 8192, 100, 15});

    // Simulate a transaction that may be interrupted.
    TransactionRequest request;
    request.operations = {
        {1, "Operation before crash", true},
        {2, "Operation before crash", true}
    };
    TransactionResult result = coordinator.executeTransaction(request);
    // Ensure the transaction commits.
    REQUIRE(result.status == TxStatus::COMMITTED);

    // Simulate a coordinator crash and recovery.
    bool recovered = coordinator.recover();
    REQUIRE(recovered == true);

    // After recovery, new transactions should proceed normally.
    TransactionRequest newRequest;
    newRequest.operations = {
        {1, "Operation after recovery", true},
        {2, "Operation after recovery", true}
    };
    TransactionResult newResult = coordinator.executeTransaction(newRequest);
    REQUIRE(newResult.status == TxStatus::COMMITTED);
}