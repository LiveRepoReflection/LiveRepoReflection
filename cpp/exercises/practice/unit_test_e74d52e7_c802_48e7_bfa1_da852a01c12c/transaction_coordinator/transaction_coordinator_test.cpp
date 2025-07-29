#include "transaction_coordinator.h"
#include <sstream>
#include <fstream>
#include <thread>
#include <iterator>
#include <string>
#include "catch.hpp"

using std::string;
using std::istringstream;
using std::ostringstream;
using std::ifstream;
using std::istreambuf_iterator;
using std::thread;

TEST_CASE("Single Transaction Commit", "[transaction_coordinator]") {
    // Transaction with id 123 on nodes 1, 2, 3; simulate ideal conditions so transaction commits.
    string input = "3 100\n123 1 2 3\nEND\n";
    istringstream iss(input);
    ostringstream oss;
    transaction_coordinator::process_transactions(iss, oss);
    string output = oss.str();
    // Expected output must include a commit decision for transaction 123.
    REQUIRE(output.find("Transaction 123: COMMIT") != string::npos);
}

TEST_CASE("Single Transaction Abort", "[transaction_coordinator]") {
    // Transaction 456 simulates a timeout condition by using a very low timeout value,
    // which causes at least one node to be treated as unresponsive.
    string input = "3 10\n456 1 2\nEND\n";
    istringstream iss(input);
    ostringstream oss;
    transaction_coordinator::process_transactions(iss, oss);
    string output = oss.str();
    // Expected output must include an abort decision for transaction 456.
    REQUIRE(output.find("Transaction 456: ABORT") != string::npos);
}

TEST_CASE("Multiple Transactions", "[transaction_coordinator]") {
    // Multiple transactions in one input stream.
    // For testing purposes, we assume that the implementation deterministically decides
    // that transactions with odd id numbers commit, while even id numbers abort.
    string input = "4 100\n789 1 2 3 4\n101 2 3\n112 1 4\nEND\n";
    istringstream iss(input);
    ostringstream oss;
    transaction_coordinator::process_transactions(iss, oss);
    string output = oss.str();
    // Check for expected outcomes of each transaction.
    REQUIRE(output.find("Transaction 789: COMMIT") != string::npos);
    REQUIRE(output.find("Transaction 101: COMMIT") != string::npos);
    REQUIRE(output.find("Transaction 112: ABORT") != string::npos);
}

TEST_CASE("Concurrent Transactions", "[transaction_coordinator]") {
    // Simulate two transactions executing concurrently.
    string input1 = "3 100\n201 1 2 3\nEND\n";
    string input2 = "3 100\n202 1 2\nEND\n";
    istringstream iss1(input1);
    istringstream iss2(input2);
    ostringstream oss1;
    ostringstream oss2;

    thread t1([&iss1, &oss1]() {
        transaction_coordinator::process_transactions(iss1, oss1);
    });
    thread t2([&iss2, &oss2]() {
        transaction_coordinator::process_transactions(iss2, oss2);
    });
    t1.join();
    t2.join();

    string output1 = oss1.str();
    string output2 = oss2.str();
    // For testing, assume transaction 201 (odd) commits and 202 (even) aborts.
    REQUIRE(output1.find("Transaction 201: COMMIT") != string::npos);
    REQUIRE(output2.find("Transaction 202: ABORT") != string::npos);
}

TEST_CASE("Node Logging", "[transaction_coordinator]") {
    // After processing a transaction, each participating node should log the prepare
    // and commit/abort messages to its respective log file.
    string input = "2 100\n301 1 2\nEND\n";
    istringstream iss(input);
    ostringstream oss;
    transaction_coordinator::process_transactions(iss, oss);

    ifstream log1("node_1.log");
    ifstream log2("node_2.log");
    REQUIRE(log1.good());
    REQUIRE(log2.good());

    string content1((istreambuf_iterator<char>(log1)), istreambuf_iterator<char>());
    string content2((istreambuf_iterator<char>(log2)), istreambuf_iterator<char>());

    // Verify that both logs contain a "prepare" message and a decision ("commit" or "abort")
    bool foundPrepare1 = (content1.find("prepare") != string::npos);
    bool foundDecision1 = (content1.find("commit") != string::npos) || (content1.find("abort") != string::npos);
    bool foundPrepare2 = (content2.find("prepare") != string::npos);
    bool foundDecision2 = (content2.find("commit") != string::npos) || (content2.find("abort") != string::npos);

    REQUIRE(foundPrepare1);
    REQUIRE(foundDecision1);
    REQUIRE(foundPrepare2);
    REQUIRE(foundDecision2);
}