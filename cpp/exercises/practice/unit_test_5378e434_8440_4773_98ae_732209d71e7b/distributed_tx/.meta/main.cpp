#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <random>
#include "distributed_tx.h"

// A simple implementation of the Participant interface for testing
class TestParticipant : public Participant {
private:
    int id;
    std::string storedOperation;
    bool executed = false;
    bool prepared = false;
    bool failureProbability;
    std::mt19937 rng;
    std::uniform_real_distribution<> dist;

public:
    TestParticipant(int id, double failProb = 0.0) 
        : id(id), 
          failureProbability(failProb),
          rng(std::random_device{}()),
          dist(0.0, 1.0) {}

    bool shouldFail() const {
        return dist(const_cast<std::mt19937&>(rng)) < failureProbability;
    }

    bool execute(std::string operation) override {
        std::cout << "Participant " << id << " executing operation: " << operation << std::endl;
        if (shouldFail()) {
            std::cout << "Participant " << id << " failed to execute operation" << std::endl;
            return false;
        }
        storedOperation = operation;
        executed = true;
        return true;
    }

    bool prepare() override {
        std::cout << "Participant " << id << " preparing" << std::endl;
        if (!executed || shouldFail()) {
            std::cout << "Participant " << id << " failed to prepare" << std::endl;
            return false;
        }
        prepared = true;
        return true;
    }

    bool commit() override {
        std::cout << "Participant " << id << " committing" << std::endl;
        if (!prepared || shouldFail()) {
            std::cout << "Participant " << id << " failed to commit" << std::endl;
            return false;
        }
        std::cout << "Participant " << id << " committed successfully" << std::endl;
        return true;
    }

    bool rollback() override {
        std::cout << "Participant " << id << " rolling back" << std::endl;
        if (shouldFail()) {
            std::cout << "Participant " << id << " failed to rollback" << std::endl;
            return false;
        }
        executed = false;
        prepared = false;
        std::cout << "Participant " << id << " rolled back successfully" << std::endl;
        return true;
    }
};

// Test with multiple scenarios
void runScenario(const std::string& name, const std::vector<Participant*>& participants, const std::string& operation) {
    std::cout << "\n=== Scenario: " << name << " ===" << std::endl;
    Coordinator coordinator;
    bool result = coordinator.executeTransaction(participants, operation);
    std::cout << "Transaction " << (result ? "SUCCEEDED" : "FAILED") << std::endl;
    std::cout << std::string(40, '-') << std::endl;
}

int main() {
    // Scenario 1: All participants succeed
    std::vector<std::unique_ptr<Participant>> participants1;
    std::vector<Participant*> participantPtrs1;
    
    for (int i = 0; i < 5; ++i) {
        participants1.push_back(std::make_unique<TestParticipant>(i));
        participantPtrs1.push_back(participants1.back().get());
    }
    runScenario("All Succeed", participantPtrs1, "UPDATE balance SET amount = 100");

    // Scenario 2: One participant fails during execution
    std::vector<std::unique_ptr<Participant>> participants2;
    std::vector<Participant*> participantPtrs2;
    
    for (int i = 0; i < 5; ++i) {
        double failProb = (i == 2) ? 1.0 : 0.0;  // Make the 3rd participant always fail
        participants2.push_back(std::make_unique<TestParticipant>(i, failProb));
        participantPtrs2.push_back(participants2.back().get());
    }
    runScenario("One Fails During Execute", participantPtrs2, "DELETE FROM accounts WHERE inactive = true");

    // Scenario 3: One participant fails during prepare
    std::vector<std::unique_ptr<Participant>> participants3;
    std::vector<Participant*> participantPtrs3;
    
    class PrepareFailParticipant : public TestParticipant {
    public:
        PrepareFailParticipant(int id) : TestParticipant(id) {}
        
        bool prepare() override {
            std::cout << "Participant " << getId() << " will fail during prepare" << std::endl;
            return false;
        }
        
        int getId() const { return TestParticipant::id; }
    };
    
    for (int i = 0; i < 5; ++i) {
        if (i == 3) {
            participants3.push_back(std::make_unique<PrepareFailParticipant>(i));
        } else {
            participants3.push_back(std::make_unique<TestParticipant>(i));
        }
        participantPtrs3.push_back(participants3.back().get());
    }
    runScenario("One Fails During Prepare", participantPtrs3, "INSERT INTO logs VALUES (timestamp, 'event')");

    // Scenario 4: One participant fails during commit
    std::vector<std::unique_ptr<Participant>> participants4;
    std::vector<Participant*> participantPtrs4;
    
    class CommitFailParticipant : public TestParticipant {
    public:
        CommitFailParticipant(int id) : TestParticipant(id) {}
        
        bool commit() override {
            std::cout << "Participant " << getId() << " will fail during commit" << std::endl;
            return false;
        }
        
        int getId() const { return TestParticipant::id; }
    };
    
    for (int i = 0; i < 5; ++i) {
        if (i == 1) {
            participants4.push_back(std::make_unique<CommitFailParticipant>(i));
        } else {
            participants4.push_back(std::make_unique<TestParticipant>(i));
        }
        participantPtrs4.push_back(participants4.back().get());
    }
    runScenario("One Fails During Commit", participantPtrs4, "CREATE TABLE new_table (id INT, name VARCHAR)");

    // Scenario 5: Random failures
    std::vector<std::unique_ptr<Participant>> participants5;
    std::vector<Participant*> participantPtrs5;
    
    for (int i = 0; i < 10; ++i) {
        // 20% chance of failure for each participant
        participants5.push_back(std::make_unique<TestParticipant>(i, 0.2));
        participantPtrs5.push_back(participants5.back().get());
    }
    runScenario("Random Failures", participantPtrs5, "COMPLEX QUERY with multiple joins");

    return 0;
}