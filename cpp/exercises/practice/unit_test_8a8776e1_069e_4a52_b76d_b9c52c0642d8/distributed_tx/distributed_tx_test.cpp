#include "distributed_tx.h"
#include "catch.hpp"
#include <vector>
#include <string>
#include <future>
#include <thread>

using namespace std;

TEST_CASE("All services prepare and commit successfully", "[distributed_tx]") {
    // Simulate a scenario where every microservice successfully prepares and commits.
    vector<string> services = { "service_success_A", "service_success_B", "service_success_C" };
    string user_action = "update_profile";
    bool result = distributed_tx::process_transaction(services, user_action);
    REQUIRE(result == true);
}

TEST_CASE("Service fails during prepare phase triggering rollback", "[distributed_tx]") {
    // Simulate a scenario where one of the microservices fails in its prepare phase.
    vector<string> services = { "service_success", "service_fail_prepare", "service_success" };
    string user_action = "modify_inventory";
    bool result = distributed_tx::process_transaction(services, user_action);
    REQUIRE(result == false);
}

TEST_CASE("Service fails during commit and recovers with retries", "[distributed_tx]") {
    // Simulate a scenario where one microservice experiences a transient failure on commit,
    // then recovers via the coordinator's retry mechanism.
    vector<string> services = { "service_success", "service_retry_commit", "service_success" };
    string user_action = "log_activity";
    bool result = distributed_tx::process_transaction(services, user_action);
    REQUIRE(result == true);
}

TEST_CASE("Concurrent transactions", "[distributed_tx]") {
    // Launch multiple transactions concurrently, alternating between successful and failing prepare phases.
    auto transaction_task = [](const vector<string>& svc, const string& act) {
        return distributed_tx::process_transaction(svc, act);
    };

    vector<future<bool>> futures;
    // Create 10 concurrent transactions.
    for (int i = 0; i < 10; i++) {
        vector<string> services;
        if (i % 2 == 0) {
            services = { "service_success", "service_success", "service_success" };
        } else {
            services = { "service_success", "service_fail_prepare", "service_success" };
        }
        string action = "action_" + to_string(i);
        futures.push_back(async(launch::async, transaction_task, services, action));
    }
    
    int success_count = 0;
    for (auto& fut : futures) {
        if (fut.get()) {
            success_count++;
        }
    }
    // Expect 5 transactions to succeed (even indices) and 5 to fail.
    REQUIRE(success_count == 5);
}

TEST_CASE("Recovery of in-doubt transactions", "[distributed_tx]") {
    // Simulate recovery of transactions that were left in an in-doubt state.
    // The recover_transactions function is expected to return the number of recovered transactions.
    int recovered = distributed_tx::recover_transactions();
    // For the purpose of this test, the returned count should be non-negative.
    REQUIRE(recovered >= 0);
}