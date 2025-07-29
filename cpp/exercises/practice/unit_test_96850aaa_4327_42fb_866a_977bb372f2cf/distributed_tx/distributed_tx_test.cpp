#include "distributed_tx.h"
#include "catch.hpp"
#include <vector>

// The following tests assume that the solution provides the following structures and function:
// struct Transfer { int source_node; int destination_node; int amount; };
// struct Transaction { std::vector<Transfer> transfers; };
// struct PartitionEvent { int start_time; int end_time; std::vector<int> affected_nodes; };
// struct FailureEvent { int time; int node_id; };
// and the simulation API:
// std::vector<int> simulate_transactions(
//     int n,
//     const std::vector<int>& initial_assets,
//     const std::vector<Transaction>& transactions,
//     const std::vector<PartitionEvent>& partitions,
//     const std::vector<FailureEvent>& failure_events,
//     int timeout
// );
//
// The tests cover multiple scenarios including simple transaction, concurrent transactions,
// network partitions causing transaction aborts, node failures, and mixed fault events.

TEST_CASE("Single transaction without faults") {
    int n = 2;
    std::vector<int> initial_assets = {100, 50};
    // One transaction: transfer 30 from node0 to node1.
    distributed_tx::Transaction txn;
    txn.transfers.push_back({0, 1, 30});
    std::vector<distributed_tx::Transaction> transactions = { txn };
    std::vector<distributed_tx::PartitionEvent> partitions; // no partition events
    std::vector<distributed_tx::FailureEvent> failure_events; // no failure events
    int timeout = 20;
    
    std::vector<int> final_assets = distributed_tx::simulate_transactions(n, initial_assets, transactions, partitions, failure_events, timeout);
    
    // Expect assets to be updated: node0 70, node1 80.
    std::vector<int> expected = {70, 80};
    REQUIRE(final_assets == expected);
}

TEST_CASE("Multiple concurrent transactions without faults") {
    int n = 3;
    std::vector<int> initial_assets = {100, 100, 100};
    // Transaction 1: transfer 50 from node0 to node1.
    distributed_tx::Transaction txn1;
    txn1.transfers.push_back({0, 1, 50});
    // Transaction 2: transfer 30 from node2 to node1.
    distributed_tx::Transaction txn2;
    txn2.transfers.push_back({2, 1, 30});
    // Transaction 3: transfer 20 from node1 to node0.
    distributed_tx::Transaction txn3;
    txn3.transfers.push_back({1, 0, 20});
    std::vector<distributed_tx::Transaction> transactions = { txn1, txn2, txn3 };
    std::vector<distributed_tx::PartitionEvent> partitions; // no partitions
    std::vector<distributed_tx::FailureEvent> failure_events; // no failures
    int timeout = 30;
    
    std::vector<int> final_assets = distributed_tx::simulate_transactions(n, initial_assets, transactions, partitions, failure_events, timeout);
    
    // Expected:
    // node0: 100 - 50 (txn1) + 20 (txn3) = 70
    // node1: 100 + 50 (txn1) + 30 (txn2) - 20 (txn3) = 160
    // node2: 100 - 30 (txn2) = 70
    std::vector<int> expected = {70, 160, 70};
    REQUIRE(final_assets == expected);
}

TEST_CASE("Transaction aborted due to network partition") {
    int n = 2;
    std::vector<int> initial_assets = {100, 100};
    // One transaction: transfer 40 from node0 to node1.
    distributed_tx::Transaction txn;
    txn.transfers.push_back({0, 1, 40});
    std::vector<distributed_tx::Transaction> transactions = { txn };
    // Create a partition event isolating node1 for a time period that covers the transaction execution.
    std::vector<distributed_tx::PartitionEvent> partitions = {
        {0, 100, {1}}
    };
    std::vector<distributed_tx::FailureEvent> failure_events; // no failures
    int timeout = 50;
    
    std::vector<int> final_assets = distributed_tx::simulate_transactions(n, initial_assets, transactions, partitions, failure_events, timeout);
    
    // Expect transaction to abort due to communication failure between node0 (coordinator) and node1.
    // Assets should remain unchanged.
    std::vector<int> expected = {100, 100};
    REQUIRE(final_assets == expected);
}

TEST_CASE("Transaction aborted due to node failure") {
    int n = 2;
    std::vector<int> initial_assets = {200, 50};
    // One transaction: transfer 150 from node0 to node1.
    distributed_tx::Transaction txn;
    txn.transfers.push_back({0, 1, 150});
    std::vector<distributed_tx::Transaction> transactions = { txn };
    std::vector<distributed_tx::PartitionEvent> partitions; // no partitions
    // Simulate node failure of the coordinator (assuming node0 is coordinator) during the transaction.
    std::vector<distributed_tx::FailureEvent> failure_events = {
        {10, 0}
    };
    int timeout = 40;
    
    std::vector<int> final_assets = distributed_tx::simulate_transactions(n, initial_assets, transactions, partitions, failure_events, timeout);
    
    // Expect transaction to abort due to node failure.
    std::vector<int> expected = {200, 50};
    REQUIRE(final_assets == expected);
}

TEST_CASE("Mixed scenario: multiple transactions with partitions and failures") {
    int n = 4;
    std::vector<int> initial_assets = {300, 200, 150, 100};
    
    // Transaction 1: transfer 100 from node0 to node1.
    distributed_tx::Transaction txn1;
    txn1.transfers.push_back({0, 1, 100});
    // Transaction 2: transfer 50 from node2 to node3.
    distributed_tx::Transaction txn2;
    txn2.transfers.push_back({2, 3, 50});
    // Transaction 3: transfer 70 from node1 to node2.
    distributed_tx::Transaction txn3;
    txn3.transfers.push_back({1, 2, 70});
    // Transaction 4: transfer 30 from node3 to node0.
    distributed_tx::Transaction txn4;
    txn4.transfers.push_back({3, 0, 30});
    std::vector<distributed_tx::Transaction> transactions = { txn1, txn2, txn3, txn4 };
    
    // Partition event isolating node2 from time 5 to 25.
    std::vector<distributed_tx::PartitionEvent> partitions = {
        {5, 25, {2}}
    };
    
    // Failure events: node1 fails at time 15.
    std::vector<distributed_tx::FailureEvent> failure_events = {
        {15, 1}
    };
    
    int timeout = 50;
    
    std::vector<int> final_assets = distributed_tx::simulate_transactions(n, initial_assets, transactions, partitions, failure_events, timeout);
    
    // Analysis of expected values:
    // Transaction 1: Ideally, node0->node1: 300-100, 200+100.
    // Transaction 2: Ideally, node2->node3: 150-50, 100+50.
    // Transaction 3: May be aborted due to node2 partition and/or node1 failure.
    // Transaction 4: Ideally, node3->node0: (if txn2 succeeded and txn3 aborted): node3: 150-30, node0: (200+30) etc.
    // Since transactions are executed concurrently with faults, assume that transactions 1,2,4 succeed and transaction 3 aborts.
    // Then final:
    // node0: 300 - 100 (txn1) + 30 (txn4) = 230
    // node1: 200 + 100 (txn1) = 300
    // node2: 150 - 50 (txn2) = 100
    // node3: 100 + 50 (txn2) - 30 (txn4) = 120
    std::vector<int> expected = {230, 300, 100, 120};
    REQUIRE(final_assets == expected);
}