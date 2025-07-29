#include "txn_manager.h"
#include "catch.hpp"
#include <string>
#include <vector>

TEST_CASE("Basic single node transaction") {
    TxnManager tm(1); // 1 node system
    
    REQUIRE(tm.begin(1) == true);
    REQUIRE(tm.write(1, 0, "x", 10) == true);
    REQUIRE(tm.read(1, 0, "x") == 10);
    REQUIRE(tm.commit(1) == true);
}

TEST_CASE("Transaction rollback") {
    TxnManager tm(1);
    
    REQUIRE(tm.begin(1) == true);
    REQUIRE(tm.write(1, 0, "x", 10) == true);
    REQUIRE(tm.rollback(1) == true);
    
    REQUIRE(tm.begin(2) == true);
    REQUIRE(tm.read(2, 0, "x") == -1); // Should return -1 for NULL
}

TEST_CASE("Multiple node transaction") {
    TxnManager tm(2);
    
    REQUIRE(tm.begin(1) == true);
    REQUIRE(tm.write(1, 0, "x", 10) == true);
    REQUIRE(tm.write(1, 1, "y", 20) == true);
    REQUIRE(tm.commit(1) == true);
    
    REQUIRE(tm.begin(2) == true);
    REQUIRE(tm.read(2, 0, "x") == 10);
    REQUIRE(tm.read(2, 1, "y") == 20);
}

TEST_CASE("Concurrent transactions") {
    TxnManager tm(2);
    
    REQUIRE(tm.begin(1) == true);
    REQUIRE(tm.begin(2) == true);
    
    REQUIRE(tm.write(1, 0, "x", 10) == true);
    REQUIRE(tm.write(2, 1, "y", 20) == true);
    
    REQUIRE(tm.commit(1) == true);
    REQUIRE(tm.commit(2) == true);
    
    REQUIRE(tm.begin(3) == true);
    REQUIRE(tm.read(3, 0, "x") == 10);
    REQUIRE(tm.read(3, 1, "y") == 20);
}

TEST_CASE("Transaction isolation") {
    TxnManager tm(1);
    
    REQUIRE(tm.begin(1) == true);
    REQUIRE(tm.write(1, 0, "x", 10) == true);
    
    REQUIRE(tm.begin(2) == true);
    REQUIRE(tm.read(2, 0, "x") == -1); // Should not see uncommitted changes
    
    REQUIRE(tm.commit(1) == true);
    REQUIRE(tm.read(2, 0, "x") == 10); // Now should see committed changes
}

TEST_CASE("Multiple key-value pairs per node") {
    TxnManager tm(1);
    
    REQUIRE(tm.begin(1) == true);
    REQUIRE(tm.write(1, 0, "x", 10) == true);
    REQUIRE(tm.write(1, 0, "y", 20) == true);
    REQUIRE(tm.write(1, 0, "z", 30) == true);
    REQUIRE(tm.commit(1) == true);
    
    REQUIRE(tm.begin(2) == true);
    REQUIRE(tm.read(2, 0, "x") == 10);
    REQUIRE(tm.read(2, 0, "y") == 20);
    REQUIRE(tm.read(2, 0, "z") == 30);
}

TEST_CASE("Value overwrite in same transaction") {
    TxnManager tm(1);
    
    REQUIRE(tm.begin(1) == true);
    REQUIRE(tm.write(1, 0, "x", 10) == true);
    REQUIRE(tm.write(1, 0, "x", 20) == true);
    REQUIRE(tm.read(1, 0, "x") == 20);
    REQUIRE(tm.commit(1) == true);
}

TEST_CASE("Large number of transactions") {
    TxnManager tm(5);
    
    for(int i = 1; i <= 1000; i++) {
        REQUIRE(tm.begin(i) == true);
        REQUIRE(tm.write(i, i % 5, "key", i) == true);
        REQUIRE(tm.commit(i) == true);
    }
    
    REQUIRE(tm.begin(1001) == true);
    for(int i = 0; i < 5; i++) {
        REQUIRE(tm.read(1001, i, "key") > 0);
    }
}

TEST_CASE("Invalid operations") {
    TxnManager tm(2);
    
    // Cannot operate on non-existent transaction
    REQUIRE(tm.write(1, 0, "x", 10) == false);
    REQUIRE(tm.read(1, 0, "x") == -1);
    REQUIRE(tm.commit(1) == false);
    
    // Cannot operate on invalid node
    REQUIRE(tm.begin(1) == true);
    REQUIRE(tm.write(1, 2, "x", 10) == false);
    REQUIRE(tm.read(1, 2, "x") == -1);
}

TEST_CASE("Transaction after rollback") {
    TxnManager tm(1);
    
    REQUIRE(tm.begin(1) == true);
    REQUIRE(tm.write(1, 0, "x", 10) == true);
    REQUIRE(tm.rollback(1) == true);
    
    REQUIRE(tm.begin(1) == true);  // Reusing same transaction ID
    REQUIRE(tm.write(1, 0, "x", 20) == true);
    REQUIRE(tm.commit(1) == true);
    
    REQUIRE(tm.begin(2) == true);
    REQUIRE(tm.read(2, 0, "x") == 20);
}