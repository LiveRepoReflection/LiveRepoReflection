#include "dist_tx_coord.h"
#include "catch.hpp"
#include <thread>
#include <vector>
#include <string>

using namespace dist_tx_coord;

TEST_CASE("commit_single_node_transaction") {
    TransactionCoordinator coordinator;
    Transaction tx;
    tx.id = "tx_commit_01";
    Operation op;
    op.node_id = "node1";
    op.op_type = Operation::WRITE;
    op.key = "key1";
    op.value = "value1";
    tx.operations.push_back(op);
    
    TxResult result = coordinator.processTransaction(tx);
    
    REQUIRE(result == TxResult::COMMIT);
}

TEST_CASE("commit_multiple_nodes_transaction") {
    TransactionCoordinator coordinator;
    Transaction tx;
    tx.id = "tx_commit_multi";
    
    Operation op1;
    op1.node_id = "node1";
    op1.op_type = Operation::WRITE;
    op1.key = "key1";
    op1.value = "value1";
    tx.operations.push_back(op1);
    
    Operation op2;
    op2.node_id = "node2";
    op2.op_type = Operation::READ;
    op2.key = "key2";
    op2.value = "";
    tx.operations.push_back(op2);
    
    Operation op3;
    op3.node_id = "node3";
    op3.op_type = Operation::WRITE;
    op3.key = "key3";
    op3.value = "value3";
    tx.operations.push_back(op3);
    
    TxResult result = coordinator.processTransaction(tx);
    
    REQUIRE(result == TxResult::COMMIT);
}

TEST_CASE("rollback_due_to_failure") {
    // In our simulation, if any operation targets a node with id "fail", the transaction should rollback.
    TransactionCoordinator coordinator;
    Transaction tx;
    tx.id = "tx_fail_01";
    
    Operation op1;
    op1.node_id = "node1";
    op1.op_type = Operation::WRITE;
    op1.key = "key1";
    op1.value = "value1";
    tx.operations.push_back(op1);
    
    Operation op_fail;
    op_fail.node_id = "fail";
    op_fail.op_type = Operation::WRITE;
    op_fail.key = "key_fail";
    op_fail.value = "valueX";
    tx.operations.push_back(op_fail);
    
    TxResult result = coordinator.processTransaction(tx);
    
    REQUIRE(result == TxResult::ROLLBACK);
}

TEST_CASE("transaction_timeout") {
    // In our simulation, if a transaction has id "tx_timeout" it should simulate a timeout.
    TransactionCoordinator coordinator;
    Transaction tx;
    tx.id = "tx_timeout";
    
    Operation op;
    op.node_id = "slow";
    op.op_type = Operation::READ;
    op.key = "key_slow";
    op.value = "";
    tx.operations.push_back(op);
    
    TxResult result = coordinator.processTransaction(tx);
    
    REQUIRE(result == TxResult::TIMEOUT);
}

TEST_CASE("concurrent_transactions") {
    TransactionCoordinator coordinator;
    const int numTransactions = 10;
    std::vector<std::thread> threads;
    std::vector<TxResult> results(numTransactions);
    std::vector<std::string> tx_ids = {
        "tx_c1", "tx_c2", "tx_c3", "tx_c4", "tx_c5",
        "tx_c6", "tx_c7", "tx_c8", "tx_c9", "tx_c10"
    };
    
    for (int i = 0; i < numTransactions; i++) {
        threads.push_back(std::thread([&, i]() {
            Transaction tx;
            tx.id = tx_ids[i];
            
            Operation op;
            op.node_id = "node1";
            op.op_type = Operation::WRITE;
            op.key = "key" + std::to_string(i);
            op.value = "value" + std::to_string(i);
            tx.operations.push_back(op);
            
            // For even-indexed transactions, add an extra operation.
            if (i % 2 == 0) {
                Operation op2;
                op2.node_id = "node2";
                op2.op_type = Operation::READ;
                op2.key = "key" + std::to_string(i + 10);
                op2.value = "";
                tx.operations.push_back(op2);
            }
            
            results[i] = coordinator.processTransaction(tx);
        }));
    }
    
    for (auto &t : threads) {
        t.join();
    }
    
    for (const auto &result : results) {
        REQUIRE(result == TxResult::COMMIT);
    }
}