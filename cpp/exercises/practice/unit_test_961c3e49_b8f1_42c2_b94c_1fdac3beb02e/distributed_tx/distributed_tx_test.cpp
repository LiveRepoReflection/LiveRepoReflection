#include <sstream>
#include <string>
#include <thread>
#include <vector>
#include "catch.hpp"
#include "distributed_tx.h"

class MockCoordinator : public TransactionCoordinator {
public:
    std::vector<std::string> output;
    
    void processOutput(const std::string& msg) override {
        output.push_back(msg);
    }
};

TEST_CASE("Basic successful transaction") {
    MockCoordinator coordinator;
    
    coordinator.processCommand("BEGIN 1 1 2");
    coordinator.processCommand("PREPARED 1 1");
    coordinator.processCommand("PREPARED 1 2");
    
    REQUIRE(coordinator.output.size() >= 4);
    REQUIRE(coordinator.output[0] == "PREPARE 1 1");
    REQUIRE(coordinator.output[1] == "PREPARE 1 2");
    REQUIRE(coordinator.output[2] == "COMMIT 1 1");
    REQUIRE(coordinator.output[3] == "COMMIT 1 2");
    REQUIRE(coordinator.output.back() == "TRANSACTION_COMMITTED 1");
}

TEST_CASE("Transaction with abort") {
    MockCoordinator coordinator;
    
    coordinator.processCommand("BEGIN 2 1 2 3");
    coordinator.processCommand("PREPARED 2 1");
    coordinator.processCommand("ABORT 2 2");
    
    REQUIRE(coordinator.output.size() >= 5);
    REQUIRE(coordinator.output[0] == "PREPARE 2 1");
    REQUIRE(coordinator.output[1] == "PREPARE 2 2");
    REQUIRE(coordinator.output[2] == "PREPARE 2 3");
    REQUIRE(coordinator.output.back() == "TRANSACTION_ABORTED 2");
}

TEST_CASE("Transaction with timeout") {
    MockCoordinator coordinator;
    
    coordinator.processCommand("BEGIN 3 1 2");
    coordinator.processCommand("PREPARED 3 1");
    coordinator.processCommand("TIMEOUT 3 2");
    
    REQUIRE(coordinator.output.size() >= 4);
    REQUIRE(coordinator.output[0] == "PREPARE 3 1");
    REQUIRE(coordinator.output[1] == "PREPARE 3 2");
    REQUIRE(coordinator.output.back() == "TRANSACTION_ABORTED 3");
}

TEST_CASE("Invalid commands") {
    MockCoordinator coordinator;
    
    REQUIRE_NOTHROW(coordinator.processCommand("INVALID_COMMAND"));
    REQUIRE(coordinator.output.back() == "UNKNOWN_COMMAND");
    
    REQUIRE_NOTHROW(coordinator.processCommand("BEGIN"));
    REQUIRE(coordinator.output.back().substr(0, 6) == "ERROR:");
    
    REQUIRE_NOTHROW(coordinator.processCommand("BEGIN abc 1 2"));
    REQUIRE(coordinator.output.back().substr(0, 6) == "ERROR:");
}

TEST_CASE("Recovery functionality") {
    MockCoordinator coordinator;
    
    coordinator.processCommand("BEGIN 4 1 2");
    coordinator.processCommand("PREPARED 4 1");
    coordinator.processCommand("RECOVER");
    
    REQUIRE(coordinator.output.size() > 0);
    // Verify that the coordinator attempts to resolve the incomplete transaction
    bool found_prepare_or_rollback = false;
    for (const auto& msg : coordinator.output) {
        if (msg == "PREPARE 4 2" || msg == "ROLLBACK 4 1") {
            found_prepare_or_rollback = true;
            break;
        }
    }
    REQUIRE(found_prepare_or_rollback);
}

TEST_CASE("Concurrent transactions") {
    MockCoordinator coordinator;
    
    coordinator.processCommand("BEGIN 5 1 2");
    coordinator.processCommand("BEGIN 6 3 4");
    coordinator.processCommand("PREPARED 5 1");
    coordinator.processCommand("PREPARED 6 3");
    coordinator.processCommand("PREPARED 5 2");
    coordinator.processCommand("PREPARED 6 4");
    
    bool found_commit_5 = false;
    bool found_commit_6 = false;
    
    for (const auto& msg : coordinator.output) {
        if (msg == "TRANSACTION_COMMITTED 5") found_commit_5 = true;
        if (msg == "TRANSACTION_COMMITTED 6") found_commit_6 = true;
    }
    
    REQUIRE(found_commit_5);
    REQUIRE(found_commit_6);
}

TEST_CASE("Log functionality") {
    MockCoordinator coordinator;
    
    coordinator.processCommand("BEGIN 7 1 2");
    coordinator.processCommand("PREPARED 7 1");
    coordinator.processCommand("PREPARED 7 2");
    coordinator.processCommand("PRINT_LOG");
    
    bool found_log_entries = false;
    for (const auto& msg : coordinator.output) {
        if (msg.find("BEGIN 7") != std::string::npos ||
            msg.find("PREPARED 7") != std::string::npos) {
            found_log_entries = true;
            break;
        }
    }
    REQUIRE(found_log_entries);
}

TEST_CASE("Edge cases") {
    MockCoordinator coordinator;
    
    // Empty transaction list
    coordinator.processCommand("BEGIN 8");
    REQUIRE(coordinator.output.back().substr(0, 6) == "ERROR:");
    
    // Duplicate service IDs
    coordinator.processCommand("BEGIN 9 1 1");
    REQUIRE(coordinator.output.back().substr(0, 6) == "ERROR:");
    
    // Invalid transaction ID
    coordinator.processCommand("PREPARED 10 1");
    REQUIRE(coordinator.output.back().substr(0, 6) == "ERROR:");
    
    // Invalid service ID
    coordinator.processCommand("BEGIN 11 1 2");
    coordinator.processCommand("PREPARED 11 3");
    REQUIRE(coordinator.output.back().substr(0, 6) == "ERROR:");
}