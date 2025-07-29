#include "tx_coordinator.h"
#include "catch.hpp"
#include <thread>
#include <future>
#include <vector>
#include <string>

using namespace tx_coordinator;

TEST_CASE("Successful Transaction", "[tx_coordinator]") {
    // Clear previous state for an isolated test run.
    clear_services();

    auto success_prepare = []() -> bool { return true; };
    auto success_commit = []() -> bool { return true; };
    auto success_rollback = []() -> bool { return true; };

    // Register two services that will participate successfully.
    bool reg1 = register_service("service1", success_prepare, success_commit, success_rollback);
    bool reg2 = register_service("service2", success_prepare, success_commit, success_rollback);
    REQUIRE(reg1 == true);
    REQUIRE(reg2 == true);

    std::vector<std::string> tx_services = { "service1", "service2" };
    bool result = execute_transaction(tx_services);
    REQUIRE(result == true);
}

TEST_CASE("Prepare Failure Transaction", "[tx_coordinator]") {
    clear_services();

    auto success_prepare = []() -> bool { return true; };
    auto fail_prepare = []() -> bool { return false; };
    auto success_commit = []() -> bool { return true; };
    auto success_rollback = []() -> bool { return true; };

    // Register two services; one will fail during the prepare phase.
    bool reg1 = register_service("service1", success_prepare, success_commit, success_rollback);
    bool reg2 = register_service("service2", fail_prepare, success_commit, success_rollback);
    REQUIRE(reg1 == true);
    REQUIRE(reg2 == true);

    std::vector<std::string> tx_services = { "service1", "service2" };
    bool result = execute_transaction(tx_services);
    REQUIRE(result == false);
}

TEST_CASE("Commit Failure Transaction", "[tx_coordinator]") {
    clear_services();

    auto success_prepare = []() -> bool { return true; };
    auto success_commit = []() -> bool { return true; };
    auto fail_commit = []() -> bool { return false; };
    auto success_rollback = []() -> bool { return true; };

    // Both services prepare successfully, but one fails during commit.
    bool reg1 = register_service("service1", success_prepare, success_commit, success_rollback);
    bool reg2 = register_service("service2", success_prepare, fail_commit, success_rollback);
    REQUIRE(reg1 == true);
    REQUIRE(reg2 == true);

    std::vector<std::string> tx_services = { "service1", "service2" };
    bool result = execute_transaction(tx_services);
    REQUIRE(result == false);
}

TEST_CASE("Concurrent Transactions", "[tx_coordinator]") {
    clear_services();

    auto success_prepare = []() -> bool { return true; };
    auto success_commit = []() -> bool { return true; };
    auto success_rollback = []() -> bool { return true; };

    // Register multiple services to be used in concurrent transactions.
    for (int i = 0; i < 10; i++) {
        bool reg = register_service("service" + std::to_string(i), success_prepare, success_commit, success_rollback);
        REQUIRE(reg == true);
    }

    auto transaction_task = [](const std::vector<std::string>& services) -> bool {
        return execute_transaction(services);
    };

    std::vector<std::future<bool>> futures;
    // Launch several transactions concurrently.
    for (int i = 0; i < 5; i++) {
        std::vector<std::string> tx_services;
        for (int j = 0; j < 5; j++) {
            tx_services.push_back("service" + std::to_string((i + j) % 10));
        }
        futures.push_back(std::async(std::launch::async, transaction_task, tx_services));
    }

    for (auto &f : futures) {
        bool result = f.get();
        REQUIRE(result == true);
    }
}

TEST_CASE("Dynamic Service Registration", "[tx_coordinator]") {
    clear_services();

    auto success_prepare = []() -> bool { return true; };
    auto success_commit = []() -> bool { return true; };
    auto success_rollback = []() -> bool { return true; };

    // Initially register a single service and execute a transaction.
    bool reg1 = register_service("service1", success_prepare, success_commit, success_rollback);
    REQUIRE(reg1 == true);
    std::vector<std::string> tx_services1 = { "service1" };
    bool result1 = execute_transaction(tx_services1);
    REQUIRE(result1 == true);

    // Dynamically register an additional service and execute a new transaction.
    bool reg2 = register_service("service2", success_prepare, success_commit, success_rollback);
    REQUIRE(reg2 == true);
    std::vector<std::string> tx_services2 = { "service1", "service2" };
    bool result2 = execute_transaction(tx_services2);
    REQUIRE(result2 == true);
}