#include <chrono>
#include <iostream>
#include <thread>
#include <vector>
#include <random>
#include <atomic>
#include <functional>
#include "distributed_tx.h"
#include "catch.hpp"

// Mock Participant for testing
class MockParticipant : public Participant {
private:
    int id;
    bool shouldFail;
    std::atomic<bool> executed{false};
    std::string lastOperation;
    std::atomic<int> delayMs{0};
    
public:
    MockParticipant(int id, bool shouldFail = false) : id(id), shouldFail(shouldFail) {}
    
    void setDelay(int ms) {
        delayMs = ms;
    }
    
    bool execute(std::string operation) override {
        if (delayMs > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(delayMs));
        }
        
        lastOperation = operation;
        executed = true;
        return !shouldFail;
    }
    
    bool prepare() override {
        if (delayMs > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(delayMs));
        }
        
        return executed && !shouldFail;
    }
    
    bool commit() override {
        if (delayMs > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(delayMs));
        }
        
        return executed && !shouldFail;
    }
    
    bool rollback() override {
        if (delayMs > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(delayMs));
        }
        
        executed = false;
        return !shouldFail;
    }
    
    int getId() const { return id; }
    bool hasExecuted() const { return executed; }
    std::string getLastOperation() const { return lastOperation; }
    void setShouldFail(bool fail) { shouldFail = fail; }
};

// Test Helper Functions
std::vector<Participant*> createParticipants(int count, bool shouldFail = false) {
    std::vector<Participant*> participants;
    for (int i = 0; i < count; i++) {
        participants.push_back(new MockParticipant(i, shouldFail));
    }
    return participants;
}

void cleanupParticipants(std::vector<Participant*>& participants) {
    for (auto p : participants) {
        delete p;
    }
    participants.clear();
}

std::vector<MockParticipant*> createMockParticipants(int count) {
    std::vector<MockParticipant*> participants;
    for (int i = 0; i < count; i++) {
        participants.push_back(new MockParticipant(i));
    }
    return participants;
}

// Mock helper to convert MockParticipant* to Participant* vector
std::vector<Participant*> convertToParticipants(const std::vector<MockParticipant*>& mocks) {
    std::vector<Participant*> participants;
    for (auto p : mocks) {
        participants.push_back(static_cast<Participant*>(p));
    }
    return participants;
}

void cleanupMockParticipants(std::vector<MockParticipant*>& participants) {
    for (auto p : participants) {
        delete p;
    }
    participants.clear();
}

// Begin Tests
TEST_CASE("Coordinator handles successful transaction", "[coordinator]") {
    auto participants = createParticipants(5);
    Coordinator coordinator;
    
    bool result = coordinator.executeTransaction(participants, "test_operation");
    
    REQUIRE(result == true);
    
    cleanupParticipants(participants);
}

TEST_CASE("Coordinator correctly handles failed execution", "[coordinator]") {
    auto mockParticipants = createMockParticipants(5);
    
    // Make one participant fail during execution
    mockParticipants[2]->setShouldFail(true);
    
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    bool result = coordinator.executeTransaction(participants, "test_operation");
    
    REQUIRE(result == false);
    
    // Check that no participants are in an executed state
    for (auto p : mockParticipants) {
        REQUIRE(p->hasExecuted() == false);
    }
    
    cleanupMockParticipants(mockParticipants);
}

TEST_CASE("Coordinator handles failure during prepare phase", "[coordinator]") {
    auto mockParticipants = createMockParticipants(5);
    
    // Execute all operations first
    for (auto p : mockParticipants) {
        p->execute("test_operation");
    }
    
    // Make one participant fail during preparation
    mockParticipants[2]->setShouldFail(true);
    
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    bool result = coordinator.executeTransaction(participants, "test_operation");
    
    REQUIRE(result == false);
    
    // Check that all participants were rolled back
    for (auto p : mockParticipants) {
        REQUIRE(p->hasExecuted() == false);
    }
    
    cleanupMockParticipants(mockParticipants);
}

TEST_CASE("Coordinator handles failure during commit phase", "[coordinator]") {
    auto mockParticipants = createMockParticipants(5);
    
    // Set up special mock that fails only during commit
    class CommitFailMock : public MockParticipant {
    private:
        std::atomic<bool> prepareCompleted{false};
    public:
        CommitFailMock(int id) : MockParticipant(id) {}
        
        bool prepare() override {
            prepareCompleted = true;
            return true;
        }
        
        bool commit() override {
            return false;  // Always fail commit
        }
        
        bool rollback() override {
            return prepareCompleted;
        }
    };
    
    // Replace one participant with our special mock
    delete mockParticipants[3];
    mockParticipants[3] = new CommitFailMock(3);
    
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    bool result = coordinator.executeTransaction(participants, "test_operation");
    
    REQUIRE(result == false);
    
    cleanupMockParticipants(mockParticipants);
}

TEST_CASE("Coordinator handles timeouts", "[coordinator]") {
    auto mockParticipants = createMockParticipants(5);
    
    // Make one participant very slow
    mockParticipants[1]->setDelay(2000);  // 2 seconds, should trigger timeout
    
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    bool result = coordinator.executeTransaction(participants, "test_operation");
    
    REQUIRE(result == false);
    
    cleanupMockParticipants(mockParticipants);
}

TEST_CASE("Coordinator handles concurrent operations", "[coordinator][concurrent]") {
    const int participantCount = 20;
    auto mockParticipants = createMockParticipants(participantCount);
    
    // Set variable delays to ensure concurrency
    std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<> dist(10, 50);
    
    for (auto p : mockParticipants) {
        p->setDelay(dist(rng));
    }
    
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    // Measure time to verify concurrency is working
    auto startTime = std::chrono::high_resolution_clock::now();
    bool result = coordinator.executeTransaction(participants, "test_operation");
    auto endTime = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count();
    
    // If truly concurrent, the time should be less than the sum of all delays
    int totalDelay = participantCount * 50;
    REQUIRE(duration < totalDelay);
    REQUIRE(result == true);
    
    cleanupMockParticipants(mockParticipants);
}

TEST_CASE("Coordinator handles mixed success and failure scenarios", "[coordinator][mixed]") {
    auto mockParticipants = createMockParticipants(10);
    
    // Make a few participants fail
    mockParticipants[2]->setShouldFail(true);
    mockParticipants[5]->setShouldFail(true);
    mockParticipants[8]->setShouldFail(true);
    
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    bool result = coordinator.executeTransaction(participants, "test_operation");
    
    REQUIRE(result == false);
    
    // Check all participants were rolled back
    for (auto p : mockParticipants) {
        REQUIRE(p->hasExecuted() == false);
    }
    
    cleanupMockParticipants(mockParticipants);
}

TEST_CASE("Coordinator handles edge case of single participant", "[coordinator][edge]") {
    auto mockParticipants = createMockParticipants(1);
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    bool result = coordinator.executeTransaction(participants, "test_operation");
    
    REQUIRE(result == true);
    REQUIRE(mockParticipants[0]->hasExecuted() == true);
    REQUIRE(mockParticipants[0]->getLastOperation() == "test_operation");
    
    cleanupMockParticipants(mockParticipants);
}

TEST_CASE("Coordinator handles edge case of many participants", "[coordinator][edge][performance]") {
    const int participantCount = 100;
    auto mockParticipants = createMockParticipants(participantCount);
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    auto startTime = std::chrono::high_resolution_clock::now();
    bool result = coordinator.executeTransaction(participants, "test_operation");
    auto endTime = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count();
    
    REQUIRE(result == true);
    // Performance check - should complete in a reasonable time
    REQUIRE(duration < 5000);  // 5 seconds max for 100 participants
    
    cleanupMockParticipants(mockParticipants);
}

TEST_CASE("Coordinator handles rollback failures", "[coordinator][failure]") {
    auto mockParticipants = createMockParticipants(5);
    
    // Create a participant that fails during prepare and also during rollback
    class RollbackFailMock : public MockParticipant {
    public:
        RollbackFailMock(int id) : MockParticipant(id) {}
        
        bool prepare() override {
            return false;  // Always fail prepare
        }
        
        bool rollback() override {
            return false;  // Always fail rollback
        }
    };
    
    // Replace one participant with rollback-failing mock
    delete mockParticipants[2];
    mockParticipants[2] = new RollbackFailMock(2);
    
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    bool result = coordinator.executeTransaction(participants, "test_operation");
    
    REQUIRE(result == false);
    
    // Other participants should still be rolled back
    REQUIRE(mockParticipants[0]->hasExecuted() == false);
    REQUIRE(mockParticipants[1]->hasExecuted() == false);
    REQUIRE(mockParticipants[3]->hasExecuted() == false);
    REQUIRE(mockParticipants[4]->hasExecuted() == false);
    
    cleanupMockParticipants(mockParticipants);
}

TEST_CASE("Coordinator handles different operations", "[coordinator][operations]") {
    auto mockParticipants = createMockParticipants(5);
    Coordinator coordinator;
    auto participants = convertToParticipants(mockParticipants);
    
    std::vector<std::string> operations = {
        "insert", "update", "delete", "select", "complex query with spaces"
    };
    
    for (const auto& operation : operations) {
        bool result = coordinator.executeTransaction(participants, operation);
        REQUIRE(result == true);
        
        for (auto p : mockParticipants) {
            REQUIRE(p->getLastOperation() == operation);
        }
    }
    
    cleanupMockParticipants(mockParticipants);
}