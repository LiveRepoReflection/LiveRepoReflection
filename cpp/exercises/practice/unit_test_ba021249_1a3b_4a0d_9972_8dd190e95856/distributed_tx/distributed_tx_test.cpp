#include "distributed_tx.h"
#include <cassert>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include "catch.hpp"

TEST_CASE("Basic transaction commit", "[basic]") {
    std::stringstream output;
    TransactionManager txManager(2); // 2 shards

    txManager.processCommand("BEGIN 123");
    txManager.processCommand("UPDATE 123 0 initial data");
    txManager.processCommand("UPDATE 123 1 more data");
    txManager.processCommand("PREPARE 123");
    txManager.processCommand("COMMIT 123");
    
    output << txManager.processCommand("GET 0");
    output << std::endl;
    output << txManager.processCommand("GET 1");
    
    REQUIRE(output.str() == "initial data\nmore data");
}

TEST_CASE("Basic transaction rollback", "[basic]") {
    std::stringstream output;
    TransactionManager txManager(2); // 2 shards

    txManager.processCommand("BEGIN 123");
    txManager.processCommand("UPDATE 123 0 initial data");
    txManager.processCommand("UPDATE 123 1 more data");
    txManager.processCommand("ROLLBACK 123");
    
    output << txManager.processCommand("GET 0");
    output << std::endl;
    output << txManager.processCommand("GET 1");
    
    REQUIRE(output.str() == "NULL\nNULL");
}

TEST_CASE("Prepare then rollback", "[basic]") {
    std::stringstream output;
    TransactionManager txManager(2); // 2 shards

    txManager.processCommand("BEGIN 123");
    txManager.processCommand("UPDATE 123 0 initial data");
    txManager.processCommand("UPDATE 123 1 more data");
    txManager.processCommand("PREPARE 123");
    txManager.processCommand("ROLLBACK 123");
    
    output << txManager.processCommand("GET 0");
    output << std::endl;
    output << txManager.processCommand("GET 1");
    
    REQUIRE(output.str() == "NULL\nNULL");
}

TEST_CASE("Multiple transactions", "[multiple]") {
    std::stringstream output;
    TransactionManager txManager(3); // 3 shards

    // First transaction
    txManager.processCommand("BEGIN 123");
    txManager.processCommand("UPDATE 123 0 tx1 data");
    txManager.processCommand("UPDATE 123 1 more tx1 data");
    txManager.processCommand("PREPARE 123");
    txManager.processCommand("COMMIT 123");
    
    // Second transaction
    txManager.processCommand("BEGIN 456");
    txManager.processCommand("UPDATE 456 1 tx2 data");
    txManager.processCommand("UPDATE 456 2 more tx2 data");
    txManager.processCommand("PREPARE 456");
    txManager.processCommand("COMMIT 456");
    
    output << txManager.processCommand("GET 0");
    output << std::endl;
    output << txManager.processCommand("GET 1");
    output << std::endl;
    output << txManager.processCommand("GET 2");
    
    REQUIRE(output.str() == "tx1 data\ntx2 data\nmore tx2 data");
}

TEST_CASE("Transaction overwrites previous data", "[overwrite]") {
    std::stringstream output;
    TransactionManager txManager(2); // 2 shards

    // First transaction
    txManager.processCommand("BEGIN 123");
    txManager.processCommand("UPDATE 123 0 initial data");
    txManager.processCommand("PREPARE 123");
    txManager.processCommand("COMMIT 123");
    
    // Second transaction overwrites
    txManager.processCommand("BEGIN 456");
    txManager.processCommand("UPDATE 456 0 new data");
    txManager.processCommand("PREPARE 456");
    txManager.processCommand("COMMIT 456");
    
    output << txManager.processCommand("GET 0");
    
    REQUIRE(output.str() == "new data");
}

TEST_CASE("Example from problem statement", "[example]") {
    std::stringstream output;
    TransactionManager txManager(2); // 2 shards

    txManager.processCommand("BEGIN 123");
    txManager.processCommand("UPDATE 123 0 initial data");
    txManager.processCommand("UPDATE 123 1 more data");
    txManager.processCommand("PREPARE 123");
    txManager.processCommand("COMMIT 123");
    
    output << txManager.processCommand("GET 0");
    output << std::endl;
    output << txManager.processCommand("GET 1");
    output << std::endl;
    
    txManager.processCommand("BEGIN 456");
    txManager.processCommand("UPDATE 456 0 new data");
    txManager.processCommand("PREPARE 456");
    txManager.processCommand("ROLLBACK 456");
    
    output << txManager.processCommand("GET 0");
    output << std::endl;
    output << txManager.processCommand("GET 1");
    
    REQUIRE(output.str() == "initial data\nmore data\ninitial data\nmore data");
}

TEST_CASE("Complex sequence with multiple transactions", "[complex]") {
    std::stringstream output;
    TransactionManager txManager(3); // 3 shards

    // Transaction 1 - commits
    txManager.processCommand("BEGIN 100");
    txManager.processCommand("UPDATE 100 0 tx1 shard0");
    txManager.processCommand("UPDATE 100 1 tx1 shard1");
    txManager.processCommand("PREPARE 100");
    txManager.processCommand("COMMIT 100");
    
    // Transaction 2 - starts but will rollback later
    txManager.processCommand("BEGIN 200");
    txManager.processCommand("UPDATE 200 0 tx2 shard0");
    txManager.processCommand("UPDATE 200 2 tx2 shard2");
    
    // Transaction 3 - commits
    txManager.processCommand("BEGIN 300");
    txManager.processCommand("UPDATE 300 1 tx3 shard1");
    txManager.processCommand("UPDATE 300 2 tx3 shard2");
    txManager.processCommand("PREPARE 300");
    txManager.processCommand("COMMIT 300");
    
    // Now rollback transaction 2
    txManager.processCommand("ROLLBACK 200");
    
    // Check final state
    output << txManager.processCommand("GET 0");
    output << std::endl;
    output << txManager.processCommand("GET 1");
    output << std::endl;
    output << txManager.processCommand("GET 2");
    
    REQUIRE(output.str() == "tx1 shard0\ntx3 shard1\ntx3 shard2");
}

TEST_CASE("Boundary conditions", "[boundary]") {
    std::stringstream output;
    TransactionManager txManager(100); // Max number of shards
    
    // Transaction with max ID
    txManager.processCommand("BEGIN 100000");
    txManager.processCommand("UPDATE 100000 99 boundary test"); // Using highest shard ID
    txManager.processCommand("PREPARE 100000");
    txManager.processCommand("COMMIT 100000");
    
    output << txManager.processCommand("GET 99");
    
    REQUIRE(output.str() == "boundary test");
}

TEST_CASE("Updates with special characters", "[special_chars]") {
    std::stringstream output;
    TransactionManager txManager(1);
    
    txManager.processCommand("BEGIN 123");
    txManager.processCommand("UPDATE 123 0 Data with spaces and 123 numbers!");
    txManager.processCommand("PREPARE 123");
    txManager.processCommand("COMMIT 123");
    
    output << txManager.processCommand("GET 0");
    
    REQUIRE(output.str() == "Data with spaces and 123 numbers!");
}

TEST_CASE("Concurrent transactions on different shards", "[concurrent]") {
    std::stringstream output;
    TransactionManager txManager(3);
    
    // Start three transactions
    txManager.processCommand("BEGIN 100");
    txManager.processCommand("BEGIN 200");
    txManager.processCommand("BEGIN 300");
    
    // Each updates different shards
    txManager.processCommand("UPDATE 100 0 tx100 data");
    txManager.processCommand("UPDATE 200 1 tx200 data");
    txManager.processCommand("UPDATE 300 2 tx300 data");
    
    // Prepare and commit all
    txManager.processCommand("PREPARE 100");
    txManager.processCommand("PREPARE 200");
    txManager.processCommand("PREPARE 300");
    
    txManager.processCommand("COMMIT 100");
    txManager.processCommand("COMMIT 200");
    txManager.processCommand("COMMIT 300");
    
    output << txManager.processCommand("GET 0");
    output << std::endl;
    output << txManager.processCommand("GET 1");
    output << std::endl;
    output << txManager.processCommand("GET 2");
    
    REQUIRE(output.str() == "tx100 data\ntx200 data\ntx300 data");
}

TEST_CASE("Long data string", "[long_data]") {
    std::stringstream output;
    TransactionManager txManager(1);
    
    std::string longData(100, 'X'); // String of 100 'X' characters
    
    txManager.processCommand("BEGIN 123");
    txManager.processCommand("UPDATE 123 0 " + longData);
    txManager.processCommand("PREPARE 123");
    txManager.processCommand("COMMIT 123");
    
    output << txManager.processCommand("GET 0");
    
    REQUIRE(output.str() == longData);
}

TEST_CASE("Prepare without update", "[prepare_no_update]") {
    std::stringstream output;
    TransactionManager txManager(1);
    
    txManager.processCommand("BEGIN 123");
    txManager.processCommand("PREPARE 123");
    txManager.processCommand("COMMIT 123");
    
    output << txManager.processCommand("GET 0");
    
    REQUIRE(output.str() == "NULL");
}

TEST_CASE("Commit without prepare", "[commit_no_prepare]") {
    std::stringstream output;
    TransactionManager txManager(1);
    
    txManager.processCommand("BEGIN 123");
    txManager.processCommand("UPDATE 123 0 test data");
    // Intentionally skipping PREPARE
    txManager.processCommand("COMMIT 123");
    
    output << txManager.processCommand("GET 0");
    
    // Commit without prepare should not update the data
    REQUIRE(output.str() == "NULL");
}

TEST_CASE("Transaction impacts only affected shards", "[partial_update]") {
    std::stringstream output;
    TransactionManager txManager(3);
    
    txManager.processCommand("BEGIN 123");
    // Only update shard 0 and 2
    txManager.processCommand("UPDATE 123 0 shard0 data");
    txManager.processCommand("UPDATE 123 2 shard2 data");
    txManager.processCommand("PREPARE 123");
    txManager.processCommand("COMMIT 123");
    
    output << txManager.processCommand("GET 0");
    output << std::endl;
    output << txManager.processCommand("GET 1"); // Not updated
    output << std::endl;
    output << txManager.processCommand("GET 2");
    
    REQUIRE(output.str() == "shard0 data\nNULL\nshard2 data");
}