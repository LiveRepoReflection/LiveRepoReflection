#include "dtm_banking.h"
#include "catch.hpp"

#include <vector>
#include <string>
#include <thread>
#include <future>

// Helper function to create an operation
dtm_banking::Operation create_operation(const std::string &server_id, const std::string &account_id,
                                          const std::string &operation, int amount) {
    dtm_banking::Operation op;
    op.server_id = server_id;
    op.account_id = account_id;
    op.operation = operation;
    op.amount = amount;
    return op;
}

TEST_CASE("Successful Transaction Commit", "[dtm_banking]") {
    // Prepare a valid transaction: withdrawing from one account and depositing to another.
    std::vector<dtm_banking::Operation> ops;
    ops.push_back(create_operation("server1", "accountA", "withdraw", 50));
    ops.push_back(create_operation("server2", "accountB", "deposit", 50));

    // Process the transaction
    std::string result = dtm_banking::processTransaction(ops);
    // Expect the transaction to commit
    REQUIRE(result == "committed");
}

TEST_CASE("Transaction Abort due to Insufficient Funds", "[dtm_banking]") {
    // Prepare a transaction where the withdraw amount is greater than the available funds.
    std::vector<dtm_banking::Operation> ops;
    ops.push_back(create_operation("server1", "accountA", "withdraw", 10000)); // excessive withdraw
    ops.push_back(create_operation("server2", "accountB", "deposit", 10000));

    // Process the transaction
    std::string result = dtm_banking::processTransaction(ops);
    // Expect the transaction to be aborted due to insufficient funds on server1
    REQUIRE(result == "aborted");
}

TEST_CASE("Transaction Error for Non-existent Account", "[dtm_banking]") {
    // Prepare a transaction with a non-existent account on one of the servers.
    std::vector<dtm_banking::Operation> ops;
    ops.push_back(create_operation("server1", "nonexistent", "withdraw", 50));
    ops.push_back(create_operation("server2", "accountB", "deposit", 50));

    // Process the transaction
    std::string result = dtm_banking::processTransaction(ops);
    // An invalid account should return an error response
    REQUIRE(result == "error");
}

TEST_CASE("Deadlock Prevention Under Concurrent Transactions", "[dtm_banking]") {
    // Prepare two concurrent transactions that access overlapping accounts.
    std::vector<dtm_banking::Operation> ops1;
    ops1.push_back(create_operation("server1", "accountA", "withdraw", 30));
    ops1.push_back(create_operation("server2", "accountB", "deposit", 30));
    
    std::vector<dtm_banking::Operation> ops2;
    ops2.push_back(create_operation("server2", "accountB", "withdraw", 20));
    ops2.push_back(create_operation("server1", "accountA", "deposit", 20));

    // Launch two concurrent transactions
    auto future1 = std::async(std::launch::async, [&ops1]() {
        return dtm_banking::processTransaction(ops1);
    });
    auto future2 = std::async(std::launch::async, [&ops2]() {
        return dtm_banking::processTransaction(ops2);
    });

    // Get results from both transactions
    std::string result1 = future1.get();
    std::string result2 = future2.get();

    // Both transactions should complete (either committed or aborted) and not deadlock.
    // We allow both "committed" and "aborted" as valid outcomes.
    bool valid1 = (result1 == "committed" || result1 == "aborted");
    bool valid2 = (result2 == "committed" || result2 == "aborted");

    REQUIRE(valid1);
    REQUIRE(valid2);
}

TEST_CASE("Crash Recovery Simulation", "[dtm_banking]") {
    // Simulate a transaction that is interrupted and then recovered.
    // The test assumes that the dtm_banking module provides a recovery mechanism
    // via a function recoverTransactions() that finalizes in-flight transactions.
    
    // Prepare a transaction which will simulate a crash in-between phases.
    std::vector<dtm_banking::Operation> ops;
    ops.push_back(create_operation("server1", "accountA", "withdraw", 40));
    ops.push_back(create_operation("server2", "accountB", "deposit", 40));

    // Start processing the transaction asynchronously.
    std::future<std::string> futureTxn = std::async(std::launch::async, [&ops]() {
        return dtm_banking::processTransaction(ops);
    });

    // Simulate a crash by invoking the recovery mechanism shortly after initiation.
    // We assume recoverTransactions() is a void function that when called,
    // processes any in-flight transactions after a crash.
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    dtm_banking::recoverTransactions();

    // Wait for the original transaction to finish.
    std::string result = futureTxn.get();

    // After recovery, the transaction should have been finalized.
    // Either a commit or an abort is acceptable, but it must not remain in an incomplete state.
    bool validOutcome = (result == "committed" || result == "aborted");
    REQUIRE(validOutcome);
}