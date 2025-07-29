#include "catch.hpp"
#include "distributed_tx.h"
#include <sstream>
#include <iostream>
#include <string>

// Helper function to run the DTC simulation with given input and capture output.
std::string runSimulation(const std::string &input) {
    std::istringstream iss(input);
    std::ostringstream oss;
    // Assume the distributed_tx::run function reads from an input stream and writes to an output stream.
    distributed_tx::run(iss, oss);
    return oss.str();
}

TEST_CASE("Commit Transaction - All Nodes Vote Commit", "[distributed_tx]") {
    // Test with a single transaction that should commit.
    // Two nodes; no failures.
    std::string input = "2 1\n"
                        "{\"transaction_id\": 1, \"involved_nodes\": [1, 2], \"operations\": ["
                        "{\"node_id\": 1, \"operation_type\": 1, \"data\": \"data1\"}, "
                        "{\"node_id\": 2, \"operation_type\": 2, \"data\": \"data2\"}"
                        "], \"failed_nodes\": []}\n";
    
    std::string expected = "COMMIT\n"
                           "Node 1: [PREPARED 1, COMMITTED 1]\n"
                           "Node 2: [PREPARED 1, COMMITTED 1]\n";
    
    std::string output = runSimulation(input);
    REQUIRE(output == expected);
}

TEST_CASE("Rollback Transaction - Node Failure in Prepare Phase", "[distributed_tx]") {
    // Test with a transaction that should rollback because one node is marked as failed.
    std::string input = "2 1\n"
                        "{\"transaction_id\": 2, \"involved_nodes\": [1, 2], \"operations\": ["
                        "{\"node_id\": 1, \"operation_type\": 1, \"data\": \"data3\"}, "
                        "{\"node_id\": 2, \"operation_type\": 3, \"data\": \"data4\"}"
                        "], \"failed_nodes\": [2]}\n";
    
    std::string expected = "ROLLBACK\n"
                           "Node 1: [PREPARED 2, ABORTED 2]\n"
                           "Node 2: [PREPARED 2, ABORTED 2]\n";
    
    std::string output = runSimulation(input);
    REQUIRE(output == expected);
}

TEST_CASE("Multiple Transactions with Mixed Outcomes", "[distributed_tx]") {
    // Test with multiple transactions where one commits and one rolls back.
    std::string input = "3 2\n"
                        "{\"transaction_id\": 10, \"involved_nodes\": [1, 2, 3], \"operations\": ["
                        "{\"node_id\": 1, \"operation_type\": 1, \"data\": \"op1\"}, "
                        "{\"node_id\": 2, \"operation_type\": 2, \"data\": \"op2\"}, "
                        "{\"node_id\": 3, \"operation_type\": 1, \"data\": \"op3\"}"
                        "], \"failed_nodes\": []}\n"
                        "{\"transaction_id\": 11, \"involved_nodes\": [1, 3], \"operations\": ["
                        "{\"node_id\": 1, \"operation_type\": 3, \"data\": \"op4\"}, "
                        "{\"node_id\": 3, \"operation_type\": 1, \"data\": \"op5\"}"
                        "], \"failed_nodes\": [3]}\n";
    
    std::string expected = "COMMIT\n"
                           "Node 1: [PREPARED 10, COMMITTED 10]\n"
                           "Node 2: [PREPARED 10, COMMITTED 10]\n"
                           "Node 3: [PREPARED 10, COMMITTED 10]\n"
                           "ROLLBACK\n"
                           "Node 1: [PREPARED 11, ABORTED 11]\n"
                           "Node 3: [PREPARED 11, ABORTED 11]\n";
    
    std::string output = runSimulation(input);
    REQUIRE(output == expected);
}

TEST_CASE("Idempotency Test - Repeat Transaction", "[distributed_tx]") {
    // Test that re-submitting a transaction with the same id returns the stored result and log.
    // First, process a commit transaction.
    std::string input1 = "2 1\n"
                         "{\"transaction_id\": 20, \"involved_nodes\": [1, 2], \"operations\": ["
                         "{\"node_id\": 1, \"operation_type\": 1, \"data\": \"init\"}, "
                         "{\"node_id\": 2, \"operation_type\": 2, \"data\": \"init\"}"
                         "], \"failed_nodes\": []}\n";
    
    std::string expected1 = "COMMIT\n"
                            "Node 1: [PREPARED 20, COMMITTED 20]\n"
                            "Node 2: [PREPARED 20, COMMITTED 20]\n";
    
    std::string output1 = runSimulation(input1);
    REQUIRE(output1 == expected1);

    // Now, re-submit the same transaction.
    std::string input2 = "2 1\n"
                         "{\"transaction_id\": 20, \"involved_nodes\": [1, 2], \"operations\": ["
                         "{\"node_id\": 1, \"operation_type\": 1, \"data\": \"ignored\"}, "
                         "{\"node_id\": 2, \"operation_type\": 2, \"data\": \"ignored\"}"
                         "], \"failed_nodes\": []}\n";
    
    std::string expected2 = expected1;  // Outcome and logs should be identical.
    
    std::string output2 = runSimulation(input2);
    REQUIRE(output2 == expected2);
}

TEST_CASE("Timeout Simulation - Missing Node Response Treated as Abort", "[distributed_tx]") {
    // Simulate a timeout scenario by providing a failed node in the failed_nodes list.
    // For this test, we consider that a timeout is represented by marking the node as failed.
    std::string input = "3 1\n"
                        "{\"transaction_id\": 30, \"involved_nodes\": [1, 2, 3], \"operations\": ["
                        "{\"node_id\": 1, \"operation_type\": 1, \"data\": \"t1\"}, "
                        "{\"node_id\": 2, \"operation_type\": 2, \"data\": \"t2\"}, "
                        "{\"node_id\": 3, \"operation_type\": 3, \"data\": \"t3\"}"
                        "], \"failed_nodes\": [2]}\n";
    
    std::string expected = "ROLLBACK\n"
                           "Node 1: [PREPARED 30, ABORTED 30]\n"
                           "Node 2: [PREPARED 30, ABORTED 30]\n"
                           "Node 3: [PREPARED 30, ABORTED 30]\n";
    
    std::string output = runSimulation(input);
    REQUIRE(output == expected);
}
    
// Main entry point for Catch2
#define CATCH_CONFIG_MAIN
#include "catch.hpp"