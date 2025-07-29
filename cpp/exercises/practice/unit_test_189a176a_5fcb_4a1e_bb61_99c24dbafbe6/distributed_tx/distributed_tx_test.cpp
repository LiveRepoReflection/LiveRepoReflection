#include <sstream>
#include <iostream>
#include <thread>
#include <chrono>
#include <vector>
#include <memory>
#include "catch.hpp"
#include "distributed_tx.h"

// Utility for redirecting stdout to a string
class StdoutCapture {
public:
    StdoutCapture() : old_buf(std::cout.rdbuf(buffer.rdbuf())) {}
    ~StdoutCapture() { std::cout.rdbuf(old_buf); }
    std::string get_output() { return buffer.str(); }
    void clear() { buffer.str(""); buffer.clear(); }

private:
    std::stringstream buffer;
    std::streambuf* old_buf;
};

// Helper to run commands and get output
std::string run_commands(const std::vector<std::string>& commands) {
    StdoutCapture capture;
    std::stringstream input;
    for (const auto& cmd : commands) {
        input << cmd << "\n";
    }

    // Run the transaction coordinator with the input
    process_commands(input);
    return capture.get_output();
}

TEST_CASE("Basic transaction flow", "[basic]") {
    std::vector<std::string> commands = {
        "ADD_SERVICE 1 10 20 30",
        "ADD_SERVICE 2 15 25 35",
        "BEGIN_TRANSACTION 12345 1 2",
        "GET_TRANSACTION_STATUS 12345",
        "COMMIT_TRANSACTION 12345",
        "GET_TRANSACTION_STATUS 12345"
    };

    std::string output = run_commands(commands);
    std::istringstream iss(output);
    std::string line;

    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "IN_PROGRESS");
    
    std::getline(iss, line);
    REQUIRE(line == "45");
    
    std::getline(iss, line);
    REQUIRE(line == "COMMITTED");
}

TEST_CASE("Transaction with unavailable service", "[unavailable]") {
    std::vector<std::string> commands = {
        "ADD_SERVICE 1 10 20 30",
        "ADD_SERVICE 2 15 25 35",
        "BEGIN_TRANSACTION 1 1 2",
        "BEGIN_TRANSACTION 2 1 3", // Service 3 doesn't exist
        "GET_TRANSACTION_STATUS 2"
    };

    std::string output = run_commands(commands);
    std::istringstream iss(output);
    std::string line;

    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "ABORTED");
    
    std::getline(iss, line);
    REQUIRE(line == "NOT_FOUND");
}

TEST_CASE("Transaction rollback", "[rollback]") {
    std::vector<std::string> commands = {
        "ADD_SERVICE 1 10 20 30",
        "ADD_SERVICE 2 15 25 35",
        "BEGIN_TRANSACTION 1 1 2",
        "ROLLBACK_TRANSACTION 1",
        "GET_TRANSACTION_STATUS 1"
    };

    std::string output = run_commands(commands);
    std::istringstream iss(output);
    std::string line;

    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "65"); // 30 + 35
    
    std::getline(iss, line);
    REQUIRE(line == "ROLLED_BACK");
}

TEST_CASE("Service already in transaction", "[service_busy]") {
    std::vector<std::string> commands = {
        "ADD_SERVICE 1 10 20 30",
        "ADD_SERVICE 2 15 25 35",
        "BEGIN_TRANSACTION 1 1 2",
        "BEGIN_TRANSACTION 2 1", // Service 1 is already in transaction 1
        "COMMIT_TRANSACTION 1",
        "BEGIN_TRANSACTION 2 1", // Now service 1 should be available again
        "GET_TRANSACTION_STATUS 2"
    };

    std::string output = run_commands(commands);
    std::istringstream iss(output);
    std::string line;

    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "ABORTED");
    
    std::getline(iss, line);
    REQUIRE(line == "45");
    
    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "IN_PROGRESS");
}

TEST_CASE("Non-existent transaction queries", "[not_found]") {
    std::vector<std::string> commands = {
        "GET_TRANSACTION_STATUS 999",
        "COMMIT_TRANSACTION 999",
        "ROLLBACK_TRANSACTION 999"
    };

    std::string output = run_commands(commands);
    std::istringstream iss(output);
    std::string line;

    std::getline(iss, line);
    REQUIRE(line == "NOT_FOUND");
    
    std::getline(iss, line);
    REQUIRE(line == "TRANSACTION_NOT_FOUND");
    
    std::getline(iss, line);
    REQUIRE(line == "TRANSACTION_NOT_FOUND");
}

TEST_CASE("Multiple transactions in sequence", "[sequence]") {
    std::vector<std::string> commands = {
        "ADD_SERVICE 1 10 20 30",
        "ADD_SERVICE 2 15 25 35",
        "ADD_SERVICE 3 5 10 15",
        "BEGIN_TRANSACTION 1 1 2",
        "COMMIT_TRANSACTION 1",
        "BEGIN_TRANSACTION 2 2 3",
        "ROLLBACK_TRANSACTION 2",
        "BEGIN_TRANSACTION 3 1 3",
        "GET_TRANSACTION_STATUS 3"
    };

    std::string output = run_commands(commands);
    std::istringstream iss(output);
    std::string line;

    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "45");
    
    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "50");
    
    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "IN_PROGRESS");
}

TEST_CASE("Large scale transaction", "[large_scale]") {
    std::vector<std::string> commands;
    
    // Add 100 services
    for (int i = 1; i <= 100; i++) {
        commands.push_back("ADD_SERVICE " + std::to_string(i) + " 5 10 15");
    }
    
    // Create a transaction with all 100 services
    std::string tx_cmd = "BEGIN_TRANSACTION 1";
    for (int i = 1; i <= 100; i++) {
        tx_cmd += " " + std::to_string(i);
    }
    commands.push_back(tx_cmd);
    commands.push_back("COMMIT_TRANSACTION 1");
    
    std::string output = run_commands(commands);
    std::istringstream iss(output);
    std::string line;

    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "1000"); // 100 services * 10 commit time each
}

TEST_CASE("Multiple concurrent transactions", "[concurrent]") {
    std::vector<std::string> commands = {
        "ADD_SERVICE 1 10 20 30",
        "ADD_SERVICE 2 15 25 35",
        "ADD_SERVICE 3 5 10 15",
        "ADD_SERVICE 4 20 30 40",
        "BEGIN_TRANSACTION 1 1 2",
        "BEGIN_TRANSACTION 2 3 4",
        "GET_TRANSACTION_STATUS 1",
        "GET_TRANSACTION_STATUS 2",
        "COMMIT_TRANSACTION 1",
        "COMMIT_TRANSACTION 2"
    };

    std::string output = run_commands(commands);
    std::istringstream iss(output);
    std::string line;

    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "IN_PROGRESS");
    
    std::getline(iss, line);
    REQUIRE(line == "IN_PROGRESS");
    
    std::getline(iss, line);
    REQUIRE(line == "45");
    
    std::getline(iss, line);
    REQUIRE(line == "40");
}

TEST_CASE("Edge cases handling", "[edge_cases]") {
    std::vector<std::string> commands = {
        "ADD_SERVICE 9223372036854775807 10 20 30", // Max long long
        "BEGIN_TRANSACTION 9223372036854775807 9223372036854775807",
        "COMMIT_TRANSACTION 9223372036854775807"
    };

    std::string output = run_commands(commands);
    std::istringstream iss(output);
    std::string line;

    std::getline(iss, line);
    REQUIRE(line == "OK");
    
    std::getline(iss, line);
    REQUIRE(line == "20");
}

TEST_CASE("Error handling - Commit failed", "[errors]") {
    // This test simulates a service being removed during a transaction
    std::vector<std::string> commands = {
        "ADD_SERVICE 1 10 20 30",
        "BEGIN_TRANSACTION 1 1",
        // At this point, imagine service 1 is removed externally
        // In a real implementation, you'd have a way to simulate this
        // For this test, we'll need to modify the implementation to handle this case
    };
    
    // Note: This is a conceptual test. The actual implementation would need
    // a way to simulate service failures or removals during a transaction.
}