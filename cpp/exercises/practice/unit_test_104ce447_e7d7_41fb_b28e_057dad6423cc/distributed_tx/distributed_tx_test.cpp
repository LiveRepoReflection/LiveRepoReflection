#include "catch.hpp"
#include "distributed_tx.h"
#include <sstream>
#include <thread>
#include <future>
#include <vector>
#include <chrono>

// Helper function to run the transaction coordinator with given input and capture its output.
std::string runCoordinator(const std::string &input) {
    std::istringstream in(input);
    std::ostringstream out;
    // Assuming processTransactions is the entry point function implemented by the solver.
    distributed_tx::processTransactions(in, out);
    return out.str();
}

TEST_CASE("Single commit transaction", "[distributed_tx]") {
    std::string input = "1 COMMIT 1:OP_UPDATE";
    std::string expected = "COMMIT 1\n";
    std::string output = runCoordinator(input);
    REQUIRE(output == expected);
}

TEST_CASE("Single rollback transaction", "[distributed_tx]") {
    std::string input = "2 ROLLBACK 1:OP_UPDATE";
    std::string expected = "ROLLBACK 2\n";
    std::string output = runCoordinator(input);
    REQUIRE(output == expected);
}

TEST_CASE("Multiple transactions sequentially", "[distributed_tx]") {
    // Two transactions: one commit and one rollback.
    std::string input = "1 COMMIT 1:OP_A 2:OP_B\n2 ROLLBACK 1:OP_C";
    std::string expected = "COMMIT 1\nROLLBACK 2\n";
    std::string output = runCoordinator(input);
    REQUIRE(output == expected);
}

TEST_CASE("Simulate service failure causes rollback", "[distributed_tx]") {
    // Using "FAIL" as a special operation string to simulate a service not responding.
    std::string input = "3 COMMIT 1:OP_OK 2:FAIL";
    // Even though the directive is COMMIT, a failure in one service should force a rollback.
    std::string expected = "ROLLBACK 3\n";
    std::string output = runCoordinator(input);
    REQUIRE(output == expected);
}

TEST_CASE("Concurrent transactions", "[distributed_tx]") {
    // Prepare inputs for concurrent transactions.
    std::vector<std::string> inputs = {
        "4 COMMIT 1:OP_A 2:OP_B",
        "5 ROLLBACK 1:OP_C",
        "6 COMMIT 1:OP_OK 3:OP_OK",
        "7 COMMIT 2:FAIL"  // This should trigger rollback due to failure.
    };
    std::vector<std::string> expected_outputs = {
        "COMMIT 4\n",
        "ROLLBACK 5\n",
        "COMMIT 6\n",
        "ROLLBACK 7\n"
    };

    // Launch each transaction in its own thread.
    std::vector<std::future<std::string>> futures;
    for (const auto &inp : inputs) {
        futures.emplace_back(std::async(std::launch::async, runCoordinator, inp));
    }
    
    // Collect outputs.
    std::vector<std::string> outputs;
    for (auto &fut : futures) {
        outputs.push_back(fut.get());
    }
    
    // Since the transactions are independent, sort both expected and outputs to compare regardless of ordering.
    std::sort(outputs.begin(), outputs.end());
    std::sort(expected_outputs.begin(), expected_outputs.end());
    
    REQUIRE(outputs == expected_outputs);
}