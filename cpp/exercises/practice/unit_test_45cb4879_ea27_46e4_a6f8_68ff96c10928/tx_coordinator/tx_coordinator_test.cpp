#include "tx_coordinator.h"
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include "catch.hpp"

using namespace std;

class MockService : public Service {
public:
    MockService(int id, bool prepareSuccess, bool commitSuccess, bool rollbackSuccess)
        : id_(id), prepareSuccess_(prepareSuccess), 
          commitSuccess_(commitSuccess), rollbackSuccess_(rollbackSuccess) {}

    bool Prepare() override {
        return prepareSuccess_;
    }

    bool Commit() override {
        return commitSuccess_;
    }

    bool Rollback() override {
        return rollbackSuccess_;
    }

    int GetId() override {
        return id_;
    }

private:
    int id_;
    bool prepareSuccess_;
    bool commitSuccess_;
    bool rollbackSuccess_;
};

TEST_CASE("Single service successful transaction") {
    TransactionCoordinator coordinator;
    auto service = make_shared<MockService>(1, true, true, true);
    coordinator.RegisterService(service.get());
    
    vector<Service*> services = {service.get()};
    REQUIRE(coordinator.BeginTransaction(services) == true);
}

TEST_CASE("Single service failed prepare") {
    TransactionCoordinator coordinator;
    auto service = make_shared<MockService>(1, false, true, true);
    coordinator.RegisterService(service.get());
    
    vector<Service*> services = {service.get()};
    REQUIRE(coordinator.BeginTransaction(services) == false);
}

TEST_CASE("Multiple services all successful") {
    TransactionCoordinator coordinator;
    auto service1 = make_shared<MockService>(1, true, true, true);
    auto service2 = make_shared<MockService>(2, true, true, true);
    coordinator.RegisterService(service1.get());
    coordinator.RegisterService(service2.get());
    
    vector<Service*> services = {service1.get(), service2.get()};
    REQUIRE(coordinator.BeginTransaction(services) == true);
}

TEST_CASE("Multiple services one fails prepare") {
    TransactionCoordinator coordinator;
    auto service1 = make_shared<MockService>(1, true, true, true);
    auto service2 = make_shared<MockService>(2, false, true, true);
    coordinator.RegisterService(service1.get());
    coordinator.RegisterService(service2.get());
    
    vector<Service*> services = {service1.get(), service2.get()};
    REQUIRE(coordinator.BeginTransaction(services) == false);
}

TEST_CASE("Concurrent transactions") {
    TransactionCoordinator coordinator;
    auto service1 = make_shared<MockService>(1, true, true, true);
    auto service2 = make_shared<MockService>(2, true, true, true);
    coordinator.RegisterService(service1.get());
    coordinator.RegisterService(service2.get());
    
    atomic<int> successCount(0);
    vector<thread> threads;
    
    for (int i = 0; i < 10; ++i) {
        threads.emplace_back([&]() {
            vector<Service*> services = {service1.get(), service2.get()};
            if (coordinator.BeginTransaction(services)) {
                successCount++;
            }
        });
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    REQUIRE(successCount == 10);
}

TEST_CASE("Service timeout during prepare") {
    TransactionCoordinator coordinator;
    auto service = make_shared<MockService>(1, false, false, false);
    coordinator.RegisterService(service.get());
    
    vector<Service*> services = {service.get()};
    REQUIRE(coordinator.BeginTransaction(services) == false);
}

TEST_CASE("Unregistered service") {
    TransactionCoordinator coordinator;
    auto service = make_shared<MockService>(1, true, true, true);
    
    vector<Service*> services = {service.get()};
    REQUIRE_THROWS_AS(coordinator.BeginTransaction(services), std::runtime_error);
}

TEST_CASE("Service failure during commit") {
    TransactionCoordinator coordinator;
    auto service1 = make_shared<MockService>(1, true, false, true);
    auto service2 = make_shared<MockService>(2, true, true, true);
    coordinator.RegisterService(service1.get());
    coordinator.RegisterService(service2.get());
    
    vector<Service*> services = {service1.get(), service2.get()};
    REQUIRE(coordinator.BeginTransaction(services) == false);
}

TEST_CASE("Service failure during rollback") {
    TransactionCoordinator coordinator;
    auto service1 = make_shared<MockService>(1, false, true, false);
    auto service2 = make_shared<MockService>(2, true, true, true);
    coordinator.RegisterService(service1.get());
    coordinator.RegisterService(service2.get());
    
    vector<Service*> services = {service1.get(), service2.get()};
    REQUIRE(coordinator.BeginTransaction(services) == false);
}

TEST_CASE("Mixed success/failure scenarios") {
    TransactionCoordinator coordinator;
    auto service1 = make_shared<MockService>(1, true, true, true);
    auto service2 = make_shared<MockService>(2, false, true, false);
    auto service3 = make_shared<MockService>(3, true, false, true);
    coordinator.RegisterService(service1.get());
    coordinator.RegisterService(service2.get());
    coordinator.RegisterService(service3.get());
    
    vector<Service*> services = {service1.get(), service2.get(), service3.get()};
    REQUIRE(coordinator.BeginTransaction(services) == false);
}