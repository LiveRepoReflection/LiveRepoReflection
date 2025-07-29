#include "transaction_orchestrator.h"
#include "catch.hpp"
#include <chrono>
#include <thread>
#include <vector>
#include <future>
#include <memory>
#include <atomic>

// MockService implements the interface provided by ServiceInterface in the orchestrator.
// It simulates various service behaviors for testing purposes.
class MockService : public ServiceInterface {
public:
    enum Action {
        SUCCESS,
        ABORT,
        TIMEOUT
    };

    // delay_ms: delay (in milliseconds) before returning from prepare()
    MockService(Action act, int delay_ms = 0)
        : action(act), delay(delay_ms), commit_calls(0), abort_calls(0) {}

    // Simulate the prepare call. TIMEOUT is simulated by sleeping longer than the allowed timeout.
    bool prepare() override {
        if (delay > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(delay));
        }
        // For TIMEOUT, we simulate by returning false (not ready) after the delay.
        return action == SUCCESS;
    }

    void commit() override {
        ++commit_calls;
    }

    void abort() override {
        ++abort_calls;
    }

    Action action;
    int delay;
    std::atomic<int> commit_calls;
    std::atomic<int> abort_calls;
};

// Test that the transaction commits successfully when all services respond positively.
TEST_CASE("Transaction commits successfully when all services are ready") {
    MockService service1(MockService::SUCCESS);
    MockService service2(MockService::SUCCESS);
    std::vector<ServiceInterface*> services = { &service1, &service2 };
    // Timeout set to 1000ms.
    TransactionOrchestrator orchestrator(services, 1000);

    bool result = orchestrator.runTransaction();

    REQUIRE(result == true);
    REQUIRE(service1.commit_calls == 1);
    REQUIRE(service2.commit_calls == 1);
}

// Test that the transaction aborts if one of the services responds with an abort.
TEST_CASE("Transaction aborts when one service is not ready") {
    MockService service1(MockService::SUCCESS);
    MockService service2(MockService::ABORT);
    std::vector<ServiceInterface*> services = { &service1, &service2 };
    TransactionOrchestrator orchestrator(services, 1000);

    bool result = orchestrator.runTransaction();

    REQUIRE(result == false);
    // All services should receive an abort call in case of any failure.
    REQUIRE(service1.abort_calls == 1);
    REQUIRE(service2.abort_calls == 1);
}

// Test that the transaction aborts due to a service timeout.
TEST_CASE("Transaction aborts on service timeout") {
    MockService service1(MockService::SUCCESS);
    // Simulate a timeout: delay set longer than the orchestrator's timeout (500ms).
    MockService service2(MockService::TIMEOUT, 600);
    std::vector<ServiceInterface*> services = { &service1, &service2 };
    TransactionOrchestrator orchestrator(services, 500);

    bool result = orchestrator.runTransaction();

    REQUIRE(result == false);
    REQUIRE(service1.abort_calls == 1);
    REQUIRE(service2.abort_calls == 1);
}

// Test idempotency: multiple commit invocations should not lead to multiple commit actions.
TEST_CASE("Idempotency: Multiple commit calls do not affect state") {
    MockService service1(MockService::SUCCESS);
    MockService service2(MockService::SUCCESS);
    std::vector<ServiceInterface*> services = { &service1, &service2 };
    TransactionOrchestrator orchestrator(services, 1000);

    bool result = orchestrator.runTransaction();
    // Call finalizeTransaction() again to simulate re-sending commit messages (e.g., due to retries).
    orchestrator.finalizeTransaction();

    REQUIRE(result == true);
    // Even after re-calling finalizeTransaction(), commit should have been applied only once.
    REQUIRE(service1.commit_calls == 1);
    REQUIRE(service2.commit_calls == 1);
}

// Test that multiple transactions can be processed concurrently without interference.
TEST_CASE("Concurrent transactions handled correctly") {
    const int numTransactions = 10;
    std::vector<std::unique_ptr<MockService>> serviceMocks;
    std::vector<TransactionOrchestrator*> orchestrators;
    std::vector<ServiceInterface*> services;

    // Create a separate service for each transaction.
    for (int i = 0; i < numTransactions; ++i) {
        serviceMocks.push_back(std::make_unique<MockService>(MockService::SUCCESS));
    }
    for (int i = 0; i < numTransactions; ++i) {
        services.clear();
        services.push_back(serviceMocks[i].get());
        orchestrators.push_back(new TransactionOrchestrator(services, 1000));
    }

    std::vector<std::future<bool>> futures;
    for (auto* orch : orchestrators) {
        futures.push_back(std::async(std::launch::async, [orch]() {
            return orch->runTransaction();
        }));
    }

    int committed = 0;
    for (int i = 0; i < numTransactions; ++i) {
        bool res = futures[i].get();
        if (res) {
            committed++;
        }
    }
    // All transactions should commit successfully.
    REQUIRE(committed == numTransactions);
    for (int i = 0; i < numTransactions; ++i) {
        REQUIRE(serviceMocks[i]->commit_calls == 1);
    }

    for (auto* orch : orchestrators) {
        delete orch;
    }
}