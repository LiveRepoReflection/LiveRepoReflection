#include "distributed_tx.h"
#include "catch.hpp"
#include <sstream>
#include <string>

TEST_CASE("Single Transaction Commit") {
    // Single transaction with one participant that always commits (probability 1.0)
    std::string input = "1\n1 1 10 1.0\n";
    std::istringstream iss(input);
    std::ostringstream oss;
    distributed_tx::processTransactions(iss, oss);
    std::string expected = "Transaction 1: Committed\n";
    REQUIRE(oss.str() == expected);
}

TEST_CASE("Single Transaction Rollback Due to One Participant Failure") {
    // Single transaction with two participants; one always commits (1.0) and one always fails (0.0)
    std::string input = "1\n2 2 20 1.0 30 0.0\n";
    std::istringstream iss(input);
    std::ostringstream oss;
    distributed_tx::processTransactions(iss, oss);
    std::string expected = "Transaction 2: Rolled Back\n";
    REQUIRE(oss.str() == expected);
}

TEST_CASE("Multiple Transactions Mixed Outcomes") {
    // Two transactions: 
    // Transaction 100 with three participants that all commit.
    // Transaction 200 with one participant failing.
    std::string input = "2\n100 3 40 1.0 50 1.0 60 1.0\n200 2 70 1.0 80 0.0\n";
    std::istringstream iss(input);
    std::ostringstream oss;
    distributed_tx::processTransactions(iss, oss);
    std::string expected = "Transaction 100: Committed\nTransaction 200: Rolled Back\n";
    REQUIRE(oss.str() == expected);
}

TEST_CASE("Edge Case: All Participants Vote No") {
    // Single transaction where every participant votes no (0.0 probability)
    std::string input = "1\n300 2 90 0.0 100 0.0\n";
    std::istringstream iss(input);
    std::ostringstream oss;
    distributed_tx::processTransactions(iss, oss);
    std::string expected = "Transaction 300: Rolled Back\n";
    REQUIRE(oss.str() == expected);
}

TEST_CASE("Edge Case: Zero Transactions") {
    // Test handling of zero transactions provided as input.
    // Although constraints guarantee at least one transaction, the implementation
    // should gracefully handle this input.
    std::string input = "0\n";
    std::istringstream iss(input);
    std::ostringstream oss;
    distributed_tx::processTransactions(iss, oss);
    std::string expected = "";
    REQUIRE(oss.str() == expected);
}