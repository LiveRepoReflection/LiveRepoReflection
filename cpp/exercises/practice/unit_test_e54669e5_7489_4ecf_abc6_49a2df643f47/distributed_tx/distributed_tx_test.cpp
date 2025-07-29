#include "distributed_tx.h"
#include "catch.hpp"
#include <thread>
#include <future>
#include <vector>
#include <string>

// The following Transaction structure and TransactionManager are assumed to be defined in distributed_tx.h.
// For testing purposes, a Transaction contains the following attributes:
//   - int txid: Unique transaction identifier.
//   - std::vector<std::string> services: Identifiers for the participating service endpoints.
//   - std::string account_from: The source account ID.
//   - std::string account_to: The destination account ID.
//   - double amount: The transfer amount.
//   - int timeout_ms: The timeout in milliseconds for the transaction phases.

// It is assumed that TransactionManager has a method:
//   bool executeTransaction(const Transaction &tx);
// which returns true if the transaction is successfully committed, and false otherwise.

// Test Case 1: Successful Transaction Commit
TEST_CASE("Successful Transaction Commit", "[transaction]") {
    std::vector<std::string> services = {"account_service_A_success", "account_service_B_success"};
    Transaction tx;
    tx.txid = 1;
    tx.services = services;
    tx.account_from = "AccountA";
    tx.account_to = "AccountB";
    tx.amount = 100.0;
    tx.timeout_ms = 1000;

    TransactionManager tm;
    bool result = tm.executeTransaction(tx);
    REQUIRE(result == true);
}

// Test Case 2: Transaction Abort when one service fails in Prepare phase
TEST_CASE("Transaction Abort on Service Failure", "[transaction]") {
    std::vector<std::string> services = {"account_service_A_success", "account_service_B_fail"};
    Transaction tx;
    tx.txid = 2;
    tx.services = services;
    tx.account_from = "AccountA";
    tx.account_to = "AccountB";
    tx.amount = 150.0;
    tx.timeout_ms = 1000;

    TransactionManager tm;
    bool result = tm.executeTransaction(tx);
    REQUIRE(result == false);
}

// Test Case 3: Transaction Abort on Timeout
TEST_CASE("Transaction Abort on Timeout", "[transaction]") {
    std::vector<std::string> services = {"account_service_A_success", "account_service_B_timeout"};
    Transaction tx;
    tx.txid = 3;
    tx.services = services;
    tx.account_from = "AccountA";
    tx.account_to = "AccountB";
    tx.amount = 75.0;
    tx.timeout_ms = 500; // shorter timeout to trigger the timeout behavior

    TransactionManager tm;
    bool result = tm.executeTransaction(tx);
    REQUIRE(result == false);
}

// Test Case 4: Idempotent Transaction Commit - Commit requests repeated should not affect outcome
TEST_CASE("Idempotent Transaction Commit", "[transaction]") {
    std::vector<std::string> services = {"account_service_A_success", "account_service_B_success"};
    Transaction tx;
    tx.txid = 4;
    tx.services = services;
    tx.account_from = "AccountA";
    tx.account_to = "AccountB";
    tx.amount = 200.0;
    tx.timeout_ms = 1000;

    TransactionManager tm;
    // Execute the transaction twice using the same TXID
    bool firstResult = tm.executeTransaction(tx);
    bool secondResult = tm.executeTransaction(tx);
    REQUIRE(firstResult == true);
    REQUIRE(secondResult == true);
}

// Test Case 5: Concurrent Transactions - Ensure thread-safety and correct handling of multiple transactions
TEST_CASE("Concurrent Transactions", "[concurrency]") {
    TransactionManager tm;
    const int numTransactions = 10;
    std::vector<std::future<bool>> futures;

    for (int i = 0; i < numTransactions; i++) {
        futures.push_back(std::async(std::launch::async, [i, &tm]() -> bool {
            Transaction tx;
            tx.txid = 100 + i;
            // Alternate between a transaction expected to commit and one expected to abort
            if (i % 2 == 0) {
                tx.services = {"account_service_A_success", "account_service_B_success"};
            } else {
                tx.services = {"account_service_A_success", "account_service_B_fail"};
            }
            tx.account_from = "Account_" + std::to_string(i);
            tx.account_to = "Account_" + std::to_string(i + 1);
            tx.amount = 50.0 + i;
            tx.timeout_ms = 1000;
            return tm.executeTransaction(tx);
        }));
    }

    int successCount = 0;
    for (auto &fut : futures) {
        if (fut.get()) {
            successCount++;
        }
    }
    // Since even-indexed transactions should succeed, we expect half of the transactions to commit.
    REQUIRE(successCount == numTransactions / 2);
}