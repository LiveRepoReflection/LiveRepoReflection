#include <chrono>
#include <thread>
#include "catch.hpp"
#include "distributed_tx.h"

class MockParticipant : public IParticipant {
public:
    MockParticipant(bool willSucceed = true, bool shouldTimeout = false) 
        : willSucceed_(willSucceed), shouldTimeout_(shouldTimeout) {}

    PrepareResult prepare() override {
        if (shouldTimeout_) {
            std::this_thread::sleep_for(std::chrono::seconds(5));
        }
        prepared_ = willSucceed_;
        return willSucceed_ ? PrepareResult::READY : PrepareResult::ABORT;
    }

    bool commit() override {
        if (!prepared_) return false;
        if (shouldTimeout_) {
            std::this_thread::sleep_for(std::chrono::seconds(5));
        }
        committed_ = willSucceed_;
        return willSucceed_;
    }

    bool rollback() override {
        if (shouldTimeout_) {
            std::this_thread::sleep_for(std::chrono::seconds(5));
        }
        prepared_ = false;
        committed_ = false;
        return true;
    }

    bool isCommitted() const { return committed_; }
    bool isPrepared() const { return prepared_; }

private:
    bool willSucceed_;
    bool shouldTimeout_;
    bool prepared_ = false;
    bool committed_ = false;
};

TEST_CASE("Single participant successful transaction") {
    TransactionCoordinator coordinator;
    auto participant = std::make_shared<MockParticipant>(true);
    std::vector<std::shared_ptr<IParticipant>> participants = {participant};
    
    REQUIRE(coordinator.executeTransaction(participants) == TransactionResult::COMMITTED);
    REQUIRE(participant->isCommitted());
}

TEST_CASE("Single participant failed preparation") {
    TransactionCoordinator coordinator;
    auto participant = std::make_shared<MockParticipant>(false);
    std::vector<std::shared_ptr<IParticipant>> participants = {participant};
    
    REQUIRE(coordinator.executeTransaction(participants) == TransactionResult::ABORTED);
    REQUIRE_FALSE(participant->isCommitted());
}

TEST_CASE("Multiple participants successful transaction") {
    TransactionCoordinator coordinator;
    auto p1 = std::make_shared<MockParticipant>(true);
    auto p2 = std::make_shared<MockParticipant>(true);
    auto p3 = std::make_shared<MockParticipant>(true);
    std::vector<std::shared_ptr<IParticipant>> participants = {p1, p2, p3};
    
    REQUIRE(coordinator.executeTransaction(participants) == TransactionResult::COMMITTED);
    REQUIRE(p1->isCommitted());
    REQUIRE(p2->isCommitted());
    REQUIRE(p3->isCommitted());
}

TEST_CASE("Multiple participants with one failure") {
    TransactionCoordinator coordinator;
    auto p1 = std::make_shared<MockParticipant>(true);
    auto p2 = std::make_shared<MockParticipant>(false);
    auto p3 = std::make_shared<MockParticipant>(true);
    std::vector<std::shared_ptr<IParticipant>> participants = {p1, p2, p3};
    
    REQUIRE(coordinator.executeTransaction(participants) == TransactionResult::ABORTED);
    REQUIRE_FALSE(p1->isCommitted());
    REQUIRE_FALSE(p2->isCommitted());
    REQUIRE_FALSE(p3->isCommitted());
}

TEST_CASE("Participant timeout during prepare phase") {
    TransactionCoordinator coordinator;
    auto p1 = std::make_shared<MockParticipant>(true);
    auto p2 = std::make_shared<MockParticipant>(true, true);  // Will timeout
    std::vector<std::shared_ptr<IParticipant>> participants = {p1, p2};
    
    REQUIRE(coordinator.executeTransaction(participants) == TransactionResult::TIMEOUT);
    REQUIRE_FALSE(p1->isCommitted());
    REQUIRE_FALSE(p2->isCommitted());
}

TEST_CASE("Concurrent transactions") {
    TransactionCoordinator coordinator;
    std::vector<std::future<TransactionResult>> futures;
    
    for (int i = 0; i < 5; ++i) {
        futures.push_back(std::async(std::launch::async, [&coordinator]() {
            auto p1 = std::make_shared<MockParticipant>(true);
            auto p2 = std::make_shared<MockParticipant>(true);
            std::vector<std::shared_ptr<IParticipant>> participants = {p1, p2};
            return coordinator.executeTransaction(participants);
        }));
    }
    
    for (auto& future : futures) {
        REQUIRE(future.get() == TransactionResult::COMMITTED);
    }
}

TEST_CASE("Empty participant list") {
    TransactionCoordinator coordinator;
    std::vector<std::shared_ptr<IParticipant>> participants;
    
    REQUIRE(coordinator.executeTransaction(participants) == TransactionResult::INVALID);
}

TEST_CASE("Null participant") {
    TransactionCoordinator coordinator;
    std::vector<std::shared_ptr<IParticipant>> participants = {nullptr};
    
    REQUIRE(coordinator.executeTransaction(participants) == TransactionResult::INVALID);
}

TEST_CASE("Maximum participants exceeded") {
    TransactionCoordinator coordinator;
    std::vector<std::shared_ptr<IParticipant>> participants;
    
    for (int i = 0; i < 1000; ++i) {
        participants.push_back(std::make_shared<MockParticipant>(true));
    }
    
    REQUIRE(coordinator.executeTransaction(participants) == TransactionResult::INVALID);
}