#include "distributed_tx.h"
#include "catch.hpp"
#include <chrono>
#include <thread>
#include <vector>
#include <string>

using namespace distributed_tx;
using namespace std;

// Test case: Successful transaction commits across all participants.
TEST_CASE("Successful transaction commits across all participants") {
    // Create a coordinator with a timeout of 1000 milliseconds.
    Coordinator coordinator(1000);
    // Create two participants that will vote COMMIT (true means vote commit, false means vote abort).
    Participant participant1("p1", true, false);
    Participant participant2("p2", true, false);

    // Add participants to the coordinator.
    coordinator.addParticipant(&participant1);
    coordinator.addParticipant(&participant2);

    // Initiate the transaction.
    coordinator.initiateTransaction();

    // Wait until the coordinator registers acknowledgements from all participants.
    while (!coordinator.allAcksReceived()) {
        this_thread::sleep_for(chrono::milliseconds(10));
    }

    // Check that the global decision is to commit.
    string decision = coordinator.getGlobalDecision();
    REQUIRE(decision == "GLOBAL_COMMIT");

    // Verify that both participants logged a committed state.
    REQUIRE(participant1.getLog() == "committed");
    REQUIRE(participant2.getLog() == "committed");
}

// Test case: Transaction aborts if any participant votes abort.
TEST_CASE("Transaction aborts if any participant votes abort") {
    Coordinator coordinator(1000);
    // Participant p1 will vote COMMIT, while participant p2 will vote ABORT.
    Participant participant1("p1", true, false);
    Participant participant2("p2", false, false);

    coordinator.addParticipant(&participant1);
    coordinator.addParticipant(&participant2);

    coordinator.initiateTransaction();

    while (!coordinator.allAcksReceived()) {
        this_thread::sleep_for(chrono::milliseconds(10));
    }

    string decision = coordinator.getGlobalDecision();
    REQUIRE(decision == "GLOBAL_ABORT");

    // Both participants should have aborted the transaction.
    REQUIRE(participant1.getLog() == "aborted");
    REQUIRE(participant2.getLog() == "aborted");
}

// Test case: Transaction aborts when a participant times out during voting.
TEST_CASE("Transaction aborts when a participant times out during voting") {
    Coordinator coordinator(500); // Set a shorter timeout for testing.
    // Participant p1 behaves normally while participant p2 simulates a timeout.
    Participant participant1("p1", true, false);
    Participant participant2("p2", true, true);  // The third parameter true simulates a timeout.

    coordinator.addParticipant(&participant1);
    coordinator.addParticipant(&participant2);

    coordinator.initiateTransaction();

    while (!coordinator.allAcksReceived()) {
        this_thread::sleep_for(chrono::milliseconds(10));
    }

    string decision = coordinator.getGlobalDecision();
    REQUIRE(decision == "GLOBAL_ABORT");

    // Both participants should have aborted due to the timeout in one participant.
    REQUIRE(participant1.getLog() == "aborted");
    REQUIRE(participant2.getLog() == "aborted");
}

// Test case: Participant recovery after a simulated crash during transaction.
TEST_CASE("Participant recovery recovers unfinished transaction") {
    Coordinator coordinator(1000);
    // Both participants are set to vote commit.
    Participant participant1("p1", true, false);
    Participant participant2("p2", true, false);

    coordinator.addParticipant(&participant1);
    coordinator.addParticipant(&participant2);

    // Initiate the transaction.
    coordinator.initiateTransaction();

    // Simulate a crash for participant2 after it has prepared its transaction.
    participant2.simulateCrash();

    // Wait briefly to allow the coordinator to process the state from participant1.
    auto start = chrono::steady_clock::now();
    while (!coordinator.allAcksReceived() &&
           chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now() - start).count() < 500) {
        this_thread::sleep_for(chrono::milliseconds(10));
    }
    
    // Simulate recovery for participant2.
    participant2.recover();

    // Wait until all acknowledgements are received post-recovery.
    while (!coordinator.allAcksReceived()) {
        this_thread::sleep_for(chrono::milliseconds(10));
    }

    string decision = coordinator.getGlobalDecision();
    // Since both participants are commit voters, the final decision should be commit.
    REQUIRE(decision == "GLOBAL_COMMIT");

    // Validate that both participants ultimately logged a committed state.
    REQUIRE(participant1.getLog() == "committed");
    REQUIRE(participant2.getLog() == "committed");
}