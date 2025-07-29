#include "distributed_tx.h"
#include "catch.hpp"
#include <chrono>
#include <iostream>
#include <memory>
#include <random>
#include <thread>
#include <vector>

class MockParticipant : public TransactionParticipant {
public:
    MockParticipant(std::string name, bool shouldFailPrepare = false,
                   bool shouldFailCommit = false, 
                   bool shouldFailCompensate = false)
        : name_(std::move(name)), 
          shouldFailPrepare_(shouldFailPrepare),
          shouldFailCommit_(shouldFailCommit),
          shouldFailCompensate_(shouldFailCompensate),
          prepareCallCount_(0),
          commitCallCount_(0),
          compensateCallCount_(0) {}

    bool prepare() override {
        prepareCallCount_++;
        return !shouldFailPrepare_;
    }

    bool commit() override {
        commitCallCount_++;
        return !shouldFailCommit_;
    }

    bool compensate() override {
        compensateCallCount_++;
        return !shouldFailCompensate_;
    }

    const std::string& getName() const { return name_; }

    int getPrepareCallCount() const { return prepareCallCount_; }
    int getCommitCallCount() const { return commitCallCount_; }
    int getCompensateCallCount() const { return compensateCallCount_; }

private:
    std::string name_;
    bool shouldFailPrepare_;
    bool shouldFailCommit_;
    bool shouldFailCompensate_;
    int prepareCallCount_;
    int commitCallCount_;
    int compensateCallCount_;
};

class RandomFailureParticipant : public TransactionParticipant {
public:
    RandomFailureParticipant(std::string name, double failureProbability = 0.3)
        : name_(std::move(name)), 
          failureProbability_(failureProbability),
          prepareCallCount_(0),
          commitCallCount_(0),
          compensateCallCount_(0),
          generator_(std::random_device{}()),
          distribution_(0.0, 1.0) {}

    bool prepare() override {
        prepareCallCount_++;
        bool result = distribution_(generator_) >= failureProbability_;
        return result;
    }

    bool commit() override {
        commitCallCount_++;
        bool result = distribution_(generator_) >= failureProbability_;
        return result;
    }

    bool compensate() override {
        compensateCallCount_++;
        bool result = distribution_(generator_) >= failureProbability_;
        return result;
    }

    const std::string& getName() const { return name_; }
    
    int getPrepareCallCount() const { return prepareCallCount_; }
    int getCommitCallCount() const { return commitCallCount_; }
    int getCompensateCallCount() const { return compensateCallCount_; }

private:
    std::string name_;
    double failureProbability_;
    int prepareCallCount_;
    int commitCallCount_;
    int compensateCallCount_;
    std::mt19937 generator_;
    std::uniform_real_distribution<double> distribution_;
};

TEST_CASE("TransactionCoordinator handles successful transaction", "[TransactionCoordinator]") {
    TransactionCoordinator coordinator;
    coordinator.begin();

    auto participant1 = std::make_shared<MockParticipant>("Participant1");
    auto participant2 = std::make_shared<MockParticipant>("Participant2");
    auto participant3 = std::make_shared<MockParticipant>("Participant3");

    coordinator.enroll(participant1);
    coordinator.enroll(participant2);
    coordinator.enroll(participant3);

    bool result = coordinator.commit();

    REQUIRE(result == true);
    REQUIRE(participant1->getPrepareCallCount() == 1);
    REQUIRE(participant1->getCommitCallCount() == 1);
    REQUIRE(participant1->getCompensateCallCount() == 0);
    
    REQUIRE(participant2->getPrepareCallCount() == 1);
    REQUIRE(participant2->getCommitCallCount() == 1);
    REQUIRE(participant2->getCompensateCallCount() == 0);
    
    REQUIRE(participant3->getPrepareCallCount() == 1);
    REQUIRE(participant3->getCommitCallCount() == 1);
    REQUIRE(participant3->getCompensateCallCount() == 0);
}

TEST_CASE("TransactionCoordinator handles prepare failure", "[TransactionCoordinator]") {
    TransactionCoordinator coordinator;
    coordinator.begin();

    auto participant1 = std::make_shared<MockParticipant>("Participant1");
    auto participant2 = std::make_shared<MockParticipant>("Participant2", true); // Will fail on prepare
    auto participant3 = std::make_shared<MockParticipant>("Participant3");

    coordinator.enroll(participant1);
    coordinator.enroll(participant2);
    coordinator.enroll(participant3);

    bool result = coordinator.commit();

    REQUIRE(result == false);
    REQUIRE(participant1->getPrepareCallCount() == 1);
    REQUIRE(participant1->getCommitCallCount() == 0);
    REQUIRE(participant1->getCompensateCallCount() == 1);
    
    REQUIRE(participant2->getPrepareCallCount() == 1);
    REQUIRE(participant2->getCommitCallCount() == 0);
    REQUIRE(participant2->getCompensateCallCount() == 0); // No need to compensate if prepare failed
    
    REQUIRE(participant3->getPrepareCallCount() == 0); // Should not be called after failure
    REQUIRE(participant3->getCommitCallCount() == 0);
    REQUIRE(participant3->getCompensateCallCount() == 0);
}

TEST_CASE("TransactionCoordinator handles commit failure", "[TransactionCoordinator]") {
    TransactionCoordinator coordinator;
    coordinator.begin();

    auto participant1 = std::make_shared<MockParticipant>("Participant1");
    auto participant2 = std::make_shared<MockParticipant>("Participant2", false, true); // Will fail on commit
    auto participant3 = std::make_shared<MockParticipant>("Participant3");

    coordinator.enroll(participant1);
    coordinator.enroll(participant2);
    coordinator.enroll(participant3);

    bool result = coordinator.commit();

    REQUIRE(result == false);
    REQUIRE(participant1->getPrepareCallCount() == 1);
    REQUIRE(participant1->getCommitCallCount() == 1);
    REQUIRE(participant1->getCompensateCallCount() == 1);
    
    REQUIRE(participant2->getPrepareCallCount() == 1);
    REQUIRE(participant2->getCommitCallCount() == 1);
    REQUIRE(participant2->getCompensateCallCount() == 1);
    
    REQUIRE(participant3->getPrepareCallCount() == 1);
    REQUIRE(participant3->getCommitCallCount() == 0); // Should not be called after failure
    REQUIRE(participant3->getCompensateCallCount() == 1);
}

TEST_CASE("TransactionCoordinator handles manual rollback", "[TransactionCoordinator]") {
    TransactionCoordinator coordinator;
    coordinator.begin();

    auto participant1 = std::make_shared<MockParticipant>("Participant1");
    auto participant2 = std::make_shared<MockParticipant>("Participant2");
    auto participant3 = std::make_shared<MockParticipant>("Participant3");

    coordinator.enroll(participant1);
    coordinator.enroll(participant2);
    coordinator.enroll(participant3);

    // Manually trigger rollback
    bool result = coordinator.rollback();

    REQUIRE(result == true);
    REQUIRE(participant1->getPrepareCallCount() == 0);
    REQUIRE(participant1->getCommitCallCount() == 0);
    REQUIRE(participant1->getCompensateCallCount() == 1);
    
    REQUIRE(participant2->getPrepareCallCount() == 0);
    REQUIRE(participant2->getCommitCallCount() == 0);
    REQUIRE(participant2->getCompensateCallCount() == 1);
    
    REQUIRE(participant3->getPrepareCallCount() == 0);
    REQUIRE(participant3->getCommitCallCount() == 0);
    REQUIRE(participant3->getCompensateCallCount() == 1);
}

TEST_CASE("TransactionCoordinator handles compensation failure", "[TransactionCoordinator]") {
    TransactionCoordinator coordinator;
    coordinator.begin();

    auto participant1 = std::make_shared<MockParticipant>("Participant1");
    auto participant2 = std::make_shared<MockParticipant>("Participant2", false, false, true); // Will fail on compensate
    auto participant3 = std::make_shared<MockParticipant>("Participant3");

    coordinator.enroll(participant1);
    coordinator.enroll(participant2);
    coordinator.enroll(participant3);

    bool result = coordinator.rollback();

    REQUIRE(result == false); // Rollback should fail because participant2's compensation fails
    REQUIRE(participant1->getCompensateCallCount() == 1);
    REQUIRE(participant2->getCompensateCallCount() == 1);
    REQUIRE(participant3->getCompensateCallCount() == 1);
}

TEST_CASE("TransactionCoordinator handles empty transaction", "[TransactionCoordinator]") {
    TransactionCoordinator coordinator;
    coordinator.begin();

    bool commitResult = coordinator.commit();
    REQUIRE(commitResult == true);

    coordinator.begin(); // Start a new transaction
    bool rollbackResult = coordinator.rollback();
    REQUIRE(rollbackResult == true);
}

TEST_CASE("TransactionCoordinator handles concurrent transactions", "[TransactionCoordinator]") {
    const int numThreads = 10;
    const int numParticipantsPerTx = 5;
    std::vector<std::thread> threads;
    std::atomic<int> successCount(0);
    std::atomic<int> failureCount(0);

    for (int i = 0; i < numThreads; ++i) {
        threads.emplace_back([i, numParticipantsPerTx, &successCount, &failureCount]() {
            TransactionCoordinator coordinator;
            coordinator.begin();

            // Add participants with small chance of random failure
            for (int j = 0; j < numParticipantsPerTx; ++j) {
                auto participant = std::make_shared<RandomFailureParticipant>(
                    "Participant_" + std::to_string(i) + "_" + std::to_string(j), 0.1);
                coordinator.enroll(participant);
            }

            // Randomly decide between commit and rollback
            std::mt19937 gen(std::random_device{}());
            std::uniform_int_distribution<> dist(0, 1);
            bool success;
            
            if (dist(gen) == 0) {
                success = coordinator.commit();
            } else {
                success = coordinator.rollback();
            }

            if (success) {
                successCount++;
            } else {
                failureCount++;
            }
        });
    }

    // Wait for all threads to complete
    for (auto& thread : threads) {
        thread.join();
    }

    // We should have exactly numThreads operations complete (some succeed, some fail)
    REQUIRE(successCount + failureCount == numThreads);
}

TEST_CASE("TransactionCoordinator correctly handles participants' order", "[TransactionCoordinator]") {
    TransactionCoordinator coordinator;
    coordinator.begin();

    std::vector<std::string> prepareOrder;
    std::vector<std::string> commitOrder;
    std::vector<std::string> compensateOrder;

    class OrderTrackingParticipant : public TransactionParticipant {
    public:
        OrderTrackingParticipant(std::string name, std::vector<std::string>& prepareOrder,
                               std::vector<std::string>& commitOrder, 
                               std::vector<std::string>& compensateOrder)
            : name_(std::move(name)), 
              prepareOrder_(prepareOrder),
              commitOrder_(commitOrder),
              compensateOrder_(compensateOrder) {}

        bool prepare() override {
            prepareOrder_.push_back(name_);
            return true;
        }

        bool commit() override {
            commitOrder_.push_back(name_);
            return true;
        }

        bool compensate() override {
            compensateOrder_.push_back(name_);
            return true;
        }

    private:
        std::string name_;
        std::vector<std::string>& prepareOrder_;
        std::vector<std::string>& commitOrder_;
        std::vector<std::string>& compensateOrder_;
    };

    auto p1 = std::make_shared<OrderTrackingParticipant>("P1", prepareOrder, commitOrder, compensateOrder);
    auto p2 = std::make_shared<OrderTrackingParticipant>("P2", prepareOrder, commitOrder, compensateOrder);
    auto p3 = std::make_shared<OrderTrackingParticipant>("P3", prepareOrder, commitOrder, compensateOrder);

    coordinator.enroll(p1);
    coordinator.enroll(p2);
    coordinator.enroll(p3);

    bool result = coordinator.commit();
    REQUIRE(result == true);

    // Check prepare and commit order is in order of enrollment
    REQUIRE(prepareOrder == std::vector<std::string>({"P1", "P2", "P3"}));
    REQUIRE(commitOrder == std::vector<std::string>({"P1", "P2", "P3"}));

    // Start a new transaction for rollback test
    coordinator.begin();
    coordinator.enroll(p1);
    coordinator.enroll(p2);
    coordinator.enroll(p3);

    compensateOrder.clear();
    result = coordinator.rollback();
    REQUIRE(result == true);

    // Check compensate order is reverse of enrollment
    REQUIRE(compensateOrder == std::vector<std::string>({"P3", "P2", "P1"}));
}

TEST_CASE("TransactionCoordinator is idempotent", "[TransactionCoordinator]") {
    TransactionCoordinator coordinator;
    coordinator.begin();

    auto participant = std::make_shared<MockParticipant>("Participant");
    coordinator.enroll(participant);
    
    // Enroll the same participant multiple times
    coordinator.enroll(participant);
    coordinator.enroll(participant);

    bool result = coordinator.commit();
    REQUIRE(result == true);
    
    // Even though we enrolled the participant multiple times,
    // the operations should only be called once on it
    REQUIRE(participant->getPrepareCallCount() == 1);
    REQUIRE(participant->getCommitCallCount() == 1);
}