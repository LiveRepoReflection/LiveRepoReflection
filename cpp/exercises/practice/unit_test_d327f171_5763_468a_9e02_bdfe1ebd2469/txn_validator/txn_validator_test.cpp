#include "txn_validator.h"
#include "catch.hpp"

TEST_CASE("Basic successful transaction") {
    std::string log = 
        "Tx1,ServiceA,PREPARE,1000\n"
        "Tx1,ServiceB,PREPARE,1001\n"
        "Tx1,Coordinator,COORDINATOR_COMMIT,1002\n"
        "Tx1,ServiceA,COMMIT,1003\n"
        "Tx1,ServiceB,COMMIT,1004\n";

    std::string expected = "Tx1,COMMITTED\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Basic aborted transaction") {
    std::string log = 
        "Tx1,ServiceA,PREPARE,1000\n"
        "Tx1,ServiceB,ABORT,1001\n"
        "Tx1,Coordinator,COORDINATOR_ABORT,1002\n";

    std::string expected = "Tx1,ABORTED\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Inconsistent transaction - commit without prepare") {
    std::string log = 
        "Tx1,ServiceA,COMMIT,1000\n"
        "Tx1,Coordinator,COORDINATOR_COMMIT,1001\n";

    std::string expected = "Tx1,INCONSISTENT\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Multiple transactions") {
    std::string log = 
        "Tx2,ServiceA,PREPARE,1000\n"
        "Tx1,ServiceA,PREPARE,1001\n"
        "Tx1,ServiceB,PREPARE,1002\n"
        "Tx1,Coordinator,COORDINATOR_COMMIT,1003\n"
        "Tx1,ServiceA,COMMIT,1004\n"
        "Tx1,ServiceB,COMMIT,1005\n"
        "Tx2,ServiceB,ABORT,1006\n"
        "Tx2,Coordinator,COORDINATOR_ABORT,1007\n";

    std::string expected = "Tx1,COMMITTED\nTx2,ABORTED\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Duplicate events") {
    std::string log = 
        "Tx1,ServiceA,PREPARE,1000\n"
        "Tx1,ServiceA,PREPARE,1000\n"
        "Tx1,ServiceB,PREPARE,1001\n"
        "Tx1,Coordinator,COORDINATOR_COMMIT,1002\n"
        "Tx1,ServiceA,COMMIT,1003\n"
        "Tx1,ServiceB,COMMIT,1004\n"
        "Tx1,ServiceB,COMMIT,1004\n";

    std::string expected = "Tx1,COMMITTED\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Inconsistent - conflicting coordinator decisions") {
    std::string log = 
        "Tx1,ServiceA,PREPARE,1000\n"
        "Tx1,Coordinator,COORDINATOR_COMMIT,1001\n"
        "Tx1,Coordinator,COORDINATOR_ABORT,1002\n";

    std::string expected = "Tx1,INCONSISTENT\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Inconsistent - commit after abort") {
    std::string log = 
        "Tx1,ServiceA,PREPARE,1000\n"
        "Tx1,ServiceA,ABORT,1001\n"
        "Tx1,ServiceA,COMMIT,1002\n";

    std::string expected = "Tx1,INCONSISTENT\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Empty log") {
    std::string log = "";
    std::string expected = "";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Large number of services") {
    std::string log;
    for(int i = 0; i < 100; i++) {
        log += "Tx1,Service" + std::to_string(i) + ",PREPARE,1000\n";
    }
    log += "Tx1,Coordinator,COORDINATOR_COMMIT,1001\n";
    for(int i = 0; i < 100; i++) {
        log += "Tx1,Service" + std::to_string(i) + ",COMMIT,1002\n";
    }

    std::string expected = "Tx1,COMMITTED\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Out of order events") {
    std::string log = 
        "Tx1,ServiceB,COMMIT,1004\n"
        "Tx1,ServiceA,COMMIT,1003\n"
        "Tx1,Coordinator,COORDINATOR_COMMIT,1002\n"
        "Tx1,ServiceB,PREPARE,1001\n"
        "Tx1,ServiceA,PREPARE,1000\n";

    std::string expected = "Tx1,COMMITTED\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Missing coordinator decision") {
    std::string log = 
        "Tx1,ServiceA,PREPARE,1000\n"
        "Tx1,ServiceB,PREPARE,1001\n"
        "Tx1,ServiceA,COMMIT,1003\n"
        "Tx1,ServiceB,COMMIT,1004\n";

    std::string expected = "Tx1,INCONSISTENT\n";
    REQUIRE(validate_transactions(log) == expected);
}

TEST_CASE("Partial commits") {
    std::string log = 
        "Tx1,ServiceA,PREPARE,1000\n"
        "Tx1,ServiceB,PREPARE,1001\n"
        "Tx1,Coordinator,COORDINATOR_COMMIT,1002\n"
        "Tx1,ServiceA,COMMIT,1003\n";

    std::string expected = "Tx1,INCONSISTENT\n";
    REQUIRE(validate_transactions(log) == expected);
}