#include "distributed_tx.h"

#include <vector>
#include <algorithm>
#include "catch.hpp"

TEST_CASE("Simple transaction with all shards voting to commit", "[CommitTransaction]") {
    distributed_tx::TransactionCoordinator coordinator(5);  // 5 shards
    
    std::vector<int> shards = {1, 2, 3};
    coordinator.BeginTransaction(101, shards, 50);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 101);
    
    coordinator.Prepare(101, 1, true);
    coordinator.Prepare(101, 2, true);
    coordinator.Prepare(101, 3, true);
    
    REQUIRE(coordinator.CommitTransaction(101) == true);
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == -1);  // No undecided transactions
}

TEST_CASE("Simple transaction with one shard voting to abort", "[CommitTransaction]") {
    distributed_tx::TransactionCoordinator coordinator(5);  // 5 shards
    
    std::vector<int> shards = {1, 2, 3};
    coordinator.BeginTransaction(101, shards, 50);
    
    coordinator.Prepare(101, 1, true);
    coordinator.Prepare(101, 2, false);  // One shard votes to abort
    coordinator.Prepare(101, 3, true);
    
    REQUIRE(coordinator.CommitTransaction(101) == false);  // Transaction should abort
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == -1);  // No undecided transactions
}

TEST_CASE("Transaction with explicit rollback", "[RollbackTransaction]") {
    distributed_tx::TransactionCoordinator coordinator(5);  // 5 shards
    
    std::vector<int> shards = {1, 2, 3};
    coordinator.BeginTransaction(101, shards, 50);
    
    coordinator.Prepare(101, 1, true);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 101);
    
    REQUIRE(coordinator.RollbackTransaction(101) == true);  // Explicit rollback
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == -1);  // No undecided transactions
}

TEST_CASE("GetHeaviestUndecidedTransaction with multiple transactions", "[GetHeaviestUndecidedTransaction]") {
    distributed_tx::TransactionCoordinator coordinator(5);  // 5 shards
    
    std::vector<int> shards1 = {1, 2};
    coordinator.BeginTransaction(101, shards1, 50);
    
    std::vector<int> shards2 = {3, 4};
    coordinator.BeginTransaction(102, shards2, 100);  // Higher weight
    
    std::vector<int> shards3 = {1, 5};
    coordinator.BeginTransaction(103, shards3, 75);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 102);  // Highest weight
    
    coordinator.Prepare(102, 3, true);
    coordinator.Prepare(102, 4, true);
    coordinator.CommitTransaction(102);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 103);  // Now 103 has highest weight
    
    coordinator.Prepare(103, 1, true);
    coordinator.Prepare(103, 5, true);
    coordinator.CommitTransaction(103);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 101);  // Now 101 is the only undecided
}

TEST_CASE("Edge case: prepare calls before BeginTransaction", "[PrepareBeforeBegin]") {
    distributed_tx::TransactionCoordinator coordinator(5);
    
    // Prepare calls before BeginTransaction should be ignored
    coordinator.Prepare(201, 1, true);
    coordinator.Prepare(201, 2, true);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == -1);  // No undecided transactions
    
    std::vector<int> shards = {1, 2};
    coordinator.BeginTransaction(201, shards, 50);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 201);  // Now we have an undecided transaction
    
    // These should still be needed since previous prepares were ignored
    coordinator.Prepare(201, 1, true);
    coordinator.Prepare(201, 2, true);
    
    REQUIRE(coordinator.CommitTransaction(201) == true);
}

TEST_CASE("Edge case: duplicate prepare votes", "[DuplicatePrepare]") {
    distributed_tx::TransactionCoordinator coordinator(5);
    
    std::vector<int> shards = {1, 2, 3};
    coordinator.BeginTransaction(301, shards, 50);
    
    coordinator.Prepare(301, 1, true);
    coordinator.Prepare(301, 2, true);
    coordinator.Prepare(301, 1, false);  // Second vote from shard 1 should be ignored
    
    coordinator.Prepare(301, 3, true);
    
    REQUIRE(coordinator.CommitTransaction(301) == true);  // Should commit based on first votes
}

TEST_CASE("Edge case: duplicate BeginTransaction calls", "[DuplicateBegin]") {
    distributed_tx::TransactionCoordinator coordinator(5);
    
    std::vector<int> shards1 = {1, 2};
    coordinator.BeginTransaction(401, shards1, 50);
    
    // Duplicate BeginTransaction should be ignored
    std::vector<int> shards2 = {3, 4};
    coordinator.BeginTransaction(401, shards2, 100);
    
    coordinator.Prepare(401, 1, true);
    coordinator.Prepare(401, 2, true);
    
    // Should commit with original shards, not the ones from duplicate call
    REQUIRE(coordinator.CommitTransaction(401) == true);
    
    // These prepares should be ignored as they weren't part of the original transaction
    coordinator.Prepare(401, 3, true);
    coordinator.Prepare(401, 4, true);
}

TEST_CASE("Edge case: empty shard list", "[EmptyShards]") {
    distributed_tx::TransactionCoordinator coordinator(5);
    
    std::vector<int> emptyShards;
    coordinator.BeginTransaction(501, emptyShards, 50);
    
    // With no shards, the transaction should be able to commit immediately
    REQUIRE(coordinator.CommitTransaction(501) == true);
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == -1);
}

TEST_CASE("Edge case: non-existent transaction operations", "[NonExistentTx]") {
    distributed_tx::TransactionCoordinator coordinator(5);
    
    // These operations on non-existent transactions should be ignored gracefully
    REQUIRE(coordinator.CommitTransaction(601) == false);
    REQUIRE(coordinator.RollbackTransaction(601) == false);
    coordinator.Prepare(601, 1, true);  // Should not crash
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == -1);
}

TEST_CASE("Edge case: multiple commit/rollback calls", "[MultipleCommitRollback]") {
    distributed_tx::TransactionCoordinator coordinator(5);
    
    std::vector<int> shards = {1, 2};
    coordinator.BeginTransaction(701, shards, 50);
    
    coordinator.Prepare(701, 1, true);
    coordinator.Prepare(701, 2, true);
    
    REQUIRE(coordinator.CommitTransaction(701) == true);
    REQUIRE(coordinator.CommitTransaction(701) == false);  // Second commit should be ignored
    REQUIRE(coordinator.RollbackTransaction(701) == false);  // Rollback after commit should be ignored
}

TEST_CASE("Tiebreaker for GetHeaviestUndecidedTransaction", "[TieBreaker]") {
    distributed_tx::TransactionCoordinator coordinator(5);
    
    std::vector<int> shards1 = {1, 2};
    coordinator.BeginTransaction(801, shards1, 100);
    
    std::vector<int> shards2 = {3, 4};
    coordinator.BeginTransaction(802, shards2, 100);  // Same weight as 801
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 801);  // Lower txID should win
    
    coordinator.Prepare(801, 1, true);
    coordinator.Prepare(801, 2, true);
    coordinator.CommitTransaction(801);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 802);  // Now 802 is the only undecided
}

TEST_CASE("Complex scenario with many transactions", "[ComplexScenario]") {
    distributed_tx::TransactionCoordinator coordinator(10);
    
    for (int i = 1; i <= 100; ++i) {
        std::vector<int> shards;
        for (int j = 1; j <= (i % 10) + 1; ++j) {
            shards.push_back(j);
        }
        coordinator.BeginTransaction(i, shards, i * 10);
    }
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 100);  // Highest weight
    
    // Complete some transactions
    for (int i = 1; i <= 50; ++i) {
        for (int j = 1; j <= (i % 10) + 1; ++j) {
            coordinator.Prepare(i, j, true);
        }
        coordinator.CommitTransaction(i);
    }
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 100);  // Still highest weight
    
    // Complete transaction 100
    for (int j = 1; j <= (100 % 10) + 1; ++j) {
        coordinator.Prepare(100, j, true);
    }
    coordinator.CommitTransaction(100);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 99);  // Now 99 is highest
}

TEST_CASE("Stress test with large number of shards", "[StressTest]") {
    distributed_tx::TransactionCoordinator coordinator(1000);
    
    std::vector<int> manyShards;
    for (int i = 1; i <= 1000; ++i) {
        manyShards.push_back(i);
    }
    
    coordinator.BeginTransaction(9001, manyShards, 5000);
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 9001);
    
    // Have half of the shards vote to commit
    for (int i = 1; i <= 500; ++i) {
        coordinator.Prepare(9001, i, true);
    }
    
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == 9001);  // Still undecided
    
    // Have one shard vote to abort
    coordinator.Prepare(9001, 501, false);
    
    // Finish the remaining votes
    for (int i = 502; i <= 1000; ++i) {
        coordinator.Prepare(9001, i, true);
    }
    
    REQUIRE(coordinator.CommitTransaction(9001) == false);  // Should abort due to one negative vote
    REQUIRE(coordinator.GetHeaviestUndecidedTransaction() == -1);
}