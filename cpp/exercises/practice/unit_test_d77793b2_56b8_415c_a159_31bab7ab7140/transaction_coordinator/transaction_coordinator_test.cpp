#include "catch.hpp"
#include "transaction_coordinator.h"
#include <sstream>
#include <iostream>
#include <set>
#include <string>

// Helper class to capture std::cout output.
class CoutRedirect {
public:
    CoutRedirect(std::stringstream &newStream)
        : oldBuf(std::cout.rdbuf(newStream.rdbuf())) {}
    ~CoutRedirect() {
        std::cout.rdbuf(oldBuf);
    }
private:
    std::streambuf *oldBuf;
};

TEST_CASE("All COMMIT votes result in commit", "[transaction_coordinator]") {
    std::stringstream buffer;
    {
        CoutRedirect redirect(buffer);
        // Create a TransactionCoordinator instance.
        transaction_coordinator::TransactionCoordinator coordinator;
        
        // Begin transaction 1 with participants 101 and 102.
        std::set<int> participants = {101, 102};
        coordinator.processBeginTransaction(1, participants);
        
        // Vote requests: both nodes vote COMMIT.
        coordinator.processVoteRequest(1, 101, true);
        coordinator.processVoteRequest(1, 102, true);
    }
    
    std::string expected_output =
        "Node 101 COMMIT vote received for transaction 1.\n"
        "Node 102 COMMIT vote received for transaction 1.\n"
        "Transaction 1 prepared to commit (all nodes voted COMMIT).\n"
        "Transaction 1 committed.\n"
        "Node 101 instructed to COMMIT for transaction 1.\n"
        "Node 102 instructed to COMMIT for transaction 1.\n";
        
    std::string actual_output = buffer.str();
    CHECK(actual_output == expected_output);
}

TEST_CASE("ABORT vote leads to rollback", "[transaction_coordinator]") {
    std::stringstream buffer;
    {
        CoutRedirect redirect(buffer);
        transaction_coordinator::TransactionCoordinator coordinator;
        
        // Begin transaction 2 with participants 201 and 202.
        std::set<int> participants = {201, 202};
        coordinator.processBeginTransaction(2, participants);
        
        // Vote requests: node 201 votes COMMIT, node 202 votes ABORT.
        coordinator.processVoteRequest(2, 201, true);
        coordinator.processVoteRequest(2, 202, false);
    }
    
    std::string expected_output =
        "Node 201 COMMIT vote received for transaction 2.\n"
        "Node 202 ABORT vote received for transaction 2.\n"
        "Transaction 2 aborted.\n"
        "Node 201 instructed to ROLLBACK for transaction 2.\n"
        "Node 202 instructed to ROLLBACK for transaction 2.\n"
        "Transaction 2 rolled back.\n";
        
    std::string actual_output = buffer.str();
    CHECK(actual_output == expected_output);
}

TEST_CASE("Timeout event results in abort", "[transaction_coordinator]") {
    std::stringstream buffer;
    {
        CoutRedirect redirect(buffer);
        transaction_coordinator::TransactionCoordinator coordinator;
        
        // Begin transaction 3 with participants 301 and 302.
        std::set<int> participants = {301, 302};
        coordinator.processBeginTransaction(3, participants);
        
        // Node 301 votes COMMIT.
        coordinator.processVoteRequest(3, 301, true);
        
        // Coordinator timeout event.
        coordinator.processCoordinatorTimeout(3);
    }
    
    std::string expected_output =
        "Node 301 COMMIT vote received for transaction 3.\n"
        "Coordinator timed out waiting for votes for transaction 3.\n"
        "Transaction 3 aborted.\n"
        "Node 301 instructed to ROLLBACK for transaction 3.\n"
        "Node 302 instructed to ROLLBACK for transaction 3.\n"
        "Transaction 3 rolled back.\n";
        
    std::string actual_output = buffer.str();
    CHECK(actual_output == expected_output);
}

TEST_CASE("Invalid transaction ID handling", "[transaction_coordinator]") {
    std::stringstream buffer;
    {
        CoutRedirect redirect(buffer);
        transaction_coordinator::TransactionCoordinator coordinator;
        
        // Vote request for transaction 4 before a BeginTransaction is processed.
        // Node 401 votes COMMIT.
        coordinator.processVoteRequest(4, 401, true);
        
        // Now, Begin transaction 4 with participants 401 and 402.
        std::set<int> participants = {401, 402};
        coordinator.processBeginTransaction(4, participants);
    }
    
    std::string expected_output =
        "Invalid transaction ID 4\n"
        "Node 401 COMMIT vote received for transaction 4.\n";
        
    std::string actual_output = buffer.str();
    CHECK(actual_output == expected_output);
}