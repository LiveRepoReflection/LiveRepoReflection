#include "distributed_tx.h"
#include <chrono>
#include <future>
#include <thread>
#include <vector>
#include "catch.hpp"

using namespace distributed_tx;

TEST_CASE("Single transaction commit", "[transaction]") {
    Transaction txn;
    txn.transaction_id = 1;
    txn.user_id = 101;
    txn.item_id = 5001;
    txn.quantity = 2;
    txn.price = 100;
    txn.payment_details = "VALID";
    txn.simulate_failure = false;       // Do not simulate failure
    txn.simulate_timeout = false;       // No timeout simulation
    txn.simulate_partial_failure = false; // No partial failure

    bool result = process_transaction(txn);
    // Expected to commit successfully.
    REQUIRE(result == true);
}

TEST_CASE("Single transaction rollback due to failure", "[transaction]") {
    Transaction txn;
    txn.transaction_id = 2;
    txn.user_id = 102;
    txn.item_id = 5002;
    txn.quantity = 1;
    txn.price = 150;
    txn.payment_details = "VALID";
    txn.simulate_failure = true;        // Force a failure in one of the services
    txn.simulate_timeout = false;
    txn.simulate_partial_failure = false;

    bool result = process_transaction(txn);
    // Expected to rollback due to simulated failure.
    REQUIRE(result == false);
}

TEST_CASE("Concurrent transactions", "[transaction][concurrency]") {
    const int num_transactions = 10;
    std::vector<std::future<bool>> futures;
    std::vector<Transaction> transactions(num_transactions);

    for (int i = 0; i < num_transactions; ++i) {
        transactions[i].transaction_id = 1000 + i;
        transactions[i].user_id = 200 + i;
        transactions[i].item_id = 6000 + i;
        transactions[i].quantity = (i % 3) + 1;
        transactions[i].price = 50 * ((i % 5) + 1);
        transactions[i].payment_details = "VALID";
        // Simulate failure for even-indexed transactions.
        transactions[i].simulate_failure = (i % 2 == 0);
        transactions[i].simulate_timeout = false;
        transactions[i].simulate_partial_failure = false;
    }

    for (int i = 0; i < num_transactions; ++i) {
        futures.push_back(std::async(std::launch::async, [&, i]() {
            return process_transaction(transactions[i]);
        }));
    }

    int commit_count = 0;
    int rollback_count = 0;
    for (auto& fut : futures) {
        bool res = fut.get();
        if (res)
            commit_count++;
        else
            rollback_count++;
    }
    // Check that the total processed transactions equals the number submitted.
    REQUIRE((commit_count + rollback_count) == num_transactions);
}

TEST_CASE("Timeout handling", "[transaction][timeout]") {
    Transaction txn;
    txn.transaction_id = 3;
    txn.user_id = 103;
    txn.item_id = 5003;
    txn.quantity = 3;
    txn.price = 200;
    txn.payment_details = "VALID";
    txn.simulate_failure = false;
    txn.simulate_timeout = true;        // Force a timeout scenario in one service call.
    txn.simulate_partial_failure = false;

    bool result = process_transaction(txn);
    // Expected to rollback due to timeout.
    REQUIRE(result == false);
}

TEST_CASE("Recovery from simulated service failure", "[transaction][recovery]") {
    Transaction txn;
    txn.transaction_id = 4;
    txn.user_id = 104;
    txn.item_id = 5004;
    txn.quantity = 1;
    txn.price = 300;
    txn.payment_details = "VALID";
    txn.simulate_failure = false;
    txn.simulate_timeout = false;
    txn.simulate_partial_failure = true; // Simulate a service crash during commit.

    bool result = process_transaction(txn);
    // Expected to rollback after recovery procedure due to partial failure.
    REQUIRE(result == false);
}