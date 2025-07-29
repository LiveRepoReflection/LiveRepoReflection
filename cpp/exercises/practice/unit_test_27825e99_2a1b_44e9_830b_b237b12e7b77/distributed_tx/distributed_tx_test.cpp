#include <atomic>
#include <chrono>
#include <functional>
#include <memory>
#include <thread>
#include <vector>
#include "catch.hpp"
#include "distributed_tx.h"

// Mock service implementation for testing
class MockService : public Service {
public:
    MockService(bool willPrepare = true, 
                int prepareDelayMs = 0, 
                int commitDelayMs = 0,
                int rollbackDelayMs = 0)
        : prepared_(false), 
          committed_(false), 
          rolledBack_(false),
          willPrepare_(willPrepare),
          prepareDelayMs_(prepareDelayMs),
          commitDelayMs_(commitDelayMs),
          rollbackDelayMs_(rollbackDelayMs) {}

    bool Prepare() override {
        if (prepareDelayMs_ > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(prepareDelayMs_));
        }
        prepared_ = willPrepare_;
        return willPrepare_;
    }

    void Commit() override {
        if (commitDelayMs_ > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(commitDelayMs_));
        }
        committed_ = true;
    }

    void Rollback() override {
        if (rollbackDelayMs_ > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(rollbackDelayMs_));
        }
        rolledBack_ = true;
    }

    bool IsPrepared() const { return prepared_; }
    bool IsCommitted() const { return committed_; }
    bool IsRolledBack() const { return rolledBack_; }

private:
    std::atomic<bool> prepared_;
    std::atomic<bool> committed_;
    std::atomic<bool> rolledBack_;
    bool willPrepare_;
    int prepareDelayMs_;
    int commitDelayMs_;
    int rollbackDelayMs_;
};

TEST_CASE("Begin Transaction", "[transaction]") {
    DistributedTransactionManager dtm;
    
    int tid1 = dtm.BeginTransaction();
    int tid2 = dtm.BeginTransaction();
    
    REQUIRE(tid1 > 0);
    REQUIRE(tid2 > 0);
    REQUIRE(tid1 != tid2);
}

TEST_CASE("Enlist Service", "[transaction]") {
    DistributedTransactionManager dtm;
    int tid = dtm.BeginTransaction();
    
    auto service1 = std::make_shared<MockService>();
    auto service2 = std::make_shared<MockService>();
    
    SECTION("Enlisting valid service") {
        REQUIRE(dtm.Enlist(tid, service1));
    }
    
    SECTION("Enlisting same service twice") {
        REQUIRE(dtm.Enlist(tid, service1));
        REQUIRE_FALSE(dtm.Enlist(tid, service1));
    }
    
    SECTION("Enlisting service with invalid TID") {
        REQUIRE_FALSE(dtm.Enlist(-1, service1));
        REQUIRE_FALSE(dtm.Enlist(0, service1));
        REQUIRE_FALSE(dtm.Enlist(999999, service1)); // Assuming this TID doesn't exist
    }
    
    SECTION("Enlisting multiple services") {
        REQUIRE(dtm.Enlist(tid, service1));
        REQUIRE(dtm.Enlist(tid, service2));
    }
}

TEST_CASE("Prepare Transaction", "[transaction]") {
    DistributedTransactionManager dtm;
    int tid = dtm.BeginTransaction();
    
    SECTION("Prepare with all services ready") {
        auto service1 = std::make_shared<MockService>(true); // Will prepare successfully
        auto service2 = std::make_shared<MockService>(true); // Will prepare successfully
        
        REQUIRE(dtm.Enlist(tid, service1));
        REQUIRE(dtm.Enlist(tid, service2));
        
        REQUIRE(dtm.Prepare(tid));
        REQUIRE(service1->IsPrepared());
        REQUIRE(service2->IsPrepared());
    }
    
    SECTION("Prepare with one service failing") {
        auto service1 = std::make_shared<MockService>(true);  // Will prepare successfully
        auto service2 = std::make_shared<MockService>(false); // Will fail to prepare
        
        REQUIRE(dtm.Enlist(tid, service1));
        REQUIRE(dtm.Enlist(tid, service2));
        
        REQUIRE_FALSE(dtm.Prepare(tid));
        REQUIRE(service1->IsPrepared());
        REQUIRE_FALSE(service2->IsPrepared());
        // Should automatically rollback on prepare failure
        REQUIRE(service1->IsRolledBack());
    }
    
    SECTION("Prepare with invalid TID") {
        REQUIRE_FALSE(dtm.Prepare(-1));
        REQUIRE_FALSE(dtm.Prepare(0));
        REQUIRE_FALSE(dtm.Prepare(999999)); // Assuming this TID doesn't exist
    }
    
    SECTION("Prepare with no enlisted services") {
        REQUIRE(dtm.Prepare(tid)); // Should succeed trivially
    }
}

TEST_CASE("Commit Transaction", "[transaction]") {
    DistributedTransactionManager dtm;
    int tid = dtm.BeginTransaction();
    
    SECTION("Commit after successful prepare") {
        auto service1 = std::make_shared<MockService>();
        auto service2 = std::make_shared<MockService>();
        
        REQUIRE(dtm.Enlist(tid, service1));
        REQUIRE(dtm.Enlist(tid, service2));
        
        REQUIRE(dtm.Prepare(tid));
        REQUIRE(dtm.Commit(tid));
        
        REQUIRE(service1->IsCommitted());
        REQUIRE(service2->IsCommitted());
    }
    
    SECTION("Commit without prepare") {
        auto service = std::make_shared<MockService>();
        
        REQUIRE(dtm.Enlist(tid, service));
        REQUIRE_FALSE(dtm.Commit(tid));
        REQUIRE_FALSE(service->IsCommitted());
    }
    
    SECTION("Commit after failed prepare") {
        auto service1 = std::make_shared<MockService>(true);  // Will prepare successfully
        auto service2 = std::make_shared<MockService>(false); // Will fail to prepare
        
        REQUIRE(dtm.Enlist(tid, service1));
        REQUIRE(dtm.Enlist(tid, service2));
        
        REQUIRE_FALSE(dtm.Prepare(tid));
        REQUIRE_FALSE(dtm.Commit(tid));
        
        REQUIRE_FALSE(service1->IsCommitted());
        REQUIRE_FALSE(service2->IsCommitted());
    }
    
    SECTION("Commit with invalid TID") {
        REQUIRE_FALSE(dtm.Commit(-1));
        REQUIRE_FALSE(dtm.Commit(0));
        REQUIRE_FALSE(dtm.Commit(999999)); // Assuming this TID doesn't exist
    }
}

TEST_CASE("Rollback Transaction", "[transaction]") {
    DistributedTransactionManager dtm;
    int tid = dtm.BeginTransaction();
    
    SECTION("Explicit rollback after enlist") {
        auto service1 = std::make_shared<MockService>();
        auto service2 = std::make_shared<MockService>();
        
        REQUIRE(dtm.Enlist(tid, service1));
        REQUIRE(dtm.Enlist(tid, service2));
        
        REQUIRE(dtm.Rollback(tid));
        
        REQUIRE(service1->IsRolledBack());
        REQUIRE(service2->IsRolledBack());
    }
    
    SECTION("Explicit rollback after successful prepare") {
        auto service1 = std::make_shared<MockService>();
        auto service2 = std::make_shared<MockService>();
        
        REQUIRE(dtm.Enlist(tid, service1));
        REQUIRE(dtm.Enlist(tid, service2));
        
        REQUIRE(dtm.Prepare(tid));
        REQUIRE(dtm.Rollback(tid));
        
        REQUIRE(service1->IsRolledBack());
        REQUIRE(service2->IsRolledBack());
    }
    
    SECTION("Implicit rollback after failed prepare") {
        auto service1 = std::make_shared<MockService>(true);  // Will prepare successfully
        auto service2 = std::make_shared<MockService>(false); // Will fail to prepare
        
        REQUIRE(dtm.Enlist(tid, service1));
        REQUIRE(dtm.Enlist(tid, service2));
        
        REQUIRE_FALSE(dtm.Prepare(tid));
        
        // Services should be rolled back automatically
        REQUIRE(service1->IsRolledBack());
        REQUIRE(service2->IsRolledBack());
    }
    
    SECTION("Rollback with invalid TID") {
        REQUIRE_FALSE(dtm.Rollback(-1));
        REQUIRE_FALSE(dtm.Rollback(0));
        REQUIRE_FALSE(dtm.Rollback(999999)); // Assuming this TID doesn't exist
    }
}

TEST_CASE("Concurrency", "[transaction][concurrency]") {
    DistributedTransactionManager dtm;
    std::atomic<int> successCount(0);
    std::atomic<int> failureCount(0);
    
    std::vector<std::thread> threads;
    const int numThreads = 10;
    
    for (int i = 0; i < numThreads; ++i) {
        threads.emplace_back([&dtm, &successCount, &failureCount, i]() {
            int tid = dtm.BeginTransaction();
            
            auto service1 = std::make_shared<MockService>(true, i % 5); // Variable delay
            auto service2 = std::make_shared<MockService>(i % 3 != 0);  // Some will fail
            
            if (dtm.Enlist(tid, service1) && dtm.Enlist(tid, service2)) {
                if (dtm.Prepare(tid)) {
                    if (dtm.Commit(tid)) {
                        successCount++;
                    } else {
                        failureCount++;
                    }
                } else {
                    failureCount++;
                }
            } else {
                failureCount++;
            }
        });
    }
    
    for (auto& thread : threads) {
        thread.join();
    }
    
    REQUIRE(successCount + failureCount == numThreads);
    // We can't assert exact counts since it depends on timing
}

TEST_CASE("Service delays", "[transaction][timing]") {
    DistributedTransactionManager dtm;
    int tid = dtm.BeginTransaction();
    
    auto slowPrepareService = std::make_shared<MockService>(true, 100, 0, 0); // 100ms prepare delay
    auto slowCommitService = std::make_shared<MockService>(true, 0, 100, 0);  // 100ms commit delay
    auto slowRollbackService = std::make_shared<MockService>(false, 0, 0, 100); // 100ms rollback delay
    
    REQUIRE(dtm.Enlist(tid, slowPrepareService));
    REQUIRE(dtm.Enlist(tid, slowCommitService));
    REQUIRE(dtm.Enlist(tid, slowRollbackService));
    
    auto startTime = std::chrono::steady_clock::now();
    bool prepareResult = dtm.Prepare(tid);
    auto prepareTime = std::chrono::steady_clock::now() - startTime;
    
    REQUIRE_FALSE(prepareResult);
    // Since all services' prepare operations are executed in parallel,
    // the preparation time should be roughly equal to the longest prepare time
    // plus any overhead for rollback (which happens on failure)
    
    auto rollbackDuration = std::chrono::duration_cast<std::chrono::milliseconds>(prepareTime).count();
    // This could be flaky on different machines, but the time should be at least
    // the prepare delay plus some overhead
    REQUIRE(rollbackDuration >= 100);
    
    // After failed prepare, all services should be rolled back
    REQUIRE(slowPrepareService->IsRolledBack());
    REQUIRE(slowCommitService->IsRolledBack());
    REQUIRE(slowRollbackService->IsRolledBack());
}

TEST_CASE("Multiple transactions", "[transaction]") {
    DistributedTransactionManager dtm;
    
    // Create multiple transactions
    int tid1 = dtm.BeginTransaction();
    int tid2 = dtm.BeginTransaction();
    int tid3 = dtm.BeginTransaction();
    
    auto service1 = std::make_shared<MockService>(true);
    auto service2 = std::make_shared<MockService>(true);
    auto service3 = std::make_shared<MockService>(false);
    
    // Transaction 1: enlist, prepare, commit
    REQUIRE(dtm.Enlist(tid1, service1));
    REQUIRE(dtm.Prepare(tid1));
    REQUIRE(dtm.Commit(tid1));
    
    // Transaction 2: enlist, rollback
    REQUIRE(dtm.Enlist(tid2, service2));
    REQUIRE(dtm.Rollback(tid2));
    
    // Transaction 3: enlist, prepare (fails), implicit rollback
    REQUIRE(dtm.Enlist(tid3, service3));
    REQUIRE_FALSE(dtm.Prepare(tid3));
    
    // Verify state
    REQUIRE(service1->IsCommitted());
    REQUIRE_FALSE(service1->IsRolledBack());
    
    REQUIRE_FALSE(service2->IsCommitted());
    REQUIRE(service2->IsRolledBack());
    
    REQUIRE_FALSE(service3->IsCommitted());
    REQUIRE(service3->IsRolledBack());
}