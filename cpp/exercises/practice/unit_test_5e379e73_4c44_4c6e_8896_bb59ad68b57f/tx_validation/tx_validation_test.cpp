#include "tx_validation.h"
#include <string>
#include <vector>
#include <sstream>
#include "catch.hpp"

using namespace std;

TEST_CASE("Valid simple transaction") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "VOTE_COMMIT 1 SERVICE_1",
        "COMMIT 1",
        "COMPLETE 1 SERVICE_1"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == true);
}

TEST_CASE("Valid multi-service transaction with commit") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "PREPARE 1 SERVICE_2",
        "VOTE_COMMIT 1 SERVICE_1",
        "VOTE_COMMIT 1 SERVICE_2",
        "COMMIT 1",
        "COMPLETE 1 SERVICE_1",
        "COMPLETE 1 SERVICE_2"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == true);
}

TEST_CASE("Valid multi-service transaction with abort") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "PREPARE 1 SERVICE_2",
        "VOTE_COMMIT 1 SERVICE_1",
        "VOTE_ABORT 1 SERVICE_2",
        "ABORT 1",
        "COMPLETE 1 SERVICE_1",
        "COMPLETE 1 SERVICE_2"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == true);
}

TEST_CASE("Valid multiple transactions") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "PREPARE 1 SERVICE_2",
        "VOTE_COMMIT 1 SERVICE_1",
        "VOTE_COMMIT 1 SERVICE_2",
        "COMMIT 1",
        "COMPLETE 1 SERVICE_1",
        "COMPLETE 1 SERVICE_2",
        "PREPARE 2 SERVICE_1",
        "VOTE_ABORT 2 SERVICE_1",
        "ABORT 2",
        "COMPLETE 2 SERVICE_1",
        "PREPARE 3 SERVICE_1",
        "PREPARE 3 SERVICE_2",
        "VOTE_COMMIT 3 SERVICE_1",
        "VOTE_ABORT 3 SERVICE_2",
        "ABORT 3",
        "COMPLETE 3 SERVICE_1",
        "COMPLETE 3 SERVICE_2"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == true);
}

TEST_CASE("Invalid: Vote before prepare") {
    vector<string> logs = {
        "VOTE_COMMIT 1 SERVICE_1",
        "PREPARE 1 SERVICE_1",
        "COMMIT 1",
        "COMPLETE 1 SERVICE_1"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == false);
}

TEST_CASE("Invalid: Multiple votes for same transaction from same service") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "VOTE_COMMIT 1 SERVICE_1",
        "VOTE_ABORT 1 SERVICE_1",
        "ABORT 1",
        "COMPLETE 1 SERVICE_1"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == false);
}

TEST_CASE("Invalid: Commit before all votes are in") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "PREPARE 1 SERVICE_2",
        "VOTE_COMMIT 1 SERVICE_1",
        "COMMIT 1",
        "VOTE_COMMIT 1 SERVICE_2",
        "COMPLETE 1 SERVICE_1",
        "COMPLETE 1 SERVICE_2"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == false);
}

TEST_CASE("Invalid: Commit when abort vote exists") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "PREPARE 1 SERVICE_2",
        "VOTE_COMMIT 1 SERVICE_1",
        "VOTE_ABORT 1 SERVICE_2",
        "COMMIT 1",
        "COMPLETE 1 SERVICE_1",
        "COMPLETE 1 SERVICE_2"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == false);
}

TEST_CASE("Invalid: Complete before commit/abort") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "VOTE_COMMIT 1 SERVICE_1",
        "COMPLETE 1 SERVICE_1",
        "COMMIT 1"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == false);
}

TEST_CASE("Invalid: Multiple complete for same transaction from same service") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "VOTE_COMMIT 1 SERVICE_1",
        "COMMIT 1",
        "COMPLETE 1 SERVICE_1",
        "COMPLETE 1 SERVICE_1"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == false);
}

TEST_CASE("Invalid: Abort without any abort vote") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "PREPARE 1 SERVICE_2",
        "VOTE_COMMIT 1 SERVICE_1",
        "VOTE_COMMIT 1 SERVICE_2",
        "ABORT 1",
        "COMPLETE 1 SERVICE_1",
        "COMPLETE 1 SERVICE_2"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == false);
}

TEST_CASE("Stress test with large input") {
    vector<string> logs;
    
    // Generate a large number of valid transactions
    for (int i = 1; i <= 1000; i++) {
        logs.push_back("PREPARE " + to_string(i) + " SERVICE_1");
        logs.push_back("PREPARE " + to_string(i) + " SERVICE_2");
        logs.push_back("VOTE_COMMIT " + to_string(i) + " SERVICE_1");
        logs.push_back("VOTE_COMMIT " + to_string(i) + " SERVICE_2");
        logs.push_back("COMMIT " + to_string(i));
        logs.push_back("COMPLETE " + to_string(i) + " SERVICE_1");
        logs.push_back("COMPLETE " + to_string(i) + " SERVICE_2");
    }
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == true);
}

TEST_CASE("Empty logs") {
    vector<string> logs;
    bool result = tx_validation::validate_transactions(logs);
    REQUIRE(result == true);
}

TEST_CASE("Interleaved transactions") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "PREPARE 2 SERVICE_2",
        "VOTE_COMMIT 1 SERVICE_1",
        "VOTE_COMMIT 2 SERVICE_2",
        "COMMIT 1",
        "COMMIT 2",
        "COMPLETE 1 SERVICE_1",
        "COMPLETE 2 SERVICE_2"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == true);
}

TEST_CASE("Complex interleaved transactions") {
    vector<string> logs = {
        "PREPARE 1 SERVICE_1",
        "PREPARE 1 SERVICE_2",
        "PREPARE 2 SERVICE_1",
        "VOTE_COMMIT 1 SERVICE_1",
        "PREPARE 2 SERVICE_3",
        "VOTE_COMMIT 2 SERVICE_1",
        "VOTE_ABORT 1 SERVICE_2",
        "VOTE_COMMIT 2 SERVICE_3",
        "ABORT 1",
        "COMMIT 2", 
        "COMPLETE 1 SERVICE_1",
        "COMPLETE 2 SERVICE_1",
        "COMPLETE 1 SERVICE_2",
        "COMPLETE 2 SERVICE_3"
    };
    
    bool result = tx_validation::validate_transactions(logs);
    
    REQUIRE(result == true);
}

TEST_CASE("From string stream") {
    string input = "PREPARE 1 SERVICE_1\n"
                  "PREPARE 1 SERVICE_2\n"
                  "VOTE_COMMIT 1 SERVICE_1\n"
                  "VOTE_COMMIT 1 SERVICE_2\n"
                  "COMMIT 1\n"
                  "COMPLETE 1 SERVICE_1\n"
                  "COMPLETE 1 SERVICE_2";
                  
    istringstream iss(input);
    bool result = tx_validation::validate_transactions(iss);
    
    REQUIRE(result == true);
}