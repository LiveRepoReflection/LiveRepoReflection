#include "tx_coordinator.h"
#include "catch.hpp"
#include <vector>
#include <sstream>
#include <string>

TEST_CASE("Create and track transactions") {
    TransactionCoordinator coordinator;
    
    SECTION("Create a new transaction") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.getTransactionStatus(1) == "PENDING");
    }
    
    SECTION("Create duplicate transaction") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.createTransaction(1) == "ERROR: Transaction 1 already exists");
    }
    
    SECTION("Get status of non-existent transaction") {
        REQUIRE(coordinator.getTransactionStatus(999) == "ERROR: Transaction 999 does not exist");
    }
}

TEST_CASE("Register operations with transactions") {
    TransactionCoordinator coordinator;
    
    SECTION("Register operations with valid transaction") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 10) == "OK");
        REQUIRE(coordinator.registerOperation(1, 101, 1002, 20) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1003, 15) == "OK");
    }
    
    SECTION("Register operation with non-existent transaction") {
        REQUIRE(coordinator.registerOperation(999, 100, 1001, 10) == 
                "ERROR: Transaction 999 does not exist");
    }
    
    SECTION("Register operation with duplicate operation ID on the same node") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 10) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 20) == 
                "ERROR: Operation 1001 already exists for node 100 in transaction 1");
    }
    
    SECTION("Register operation with negative cost") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, -10) == 
                "ERROR: Cost must be positive");
    }
}

TEST_CASE("Critical node identification") {
    TransactionCoordinator coordinator;
    
    SECTION("Single node is critical") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 10) == "OK");
        REQUIRE(coordinator.getCriticalNode(1) == "100");
    }
    
    SECTION("Node with highest total cost is critical") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 10) == "OK");
        REQUIRE(coordinator.registerOperation(1, 200, 2001, 15) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1002, 20) == "OK");
        REQUIRE(coordinator.getCriticalNode(1) == "100"); // 100 has total cost 30, 200 has 15
    }
    
    SECTION("Node with lowest ID is critical when costs are equal") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.registerOperation(1, 200, 2001, 10) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 10) == "OK");
        REQUIRE(coordinator.getCriticalNode(1) == "100"); // Both have cost 10, but 100 < 200
    }
    
    SECTION("Critical node for non-existent transaction") {
        REQUIRE(coordinator.getCriticalNode(999) == "ERROR: Transaction 999 does not exist");
    }
    
    SECTION("Critical node for transaction with no operations") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.getCriticalNode(1) == "ERROR: Transaction 1 has no operations");
    }
}

TEST_CASE("Two-Phase Commit Protocol") {
    TransactionCoordinator coordinator;
    
    SECTION("Prepare and commit a transaction") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 10) == "OK");
        REQUIRE(coordinator.registerOperation(1, 200, 2001, 15) == "OK");
        
        REQUIRE(coordinator.prepareTransaction(1) == "OK");
        REQUIRE(coordinator.getTransactionStatus(1) == "COMMITTED");
    }
    
    SECTION("Cannot prepare non-existent transaction") {
        REQUIRE(coordinator.prepareTransaction(999) == "ERROR: Transaction 999 does not exist");
    }
    
    SECTION("Cannot prepare transaction with no operations") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.prepareTransaction(1) == "ERROR: Transaction 1 has no operations");
    }
    
    SECTION("Cannot prepare already committed transaction") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 10) == "OK");
        REQUIRE(coordinator.prepareTransaction(1) == "OK");
        REQUIRE(coordinator.prepareTransaction(1) == "ERROR: Transaction 1 is already COMMITTED");
    }
}

TEST_CASE("Multiple transactions") {
    TransactionCoordinator coordinator;
    
    SECTION("Handle multiple transactions independently") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.createTransaction(2) == "OK");
        
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 10) == "OK");
        REQUIRE(coordinator.registerOperation(2, 100, 2001, 20) == "OK");
        
        REQUIRE(coordinator.prepareTransaction(1) == "OK");
        REQUIRE(coordinator.getTransactionStatus(1) == "COMMITTED");
        REQUIRE(coordinator.getTransactionStatus(2) == "PENDING");
    }
}

TEST_CASE("Large scale stress test") {
    TransactionCoordinator coordinator;
    
    SECTION("Handle many operations across many nodes") {
        for(int tx = 1; tx <= 10; tx++) {
            REQUIRE(coordinator.createTransaction(tx) == "OK");
            
            for(int node = 100; node <= 150; node++) {
                for(int op = 1; op <= 50; op++) {
                    int opId = node * 1000 + op;
                    REQUIRE(coordinator.registerOperation(tx, node, opId, op) == "OK");
                }
            }
            
            REQUIRE(coordinator.prepareTransaction(tx) == "OK");
            REQUIRE(coordinator.getTransactionStatus(tx) == "COMMITTED");
        }
    }
}

TEST_CASE("Edge cases") {
    TransactionCoordinator coordinator;
    
    SECTION("Register operation to transaction that's already committed") {
        REQUIRE(coordinator.createTransaction(1) == "OK");
        REQUIRE(coordinator.registerOperation(1, 100, 1001, 10) == "OK");
        REQUIRE(coordinator.prepareTransaction(1) == "OK");
        
        REQUIRE(coordinator.registerOperation(1, 100, 1002, 20) == 
                "ERROR: Cannot modify committed transaction 1");
    }
    
    SECTION("Maximum values for IDs and costs") {
        int maxId = std::numeric_limits<int>::max();
        
        REQUIRE(coordinator.createTransaction(maxId) == "OK");
        REQUIRE(coordinator.registerOperation(maxId, maxId, maxId, maxId) == "OK");
        REQUIRE(coordinator.prepareTransaction(maxId) == "OK");
        REQUIRE(coordinator.getTransactionStatus(maxId) == "COMMITTED");
    }
}

TEST_CASE("Command interface parsing") {
    TransactionCoordinator coordinator;
    
    SECTION("Parse and execute valid commands") {
        std::vector<std::string> commands = {
            "CREATE_TRANSACTION 1",
            "REGISTER_OPERATION 1 100 1001 10",
            "GET_CRITICAL_NODE 1",
            "PREPARE 1",
            "GET_STATUS 1"
        };
        
        std::vector<std::string> expected = {
            "OK",
            "OK",
            "100",
            "OK",
            "COMMITTED"
        };
        
        for(size_t i = 0; i < commands.size(); i++) {
            REQUIRE(coordinator.executeCommand(commands[i]) == expected[i]);
        }
    }
    
    SECTION("Handle invalid commands") {
        std::vector<std::string> commands = {
            "UNKNOWN_COMMAND",
            "CREATE_TRANSACTION",
            "REGISTER_OPERATION 1",
            "PREPARE"
        };
        
        for(const auto& cmd : commands) {
            REQUIRE(coordinator.executeCommand(cmd).find("ERROR: Invalid command") == 0);
        }
    }
}