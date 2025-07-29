#include <chrono>
#include <future>
#include <iostream>
#include <map>
#include <mutex>
#include <random>
#include <thread>
#include <vector>
#include <sstream>
#include <string>

#include "catch.hpp"
#include "tx_coordinator.h"

// Mock service implementation for testing
class MockService : public ServiceInterface {
public:
    MockService(const std::string& id, bool alwaysSucceed = true, int delayMs = 5)
        : id_(id), alwaysSucceed_(alwaysSucceed), delayMs_(delayMs), isPrepared_(false) {
    }

    bool prepare(int transactionId) override {
        std::this_thread::sleep_for(std::chrono::milliseconds(delayMs_));
        
        std::lock_guard<std::mutex> lock(mutex_);
        if (isPrepared_) {
            return false; // Service is already prepared for another transaction
        }
        
        isPrepared_ = true;
        preparedTxId_ = transactionId;
        return alwaysSucceed_;
    }

    bool commit(int transactionId) override {
        std::this_thread::sleep_for(std::chrono::milliseconds(delayMs_));
        
        std::lock_guard<std::mutex> lock(mutex_);
        if (!isPrepared_ || preparedTxId_ != transactionId) {
            return false;
        }
        
        isPrepared_ = false;
        return true;
    }

    bool rollback(int transactionId) override {
        std::this_thread::sleep_for(std::chrono::milliseconds(delayMs_));
        
        std::lock_guard<std::mutex> lock(mutex_);
        if (isPrepared_ && preparedTxId_ == transactionId) {
            isPrepared_ = false;
        }
        return true;
    }

    void setTimeout(bool shouldTimeout) {
        std::lock_guard<std::mutex> lock(mutex_);
        delayMs_ = shouldTimeout ? 100 : 5;
    }

    void setAlwaysSucceed(bool succeed) {
        std::lock_guard<std::mutex> lock(mutex_);
        alwaysSucceed_ = succeed;
    }

    bool isPrepared() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return isPrepared_;
    }

private:
    std::string id_;
    bool alwaysSucceed_;
    int delayMs_;
    bool isPrepared_;
    int preparedTxId_;
    mutable std::mutex mutex_;
};

// Helper function to create a set of mock services
std::map<std::string, std::shared_ptr<ServiceInterface>> createMockServices(
    const std::vector<std::string>& serviceIds,
    bool alwaysSucceed = true,
    int delayMs = 5) {
    
    std::map<std::string, std::shared_ptr<ServiceInterface>> services;
    for (const auto& id : serviceIds) {
        services[id] = std::make_shared<MockService>(id, alwaysSucceed, delayMs);
    }
    return services;
}

TEST_CASE("Basic transaction with all services voting commit", "[basic]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3"};
    auto services = createMockServices(serviceIds);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    int txId = 100;
    std::vector<std::string> involvedServices = {"service1", "service2"};
    
    auto result = coordinator.processTransaction(txId, involvedServices);
    REQUIRE(result == "COMMIT 100");
}

TEST_CASE("Transaction with one service voting abort", "[basic]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3"};
    auto services = createMockServices(serviceIds);
    
    // Make service2 always vote abort
    auto service2 = std::static_pointer_cast<MockService>(services["service2"]);
    service2->setAlwaysSucceed(false);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    int txId = 101;
    std::vector<std::string> involvedServices = {"service1", "service2"};
    
    auto result = coordinator.processTransaction(txId, involvedServices);
    REQUIRE(result == "ABORT 101");
}

TEST_CASE("Transaction with service timeout", "[timeout]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3"};
    auto services = createMockServices(serviceIds);
    
    // Make service2 timeout
    auto service2 = std::static_pointer_cast<MockService>(services["service2"]);
    service2->setTimeout(true);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    int txId = 102;
    std::vector<std::string> involvedServices = {"service1", "service2"};
    
    auto result = coordinator.processTransaction(txId, involvedServices);
    REQUIRE(result == "ABORT 102");
}

TEST_CASE("Multiple concurrent transactions", "[concurrent]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3"};
    auto services = createMockServices(serviceIds);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    auto tx1 = std::async(std::launch::async, [&]() {
        return coordinator.processTransaction(103, {"service1", "service2"});
    });
    
    auto tx2 = std::async(std::launch::async, [&]() {
        return coordinator.processTransaction(104, {"service2", "service3"});
    });
    
    std::string result1 = tx1.get();
    std::string result2 = tx2.get();
    
    bool bothCommitted = (result1 == "COMMIT 103" && result2 == "COMMIT 104");
    bool oneAborted = (result1 == "ABORT 103" || result2 == "ABORT 104");
    
    // Either both commit or at least one aborts due to service contention
    REQUIRE((bothCommitted || oneAborted));
}

TEST_CASE("Services involved in multiple transactions", "[multiple]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3"};
    auto services = createMockServices(serviceIds);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    // Process first transaction
    auto result1 = coordinator.processTransaction(105, {"service1", "service2"});
    
    // Process second transaction involving the same services
    auto result2 = coordinator.processTransaction(106, {"service1", "service2"});
    
    REQUIRE((result1 == "COMMIT 105" || result1 == "ABORT 105"));
    REQUIRE((result2 == "COMMIT 106" || result2 == "ABORT 106"));
}

TEST_CASE("Large number of transactions", "[stress]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3", "service4", "service5"};
    auto services = createMockServices(serviceIds);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    const int numTransactions = 50;
    std::vector<std::future<std::string>> futures;
    
    for (int i = 0; i < numTransactions; i++) {
        int txId = 1000 + i;
        
        // Randomly select 2-3 services
        std::vector<std::string> involvedServices;
        int numServices = 2 + (i % 2); // Either 2 or 3 services
        for (int j = 0; j < numServices; j++) {
            involvedServices.push_back(serviceIds[j % serviceIds.size()]);
        }
        
        futures.push_back(std::async(std::launch::async, [&coordinator, txId, involvedServices]() {
            return coordinator.processTransaction(txId, involvedServices);
        }));
    }
    
    // Wait for all transactions to complete
    for (auto& future : futures) {
        std::string result = future.get();
        REQUIRE((result.find("COMMIT") == 0 || result.find("ABORT") == 0));
    }
}

TEST_CASE("Transaction with a single service", "[edge_case]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3"};
    auto services = createMockServices(serviceIds);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    int txId = 107;
    std::vector<std::string> involvedServices = {"service1"};
    
    auto result = coordinator.processTransaction(txId, involvedServices);
    REQUIRE(result == "COMMIT 107");
}

TEST_CASE("Transaction with non-existent service", "[error]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3"};
    auto services = createMockServices(serviceIds);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    int txId = 108;
    std::vector<std::string> involvedServices = {"service1", "nonexistent"};
    
    auto result = coordinator.processTransaction(txId, involvedServices);
    REQUIRE(result == "ABORT 108");
}

TEST_CASE("Empty transaction", "[edge_case]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3"};
    auto services = createMockServices(serviceIds);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    int txId = 109;
    std::vector<std::string> involvedServices;
    
    auto result = coordinator.processTransaction(txId, involvedServices);
    REQUIRE(result == "COMMIT 109");
}

TEST_CASE("Service cleanup after transaction", "[cleanup]") {
    std::vector<std::string> serviceIds = {"service1"};
    auto services = createMockServices(serviceIds);
    
    auto mockService = std::static_pointer_cast<MockService>(services["service1"]);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    // Successful transaction
    auto result1 = coordinator.processTransaction(110, {"service1"});
    REQUIRE(result1 == "COMMIT 110");
    REQUIRE_FALSE(mockService->isPrepared());
    
    // Failed transaction
    mockService->setAlwaysSucceed(false);
    auto result2 = coordinator.processTransaction(111, {"service1"});
    REQUIRE(result2 == "ABORT 111");
    REQUIRE_FALSE(mockService->isPrepared());
}

TEST_CASE("Process batch of transactions", "[batch]") {
    std::vector<std::string> serviceIds = {"service1", "service2", "service3"};
    auto services = createMockServices(serviceIds);
    
    TransactionCoordinator coordinator(services, 50); // 50ms timeout
    
    std::vector<std::pair<int, std::vector<std::string>>> transactions = {
        {200, {"service1", "service2"}},
        {201, {"service2", "service3"}},
        {202, {"service1", "service3"}},
        {203, {"service1", "service2", "service3"}}
    };
    
    std::vector<std::string> results = coordinator.processTransactions(transactions);
    
    REQUIRE(results.size() == 4);
    for (const auto& result : results) {
        REQUIRE((result.find("COMMIT") == 0 || result.find("ABORT") == 0));
    }
}