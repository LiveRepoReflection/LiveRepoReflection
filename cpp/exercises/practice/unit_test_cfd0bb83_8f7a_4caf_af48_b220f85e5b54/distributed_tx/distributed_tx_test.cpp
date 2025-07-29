#include "distributed_tx.h"
#include "catch.hpp"
#include <thread>
#include <chrono>
#include <set>
#include <stdexcept>

using namespace std::chrono_literals;

// These tests assume the existence of a Coordinator class in the distributed_tx namespace
// with the following API:
//   std::string BeginTransaction();
//   void RegisterParticipant(const std::string& transaction_id, const std::string& service_id, const std::string& rollback_endpoint);
//   void ReportVote(const std::string& transaction_id, const std::string& service_id, bool voteCommit);
//   std::string GetTransactionStatus(const std::string& transaction_id);
//   void SetPrepareTimeout(int milliseconds);
//   void RecoverFromLog();
//
// The GetTransactionStatus function returns one of "pending", "committed", or "rolled_back".
// The ReportVote function accepts true for a commit vote and false for an abort vote.
// Note: The behavior for timeouts and logging recovery is simulated based on configurable timeouts.

TEST_CASE("Unique Transaction IDs", "[transaction]") {
    distributed_tx::Coordinator coordinator;
    auto tx1 = coordinator.BeginTransaction();
    auto tx2 = coordinator.BeginTransaction();
    REQUIRE(tx1 != tx2);
}

TEST_CASE("Commit Transaction with Single Participant", "[transaction]") {
    distributed_tx::Coordinator coordinator;
    auto tx = coordinator.BeginTransaction();
    coordinator.RegisterParticipant(tx, "service1", "http://localhost/rollback1");
    coordinator.ReportVote(tx, "service1", true);
    // Allow some time for the coordinator to process commit
    std::this_thread::sleep_for(100ms);
    REQUIRE(coordinator.GetTransactionStatus(tx) == "committed");
}

TEST_CASE("Abort Transaction with Single Participant", "[transaction]") {
    distributed_tx::Coordinator coordinator;
    auto tx = coordinator.BeginTransaction();
    coordinator.RegisterParticipant(tx, "service1", "http://localhost/rollback1");
    coordinator.ReportVote(tx, "service1", false);
    // Allow some time for the coordinator to process rollback
    std::this_thread::sleep_for(100ms);
    REQUIRE(coordinator.GetTransactionStatus(tx) == "rolled_back");
}

TEST_CASE("Commit Transaction with Multiple Participants", "[transaction]") {
    distributed_tx::Coordinator coordinator;
    auto tx = coordinator.BeginTransaction();
    coordinator.RegisterParticipant(tx, "service1", "http://localhost/rollback1");
    coordinator.RegisterParticipant(tx, "service2", "http://localhost/rollback2");
    coordinator.RegisterParticipant(tx, "service3", "http://localhost/rollback3");
    coordinator.ReportVote(tx, "service1", true);
    coordinator.ReportVote(tx, "service2", true);
    coordinator.ReportVote(tx, "service3", true);
    std::this_thread::sleep_for(100ms);
    REQUIRE(coordinator.GetTransactionStatus(tx) == "committed");
}

TEST_CASE("Abort Transaction if Any Participant Votes Abort", "[transaction]") {
    distributed_tx::Coordinator coordinator;
    auto tx = coordinator.BeginTransaction();
    coordinator.RegisterParticipant(tx, "service1", "http://localhost/rollback1");
    coordinator.RegisterParticipant(tx, "service2", "http://localhost/rollback2");
    coordinator.RegisterParticipant(tx, "service3", "http://localhost/rollback3");
    coordinator.ReportVote(tx, "service1", true);
    coordinator.ReportVote(tx, "service2", false);
    coordinator.ReportVote(tx, "service3", true);
    std::this_thread::sleep_for(100ms);
    REQUIRE(coordinator.GetTransactionStatus(tx) == "rolled_back");
}

TEST_CASE("Timeout During Prepare Phase Causes Rollback", "[transaction]") {
    distributed_tx::Coordinator coordinator;
    // Set a short prepare timeout for testing purposes (e.g., 200 ms)
    coordinator.SetPrepareTimeout(200);
    auto tx = coordinator.BeginTransaction();
    coordinator.RegisterParticipant(tx, "service1", "http://localhost/rollback1");
    coordinator.RegisterParticipant(tx, "service2", "http://localhost/rollback2");
    // Report vote only for one service; the other will timeout
    coordinator.ReportVote(tx, "service1", true);
    // Wait longer than prepare timeout to simulate timeout for service2
    std::this_thread::sleep_for(300ms);
    REQUIRE(coordinator.GetTransactionStatus(tx) == "rolled_back");
}

TEST_CASE("Duplicate Participant Registration Throws Exception", "[transaction]") {
    distributed_tx::Coordinator coordinator;
    auto tx = coordinator.BeginTransaction();
    coordinator.RegisterParticipant(tx, "service1", "http://localhost/rollback1");
    // Attempting to register the same participant again should throw an exception.
    REQUIRE_THROWS_AS(coordinator.RegisterParticipant(tx, "service1", "http://localhost/rollback1"), std::invalid_argument);
}

TEST_CASE("Report Vote for Unregistered Participant Throws Exception", "[transaction]") {
    distributed_tx::Coordinator coordinator;
    auto tx = coordinator.BeginTransaction();
    // Reporting a vote for a participant that has not been registered should throw an exception.
    REQUIRE_THROWS_AS(coordinator.ReportVote(tx, "unknown_service", true), std::invalid_argument);
}

TEST_CASE("Invalid Transaction ID Throws Exception", "[transaction]") {
    distributed_tx::Coordinator coordinator;
    // Operations on an invalid or non-existent transaction ID should throw an exception.
    REQUIRE_THROWS_AS(coordinator.RegisterParticipant("invalid_tx", "service1", "http://localhost/rollback1"), std::invalid_argument);
    REQUIRE_THROWS_AS(coordinator.ReportVote("invalid_tx", "service1", true), std::invalid_argument);
    REQUIRE_THROWS_AS(coordinator.GetTransactionStatus("invalid_tx"), std::invalid_argument);
}

TEST_CASE("Logging and Recovery of In-Flight Transaction", "[recovery]") {
    {
        // In this block, simulate creating a transaction and processing some votes
        distributed_tx::Coordinator coordinator;
        auto tx = coordinator.BeginTransaction();
        coordinator.RegisterParticipant(tx, "service1", "http://localhost/rollback1");
        coordinator.RegisterParticipant(tx, "service2", "http://localhost/rollback2");
        // Only one participant votes before a simulated crash
        coordinator.ReportVote(tx, "service1", true);
        // Assume the coordinator logs the state to disk here.
    }
    {
        // Now simulate a process restart and recovery.
        distributed_tx::Coordinator coordinator;
        // Recover in-flight transactions from the log.
        coordinator.RecoverFromLog();
        // Retrieve the transaction ID from the log. For testing, we assume the recovery process
        // makes the transaction available via a known mechanism.
        // Here we simulate by retrieving a set of transaction IDs.
        std::set<std::string> recoveredTxs = coordinator.GetRecoveredTransactionIDs();
        // There should be at least one recovered transaction.
        REQUIRE(!recoveredTxs.empty());
        // For each recovered transaction, if not all votes were reported, the outcome should be rolled_back.
        for (const auto& tx : recoveredTxs) {
            std::string status = coordinator.GetTransactionStatus(tx);
            // Since one participant did not vote, the transaction should be rolled back after recovery.
            REQUIRE(status == "rolled_back");
        }
    }
}