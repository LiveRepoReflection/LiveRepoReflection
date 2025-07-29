#include <vector>
#include <cstdint>
#include <algorithm>
#include "catch.hpp"
#include "tx_ordering.h"

using namespace std;
using namespace tx_ordering;

// Helper function to check that in the output order, transactions from the same node appear in increasing order of txID.
void check_causal_ordering(const vector<TransactionProposal>& proposals,
                           const vector<uint64_t>& orderedIDs) {
    // Map nodeID -> vector of txIDs in the order they were submitted.
    // We assume that txIDs encode the ordering for a given node (i.e., lower means earlier)
    // Create a map from nodeID to expected ordering (extracted from proposals, sorted by txID)
    vector<TransactionProposal> copy = proposals;
    // Sort proposals within each node by txID to get expected ordering.
    sort(copy.begin(), copy.end(), [](const TransactionProposal &a, const TransactionProposal &b) {
        if (a.nodeID != b.nodeID)
            return a.nodeID < b.nodeID;
        return a.txID < b.txID;
    });
    
    // For each node, extract expected ordering.
    // Then, verify that in the global ordering the relative order of these txIDs is preserved.
    // For simplicity, iterate over nodes 0-255.
    for (uint8_t node = 0; node < 255; ++node) {
        vector<uint64_t> expected;
        for (const auto& p : copy) {
            if (p.nodeID == node)
                expected.push_back(p.txID);
        }
        if (expected.empty())
            continue;
        // Extract indices in orderedIDs where these txIDs appear.
        size_t lastIndex = 0;
        bool firstFound = false;
        for (uint64_t tx : expected) {
            auto it = find(orderedIDs.begin(), orderedIDs.end(), tx);
            REQUIRE(it != orderedIDs.end());
            size_t index = distance(orderedIDs.begin(), it);
            if (firstFound) {
                REQUIRE(index > lastIndex);
            }
            lastIndex = index;
            firstFound = true;
        }
    }
}

TEST_CASE("Single Transaction") {
    vector<TransactionProposal> proposals;
    TransactionProposal t;
    t.txID = 1001;
    t.nodeID = 1;
    t.dataItems = {2001, 3001};
    t.duration = 50;
    t.readOnly = false;
    proposals.push_back(t);

    vector<uint64_t> ordered = orderTransactions(proposals);
    
    // Expect only one transaction in the output
    REQUIRE(ordered.size() == 1);
    REQUIRE(ordered[0] == 1001);
}

TEST_CASE("Multiple In-Order Transactions Same Node") {
    vector<TransactionProposal> proposals;
    // Simulate transactions from node 5 in proper order
    for (uint64_t seq = 1; seq <= 5; seq++) {
        TransactionProposal t;
        // Encode txID: for simplicity, assume txID = (nodeID << 32) | seq
        t.txID = (static_cast<uint64_t>(5) << 32) | seq;
        t.nodeID = 5;
        t.dataItems = {100 + seq}; // distinct data items to avoid conflicts
        t.duration = 20;
        t.readOnly = false;
        proposals.push_back(t);
    }

    vector<uint64_t> ordered = orderTransactions(proposals);

    // Check that all transactions are present and in same relative order as submitted.
    REQUIRE(ordered.size() == proposals.size());
    for (size_t i = 0; i < proposals.size(); i++) {
        REQUIRE(ordered[i] == proposals[i].txID);
    }
}

TEST_CASE("Out-of-Order Arrival from Multiple Nodes") {
    vector<TransactionProposal> proposals;
    // Transactions from node 3 and node 7, inserted in unsorted order.
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(7) << 32) | 2; // node 7, seq 2
        t.nodeID = 7;
        t.dataItems = {5002};
        t.duration = 30;
        t.readOnly = false;
        proposals.push_back(t);
    }
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(3) << 32) | 1; // node 3, seq 1
        t.nodeID = 3;
        t.dataItems = {3001};
        t.duration = 40;
        t.readOnly = false;
        proposals.push_back(t);
    }
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(7) << 32) | 1; // node 7, seq 1
        t.nodeID = 7;
        t.dataItems = {5001};
        t.duration = 25;
        t.readOnly = false;
        proposals.push_back(t);
    }
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(3) << 32) | 2; // node 3, seq 2
        t.nodeID = 3;
        t.dataItems = {3002};
        t.duration = 35;
        t.readOnly = false;
        proposals.push_back(t);
    }

    vector<uint64_t> ordered = orderTransactions(proposals);

    // Ensure that the total number of transactions match.
    REQUIRE(ordered.size() == proposals.size());
    // Check causal ordering for each node.
    check_causal_ordering(proposals, ordered);
}

TEST_CASE("Conflict Resolution Ordering") {
    vector<TransactionProposal> proposals;
    // Two transactions that conflict on same data item (data item 777)
    // Assume that transactions with lower txID should appear earlier.
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(2) << 32) | 3; // node 2, seq 3
        t.nodeID = 2;
        t.dataItems = {777, 888};
        t.duration = 60;
        t.readOnly = false;
        proposals.push_back(t);
    }
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(4) << 32) | 1; // node 4, seq 1
        t.nodeID = 4;
        t.dataItems = {777}; // conflict: same data item as above
        t.duration = 45;
        t.readOnly = false;
        proposals.push_back(t);
    }
    // Add a non-conflicting transaction to ensure it can be interleaved.
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(2) << 32) | 4; // node 2, seq 4
        t.nodeID = 2;
        t.dataItems = {999};
        t.duration = 50;
        t.readOnly = false;
        proposals.push_back(t);
    }

    vector<uint64_t> ordered = orderTransactions(proposals);

    // Check that all transactions are present.
    REQUIRE(ordered.size() == proposals.size());
    // For the conflicting transactions, the one with smaller txID should come before the larger.
    uint64_t txA = (static_cast<uint64_t>(2) << 32) | 3;
    uint64_t txB = (static_cast<uint64_t>(4) << 32) | 1;
    auto posA = find(ordered.begin(), ordered.end(), txA);
    auto posB = find(ordered.begin(), ordered.end(), txB);
    REQUIRE(posA != ordered.end());
    REQUIRE(posB != ordered.end());
    // Determine expected order: if txA's numeric value is lower, then it should appear earlier.
    if (txA < txB) {
        REQUIRE(distance(ordered.begin(), posA) < distance(ordered.begin(), posB));
    } else {
        REQUIRE(distance(ordered.begin(), posB) < distance(ordered.begin(), posA));
    }
    // Check causal ordering is maintained
    check_causal_ordering(proposals, ordered);
}

TEST_CASE("Read-Only Transactions Concurrent Ordering") {
    vector<TransactionProposal> proposals;
    // Two read-only transactions from different nodes but with overlapping data items (should be concurrent)
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(10) << 32) | 1; // node 10, seq 1
        t.nodeID = 10;
        t.dataItems = {1234}; // same data item
        t.duration = 30;
        t.readOnly = true;
        proposals.push_back(t);
    }
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(20) << 32) | 1; // node 20, seq 1
        t.nodeID = 20;
        t.dataItems = {1234}; // same data item but both are read-only
        t.duration = 30;
        t.readOnly = true;
        proposals.push_back(t);
    }
    // Add a write transaction conflicting with one read-only transaction may force ordering.
    {
        TransactionProposal t;
        t.txID = (static_cast<uint64_t>(10) << 32) | 2; // node 10, seq 2
        t.nodeID = 10;
        t.dataItems = {1234};
        t.duration = 40;
        t.readOnly = false;
        proposals.push_back(t);
    }
    
    vector<uint64_t> ordered = orderTransactions(proposals);
    
    // Ensure that the output contains all transactions.
    REQUIRE(ordered.size() == proposals.size());
    // For node 10, txID order must be preserved.
    // That is, the read-only transaction (txID with seq 1) must appear before the write transaction (seq 2)
    uint64_t tx1 = (static_cast<uint64_t>(10) << 32) | 1;
    uint64_t tx2 = (static_cast<uint64_t>(10) << 32) | 2;
    auto pos1 = find(ordered.begin(), ordered.end(), tx1);
    auto pos2 = find(ordered.begin(), ordered.end(), tx2);
    REQUIRE(pos1 != ordered.end());
    REQUIRE(pos2 != ordered.end());
    REQUIRE(distance(ordered.begin(), pos1) < distance(ordered.begin(), pos2));

    // Check overall causal ordering across nodes.
    check_causal_ordering(proposals, ordered);
}