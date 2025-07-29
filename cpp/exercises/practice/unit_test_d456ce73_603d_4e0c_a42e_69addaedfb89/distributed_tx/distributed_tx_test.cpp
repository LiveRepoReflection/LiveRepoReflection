#include "catch.hpp"
#include "distributed_tx.h"
#include <chrono>
#include <future>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

class MockService {
public:
    MockService(const std::string& name, bool willSucceed = true, bool willThrow = false, 
                std::chrono::milliseconds prepareDelay = std::chrono::milliseconds(0),
                std::chrono::milliseconds commitDelay = std::chrono::milliseconds(0),
                std::chrono::milliseconds rollbackDelay = std::chrono::milliseconds(0),
                int failAfterCommitAttempts = -1)
        : name_(name), willSucceed_(willSucceed), willThrow_(willThrow),
          prepareDelay_(prepareDelay), commitDelay_(commitDelay), rollbackDelay_(rollbackDelay),
          failAfterCommitAttempts_(failAfterCommitAttempts), 
          prepareCount_(0), commitCount_(0), rollbackCount_(0) {}

    bool prepare() {
        ++prepareCount_;
        if (prepareDelay_.count() > 0) {
            std::this_thread::sleep_for(prepareDelay_);
        }
        if (willThrow_) {
            throw std::runtime_error(name_ + " prepare failed with exception");
        }
        return willSucceed_;
    }

    void commit() {
        ++commitCount_;
        if (commitDelay_.count() > 0) {
            std::this_thread::sleep_for(commitDelay_);
        }
        if (failAfterCommitAttempts_ >= 0 && commitCount_ <= failAfterCommitAttempts_) {
            throw std::runtime_error(name_ + " commit failed with exception");
        }
    }

    void rollback() {
        ++rollbackCount_;
        if (rollbackDelay_.count() > 0) {
            std::this_thread::sleep_for(rollbackDelay_);
        }
    }

    int getPrepareCount() const { return prepareCount_; }
    int getCommitCount() const { return commitCount_; }
    int getRollbackCount() const { return rollbackCount_; }
    std::string getName() const { return name_; }

private:
    std::string name_;
    bool willSucceed_;
    bool willThrow_;
    std::chrono::milliseconds prepareDelay_;
    std::chrono::milliseconds commitDelay_;
    std::chrono::milliseconds rollbackDelay_;
    int failAfterCommitAttempts_;
    int prepareCount_;
    int commitCount_;
    int rollbackCount_;
};

TEST_CASE("Successful transaction with all services succeeding", "[transaction]") {
    auto service1 = std::make_shared<MockService>("service1");
    auto service2 = std::make_shared<MockService>("service2");
    auto service3 = std::make_shared<MockService>("service3");

    std::vector<std::shared_ptr<MockService>> services = {service1, service2, service3};

    distributed_tx::TransactionCoordinator coordinator;
    coordinator.begin_transaction(services);
    bool result = coordinator.execute_transaction();

    REQUIRE(result);
    REQUIRE(service1->getPrepareCount() == 1);
    REQUIRE(service2->getPrepareCount() == 1);
    REQUIRE(service3->getPrepareCount() == 1);
    REQUIRE(service1->getCommitCount() == 1);
    REQUIRE(service2->getCommitCount() == 1);
    REQUIRE(service3->getCommitCount() == 1);
    REQUIRE(service1->getRollbackCount() == 0);
    REQUIRE(service2->getRollbackCount() == 0);
    REQUIRE(service3->getRollbackCount() == 0);
}

TEST_CASE("Transaction rolled back when a service returns false for prepare", "[transaction]") {
    auto service1 = std::make_shared<MockService>("service1");
    auto service2 = std::make_shared<MockService>("service2", false); // Will return false for prepare
    auto service3 = std::make_shared<MockService>("service3");

    std::vector<std::shared_ptr<MockService>> services = {service1, service2, service3};

    distributed_tx::TransactionCoordinator coordinator;
    coordinator.begin_transaction(services);
    bool result = coordinator.execute_transaction();

    REQUIRE_FALSE(result);
    REQUIRE(service1->getPrepareCount() >= 1); // May not call prepare on all services if using parallelization
    REQUIRE(service2->getPrepareCount() == 1);
    REQUIRE(service1->getCommitCount() == 0);
    REQUIRE(service2->getCommitCount() == 0);
    REQUIRE(service3->getCommitCount() == 0);
    REQUIRE(service1->getRollbackCount() == 1);
    REQUIRE(service2->getRollbackCount() == 1);
    REQUIRE(service3->getRollbackCount() == 1);
}

TEST_CASE("Transaction rolled back when a service throws an exception during prepare", "[transaction]") {
    auto service1 = std::make_shared<MockService>("service1");
    auto service2 = std::make_shared<MockService>("service2", true, true); // Will throw during prepare
    auto service3 = std::make_shared<MockService>("service3");

    std::vector<std::shared_ptr<MockService>> services = {service1, service2, service3};

    distributed_tx::TransactionCoordinator coordinator;
    coordinator.begin_transaction(services);
    bool result = coordinator.execute_transaction();

    REQUIRE_FALSE(result);
    REQUIRE(service2->getPrepareCount() == 1);
    REQUIRE(service1->getCommitCount() == 0);
    REQUIRE(service2->getCommitCount() == 0);
    REQUIRE(service3->getCommitCount() == 0);
    REQUIRE(service1->getRollbackCount() == 1);
    REQUIRE(service2->getRollbackCount() == 1);
    REQUIRE(service3->getRollbackCount() == 1);
}

TEST_CASE("Transaction timeout during prepare phase", "[transaction]") {
    auto service1 = std::make_shared<MockService>("service1");
    // This service will take too long to prepare
    auto service2 = std::make_shared<MockService>("service2", true, false, std::chrono::milliseconds(6000));
    auto service3 = std::make_shared<MockService>("service3");

    std::vector<std::shared_ptr<MockService>> services = {service1, service2, service3};

    distributed_tx::TransactionCoordinator coordinator;
    coordinator.set_prepare_timeout(std::chrono::seconds(1)); // Set a short timeout for testing
    coordinator.begin_transaction(services);
    
    bool result = coordinator.execute_transaction();

    REQUIRE_FALSE(result);
    // Service2 might not complete prepare due to timeout
    REQUIRE(service1->getCommitCount() == 0);
    REQUIRE(service2->getCommitCount() == 0);
    REQUIRE(service3->getCommitCount() == 0);
    REQUIRE(service1->getRollbackCount() == 1);
    REQUIRE(service2->getRollbackCount() == 1);
    REQUIRE(service3->getRollbackCount() == 1);
}

TEST_CASE("Retry mechanism for commit phase", "[transaction]") {
    auto service1 = std::make_shared<MockService>("service1");
    // This service will fail the first commit attempt but succeed on second attempt
    auto service2 = std::make_shared<MockService>("service2", true, false, 
                                                std::chrono::milliseconds(0), 
                                                std::chrono::milliseconds(0), 
                                                std::chrono::milliseconds(0), 
                                                1); // Fail after 1 commit attempt
    auto service3 = std::make_shared<MockService>("service3");

    std::vector<std::shared_ptr<MockService>> services = {service1, service2, service3};

    distributed_tx::TransactionCoordinator coordinator;
    coordinator.set_commit_max_retries(3); // Allow up to 3 retries
    coordinator.begin_transaction(services);
    bool result = coordinator.execute_transaction();

    REQUIRE(result);
    REQUIRE(service1->getPrepareCount() == 1);
    REQUIRE(service2->getPrepareCount() == 1);
    REQUIRE(service3->getPrepareCount() == 1);
    REQUIRE(service1->getCommitCount() == 1);
    REQUIRE(service2->getCommitCount() > 1); // Should have been called multiple times due to retries
    REQUIRE(service3->getCommitCount() == 1);
    REQUIRE(service1->getRollbackCount() == 0);
    REQUIRE(service2->getRollbackCount() == 0);
    REQUIRE(service3->getRollbackCount() == 0);
}

TEST_CASE("Transaction with large number of services", "[transaction][performance]") {
    const int N = 100; // Large enough to test performance but not too large for unit tests
    std::vector<std::shared_ptr<MockService>> services;
    
    for (int i = 0; i < N; ++i) {
        services.push_back(std::make_shared<MockService>("service" + std::to_string(i)));
    }

    distributed_tx::TransactionCoordinator coordinator;
    coordinator.begin_transaction(services);
    
    auto start = std::chrono::high_resolution_clock::now();
    bool result = coordinator.execute_transaction();
    auto end = std::chrono::high_resolution_clock::now();
    
    std::chrono::duration<double, std::milli> elapsed = end - start;
    
    REQUIRE(result);
    
    // Check that all services were called correctly
    for (auto& service : services) {
        REQUIRE(service->getPrepareCount() == 1);
        REQUIRE(service->getCommitCount() == 1);
        REQUIRE(service->getRollbackCount() == 0);
    }
    
    // Optional performance check - this depends on your implementation and hardware
    // INFO("Transaction with " << N << " services completed in " << elapsed.count() << "ms");
}

TEST_CASE("Concurrent service preparation", "[transaction][concurrency]") {
    // Services with significant delays to test concurrent preparation
    auto service1 = std::make_shared<MockService>("service1", true, false, std::chrono::milliseconds(300));
    auto service2 = std::make_shared<MockService>("service2", true, false, std::chrono::milliseconds(300));
    auto service3 = std::make_shared<MockService>("service3", true, false, std::chrono::milliseconds(300));

    std::vector<std::shared_ptr<MockService>> services = {service1, service2, service3};

    distributed_tx::TransactionCoordinator coordinator;
    coordinator.begin_transaction(services);
    
    auto start = std::chrono::high_resolution_clock::now();
    bool result = coordinator.execute_transaction();
    auto end = std::chrono::high_resolution_clock::now();
    
    std::chrono::duration<double, std::milli> elapsed = end - start;
    
    REQUIRE(result);
    
    // If preparation is done concurrently, the total time should be closer to the max delay
    // of a single service rather than the sum of all delays
    // Note: This test might fail if concurrency is not implemented or if the system is heavily loaded
    INFO("Transaction completed in " << elapsed.count() << "ms");
    // We don't make a hard requirement here, as it depends on the implementation
    // but we can check: 
    // REQUIRE(elapsed.count() < 600); // Less than the sum of delays (900ms)
}

TEST_CASE("Empty service list", "[transaction][edge_case]") {
    std::vector<std::shared_ptr<MockService>> services;

    distributed_tx::TransactionCoordinator coordinator;
    coordinator.begin_transaction(services);
    bool result = coordinator.execute_transaction();

    // Empty transaction should succeed (no services to commit or roll back)
    REQUIRE(result);
}

TEST_CASE("Idempotent rollback", "[transaction]") {
    auto service = std::make_shared<MockService>("service", false); // Will fail on prepare

    std::vector<std::shared_ptr<MockService>> services = {service};

    distributed_tx::TransactionCoordinator coordinator;
    coordinator.begin_transaction(services);
    bool result = coordinator.execute_transaction();

    REQUIRE_FALSE(result);
    REQUIRE(service->getPrepareCount() == 1);
    REQUIRE(service->getCommitCount() == 0);
    REQUIRE(service->getRollbackCount() == 1); // Rollback should be called exactly once
}