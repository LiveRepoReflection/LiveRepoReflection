#include "catch.hpp"
#include "txn_validator.h"
#include <vector>
#include <unordered_map>
#include <string>

TEST_CASE("Simple valid transaction", "[txn_validator]") {
    // 2 resources
    int num_resources = 2;
    
    // Transaction graph: one operation reading resource 0 at version 1, and another reading resource 1 at version 2
    std::vector<Operation> operations = {
        {0, 0, 1, std::nullopt},  // Node 0 reads resource 0 at version 1
        {1, 1, 2, 3}              // Node 1 reads resource 1 at version 2 and writes version 3
    };
    
    std::vector<Dependency> dependencies = {};
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    // Node logs show that operations were executed with correct resource versions
    std::unordered_map<int, std::vector<LogEntry>> node_logs = {
        {0, {{0, 0, 1}}},  // Node 0 executed its operation and saw resource 0 at version 1
        {1, {{1, 1, 2}}}   // Node 1 executed its operation and saw resource 1 at version 2
    };
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "COMMIT");
}

TEST_CASE("Version inconsistency", "[txn_validator]") {
    int num_resources = 1;
    
    std::vector<Operation> operations = {
        {0, 0, 1, 2}  // Node 0 expects resource 0 to be at version 1, will write version 2
    };
    
    std::vector<Dependency> dependencies = {};
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    // Node log shows that when the operation was executed, resource 0 was actually at version 3
    std::unordered_map<int, std::vector<LogEntry>> node_logs = {
        {0, {{0, 0, 3}}}
    };
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "ABORT");
}

TEST_CASE("Cycle in transaction graph", "[txn_validator]") {
    int num_resources = 2;
    
    std::vector<Operation> operations = {
        {0, 0, 1, 2},  // Node 0 operation
        {1, 1, 2, 3}   // Node 1 operation
    };
    
    // Create a cycle: 0 depends on 1, and 1 depends on 0
    std::vector<Dependency> dependencies = {
        {0, 1},
        {1, 0}
    };
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    std::unordered_map<int, std::vector<LogEntry>> node_logs = {
        {0, {{0, 0, 1}}},
        {1, {{1, 1, 2}}}
    };
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "ABORT");
}

TEST_CASE("Incomplete transaction", "[txn_validator]") {
    int num_resources = 3;
    
    std::vector<Operation> operations = {
        {0, 0, 1, 2},  // Node 0 operation
        {1, 1, 2, 3},  // Node 1 operation
        {2, 2, 1, 2}   // Node 2 operation
    };
    
    std::vector<Dependency> dependencies = {};
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    // Only two operations were executed, the third one is missing
    std::unordered_map<int, std::vector<LogEntry>> node_logs = {
        {0, {{0, 0, 1}}},
        {1, {{1, 1, 2}}}
        // Node 2's operation is missing
    };
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "ABORT");
}

TEST_CASE("Operations with dependencies", "[txn_validator]") {
    int num_resources = 3;
    
    std::vector<Operation> operations = {
        {0, 0, 1, 2},  // Node 0 reads resource 0 at version 1, writes version 2
        {1, 1, 2, 3},  // Node 1 reads resource 1 at version 2, writes version 3
        {2, 2, 1, 2},  // Node 2 reads resource 2 at version 1, writes version 2
        {3, 0, 2, 3}   // Node 3 reads resource 0 at version 2 (after Node 0's write), writes version 3
    };
    
    // Node 3 depends on Node 0 (must execute after Node 0)
    std::vector<Dependency> dependencies = {
        {0, 3}
    };
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    // Logs show all operations executed in correct order with expected versions
    std::unordered_map<int, std::vector<LogEntry>> node_logs = {
        {0, {{0, 0, 1}}},
        {1, {{1, 1, 2}}},
        {2, {{2, 2, 1}}},
        {3, {{3, 0, 2}}}  // Node 3 saw resource 0 at version 2, which is correct after Node 0's write
    };
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "COMMIT");
}

TEST_CASE("Dependency violation", "[txn_validator]") {
    int num_resources = 2;
    
    std::vector<Operation> operations = {
        {0, 0, 1, 2},  // Node 0 reads resource 0 at version 1, writes version 2
        {1, 0, 1, 3}   // Node 1 reads resource 0 at version 1, writes version 3
    };
    
    // Node 1 depends on Node 0
    std::vector<Dependency> dependencies = {
        {0, 1}
    };
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    // Logs show Node 1 executed before Node 0's changes were applied
    std::unordered_map<int, std::vector<LogEntry>> node_logs = {
        {1, {{1, 0, 1}}},  // Node 1 saw resource 0 at version 1
        {0, {{0, 0, 1}}}   // Node 0 also saw resource 0 at version 1
    };
    
    // Even though all operations executed successfully, the dependency ordering was violated
    // Node 1 should have seen resource 0 at version 2 after Node 0's write
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "ABORT");
}

TEST_CASE("Complex DAG with multiple dependencies", "[txn_validator]") {
    int num_resources = 4;
    
    std::vector<Operation> operations = {
        {0, 0, 1, 2},    // Node 0 operation
        {1, 1, 1, 2},    // Node 1 operation
        {2, 2, 1, 2},    // Node 2 operation
        {3, 3, 1, 2},    // Node 3 operation
        {4, 0, 2, 3},    // Node 4 depends on Node 0
        {5, 1, 2, 3},    // Node 5 depends on Node 1
        {6, 2, 2, 3},    // Node 6 depends on Node 2
        {7, 3, 2, 3}     // Node 7 depends on Node 3
    };
    
    std::vector<Dependency> dependencies = {
        {0, 4}, {1, 5}, {2, 6}, {3, 7},  // Direct dependencies
        {4, 7}, {5, 7}                   // Additional dependencies
    };
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    // All operations executed with correct versions in an order respecting dependencies
    std::unordered_map<int, std::vector<LogEntry>> node_logs = {
        {0, {{0, 0, 1}}},
        {1, {{1, 1, 1}}},
        {2, {{2, 2, 1}}},
        {3, {{3, 3, 1}}},
        {4, {{4, 0, 2}}},  // Node 4 saw resource 0 at version 2 (after Node 0's write)
        {5, {{5, 1, 2}}},  // Node 5 saw resource 1 at version 2 (after Node 1's write)
        {6, {{6, 2, 2}}},  // Node 6 saw resource 2 at version 2 (after Node 2's write)
        {7, {{7, 3, 2}}}   // Node 7 saw resource 3 at version 2 (after Node 3's write)
    };
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "COMMIT");
}

TEST_CASE("Operations executed in wrong order", "[txn_validator]") {
    int num_resources = 1;
    
    std::vector<Operation> operations = {
        {0, 0, 1, 2},  // Node 0 reads resource 0 at version 1, writes version 2
        {1, 0, 2, 3}   // Node 1 reads resource 0 at version 2 (after Node 0's write), writes version 3
    };
    
    // Node 1 depends on Node 0
    std::vector<Dependency> dependencies = {
        {0, 1}
    };
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    // Logs show both operations executed, but Node 1 didn't see Node 0's change
    std::unordered_map<int, std::vector<LogEntry>> node_logs = {
        {0, {{0, 0, 1}}},
        {1, {{1, 0, 1}}}  // Node 1 saw version 1, but should have seen version 2
    };
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "ABORT");
}

TEST_CASE("Large transaction with multiple read-write patterns", "[txn_validator]") {
    int num_resources = 10;
    
    // Create a complex transaction with multiple operations on each resource
    std::vector<Operation> operations;
    std::vector<Dependency> dependencies;
    
    // Initial read operations
    for (int i = 0; i < num_resources; i++) {
        operations.push_back({i, i, i, i+1});  // Node i reads resource i at version i, writes version i+1
    }
    
    // Second wave operations that depend on first wave
    for (int i = 0; i < num_resources; i++) {
        int node_id = i + num_resources;
        operations.push_back({node_id, i, i+1, i+2});  // Node node_id reads resource i at version i+1, writes version i+2
        dependencies.push_back({i, node_id});  // Depends on first wave operation
    }
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    // Create logs where all operations executed correctly
    std::unordered_map<int, std::vector<LogEntry>> node_logs;
    for (int i = 0; i < num_resources; i++) {
        node_logs[i] = {{i, i, i}};  // First wave operations
        node_logs[i + num_resources] = {{i + num_resources, i, i+1}};  // Second wave operations
    }
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "COMMIT");
    
    // Now modify one log entry to create a version inconsistency
    node_logs[5][0] = {5, 5, 6};  // Node 5 saw resource 5 at version 6, not 5 as expected
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "ABORT");
}

TEST_CASE("Read-only operations", "[txn_validator]") {
    int num_resources = 3;
    
    std::vector<Operation> operations = {
        {0, 0, 1, std::nullopt},  // Node 0 reads resource 0 at version 1 (read-only)
        {1, 1, 2, std::nullopt},  // Node 1 reads resource 1 at version 2 (read-only)
        {2, 2, 3, 4}              // Node 2 reads resource 2 at version 3, writes version 4
    };
    
    std::vector<Dependency> dependencies = {};
    
    TransactionGraph transaction_graph{operations, dependencies};
    
    // All operations executed with correct versions
    std::unordered_map<int, std::vector<LogEntry>> node_logs = {
        {0, {{0, 0, 1}}},
        {1, {{1, 1, 2}}},
        {2, {{2, 2, 3}}}
    };
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "COMMIT");
    
    // Change one read-only operation to see wrong version
    node_logs[0][0] = {0, 0, 2};  // Node 0 saw resource 0 at version 2, not 1 as expected
    
    REQUIRE(validateTransaction(num_resources, transaction_graph, node_logs) == "ABORT");
}