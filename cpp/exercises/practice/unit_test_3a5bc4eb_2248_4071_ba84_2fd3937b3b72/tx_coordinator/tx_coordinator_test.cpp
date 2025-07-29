#include "tx_coordinator.h"
#include "catch.hpp"
#include <vector>
#include <string>
#include <thread>
#include <chrono>
#include <future>
#include <set>

// The following tests assume that the tx_coordinator module provides methods for
// injecting mock responses for service endpoints. The assumed interface is as follows:
//
// void tx_coordinator::setMockResponse(const std::string& url, const std::string& phase, const std::string& response, int delay_ms = 0);
// void tx_coordinator::clearMockResponses();
// tx_coordinator::TransactionResult tx_coordinator::processTransaction(const std::vector<std::string>& prepareUrls, int timeout_ms);
// void tx_coordinator::recoverPendingTransactions();
// void tx_coordinator::resetCoordinator(); // Resets internal state and log (only for testing)

using namespace tx_coordinator;

TEST_CASE("Successful Transaction: all services ACK", "[tx_coordinator]") {
    // Reset coordinator state and clear mocks.
    resetCoordinator();
    clearMockResponses();
    
    // Setup mock responses for prepare phase (all ACK) and commit phase (all ACK).
    setMockResponse("http://service1/prepare", "prepare", "ACK");
    setMockResponse("http://service2/prepare", "prepare", "ACK");
    setMockResponse("http://service3/prepare", "prepare", "ACK");
    
    setMockResponse("http://service1/commit",  "commit", "ACK");
    setMockResponse("http://service2/commit",  "commit", "ACK");
    setMockResponse("http://service3/commit",  "commit", "ACK");
    
    std::vector<std::string> services = {
        "http://service1/prepare",
        "http://service2/prepare",
        "http://service3/prepare"
    };
    
    // Process transaction with a timeout of 1000ms.
    TransactionResult result = processTransaction(services, 1000);
    
    // Expect committed result.
    REQUIRE(result.status == "committed");
    // Transaction ID should be non-empty.
    REQUIRE_FALSE(result.transactionId.empty());
    // There should be no errors.
    REQUIRE(result.errors.empty());
}

TEST_CASE("Prepare Failure Leads to Rollback", "[tx_coordinator]") {
    resetCoordinator();
    clearMockResponses();
    
    // Setup mock responses; one service returns NACK during prepare.
    setMockResponse("http://service1/prepare", "prepare", "ACK");
    setMockResponse("http://service2/prepare", "prepare", "NACK");
    setMockResponse("http://service3/prepare", "prepare", "ACK");
    
    // Even though commit responses are set, they should not be used because prepare fails.
    setMockResponse("http://service1/commit", "commit", "ACK");
    setMockResponse("http://service2/commit", "commit", "ACK");
    setMockResponse("http://service3/commit", "commit", "ACK");
    
    // Setup rollback responses for each service.
    setMockResponse("http://service1/rollback", "rollback", "ACK");
    setMockResponse("http://service2/rollback", "rollback", "ACK");
    setMockResponse("http://service3/rollback", "rollback", "ACK");
    
    std::vector<std::string> services = {
        "http://service1/prepare",
        "http://service2/prepare",
        "http://service3/prepare"
    };
    
    TransactionResult result = processTransaction(services, 1000);
    
    // Expect rolled_back because one service failed in the prepare phase.
    REQUIRE(result.status == "rolled_back");
    REQUIRE_FALSE(result.transactionId.empty());
    // There should be at least one error reported.
    REQUIRE_FALSE(result.errors.empty());
}

TEST_CASE("Prepare Timeout Leads to Rollback", "[tx_coordinator]") {
    resetCoordinator();
    clearMockResponses();
    
    // Setup mock responses; one service delays beyond the timeout.
    setMockResponse("http://service1/prepare", "prepare", "ACK");
    // Delay service2 by 1500ms, which exceeds timeout of 1000ms.
    setMockResponse("http://service2/prepare", "prepare", "ACK", 1500);
    setMockResponse("http://service3/prepare", "prepare", "ACK");
    
    // Setup rollback responses.
    setMockResponse("http://service1/rollback", "rollback", "ACK");
    setMockResponse("http://service2/rollback", "rollback", "ACK");
    setMockResponse("http://service3/rollback", "rollback", "ACK");
    
    std::vector<std::string> services = {
        "http://service1/prepare",
        "http://service2/prepare",
        "http://service3/prepare"
    };
    
    TransactionResult result = processTransaction(services, 1000);
    
    // Expect rolled_back result due to timeout.
    REQUIRE(result.status == "rolled_back");
    REQUIRE_FALSE(result.transactionId.empty());
    REQUIRE_FALSE(result.errors.empty());
}

TEST_CASE("Concurrent Transactions with Unique IDs", "[tx_coordinator]") {
    resetCoordinator();
    clearMockResponses();
    
    // Setup mocks to always ACK for prepare and commit.
    setMockResponse("http://service1/prepare", "prepare", "ACK");
    setMockResponse("http://service2/prepare", "prepare", "ACK");
    setMockResponse("http://service3/prepare", "prepare", "ACK");
    
    setMockResponse("http://service1/commit", "commit", "ACK");
    setMockResponse("http://service2/commit", "commit", "ACK");
    setMockResponse("http://service3/commit", "commit", "ACK");
    
    std::vector<std::string> services = {
        "http://service1/prepare",
        "http://service2/prepare",
        "http://service3/prepare"
    };
    
    // Launch several transactions concurrently.
    const int numTransactions = 10;
    std::vector<std::future<TransactionResult>> futures;
    for (int i = 0; i < numTransactions; ++i) {
        futures.push_back(std::async(std::launch::async, [services]() {
            return processTransaction(services, 1000);
        }));
    }
    
    std::set<std::string> transactionIds;
    for (auto& fut : futures) {
        TransactionResult res = fut.get();
        REQUIRE(res.status == "committed");
        REQUIRE_FALSE(res.transactionId.empty());
        // Ensure unique transaction IDs.
        auto inserted = transactionIds.insert(res.transactionId);
        REQUIRE(inserted.second == true);
    }
}

TEST_CASE("Recovery from Pending Transaction", "[tx_coordinator][recovery]") {
    resetCoordinator();
    clearMockResponses();
    
    // For this test, simulate a pending transaction that gets stuck in commit phase.
    // Setup mocks for prepare phase to ACK.
    setMockResponse("http://service1/prepare", "prepare", "ACK");
    setMockResponse("http://service2/prepare", "prepare", "ACK");
    setMockResponse("http://service3/prepare", "prepare", "ACK");
    
    // Setup mocks for commit phase: one service delays its commit response indefinitely.
    setMockResponse("http://service1/commit", "commit", "ACK");
    setMockResponse("http://service2/commit", "commit", "ACK", 2000); // delay longer than recovery trigger
    setMockResponse("http://service3/commit", "commit", "ACK");
    
    // Setup rollback responses.
    setMockResponse("http://service1/rollback", "rollback", "ACK");
    setMockResponse("http://service2/rollback", "rollback", "ACK");
    setMockResponse("http://service3/rollback", "rollback", "ACK");
    
    std::vector<std::string> services = {
        "http://service1/prepare",
        "http://service2/prepare",
        "http://service3/prepare"
    };
    
    // Start the transaction in a separate async call.
    auto fut = std::async(std::launch::async, [services]() {
        return processTransaction(services, 1000);
    });
    
    // Wait a bit to ensure the transaction has moved to the commit phase and is pending.
    std::this_thread::sleep_for(std::chrono::milliseconds(1200));
    
    // Simulate coordinator recovery.
    recoverPendingTransactions();
    
    // Get the result.
    TransactionResult result = fut.get();
    
    // The transaction should have been recovered and rolled back due to commit delay.
    // Depending on the coordinator implementation, the recovered transaction might finalize as rolled_back.
    REQUIRE((result.status == "rolled_back" || result.status == "failed"));
    REQUIRE_FALSE(result.transactionId.empty());
    REQUIRE_FALSE(result.errors.empty());
}