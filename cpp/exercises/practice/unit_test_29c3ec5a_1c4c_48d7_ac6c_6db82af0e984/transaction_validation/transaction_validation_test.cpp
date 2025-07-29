#include "transaction_validation.h"
#include "catch.hpp"
#include <vector>
#include <string>

using namespace std;
using namespace transaction_validation;

// Helper function to build shard logs from initializer list of initializer lists.
vector<vector<string>> build_shard_logs(const vector<vector<string>>& logs) {
    return logs;
}

// Helper function to build global transactions from initializer list of initializer lists.
vector<vector<string>> build_global_transactions(const vector<vector<string>>& trans) {
    return trans;
}

TEST_CASE("Valid scenario with multiple shards and transactions", "[transaction_validation]") {
    int num_shards = 3;
    vector<vector<string>> shard_logs = {
        {"T1", "T3", "T5"},
        {"T2", "T4"},
        {"T6", "T8"}
    };
    vector<vector<string>> global_transactions = {
        {"0:T1", "1:T2"},
        {"0:T3", "1:T4", "2:T6"},
        {"0:T5", "2:T8"}
    };
    // Expected valid scenario.
    REQUIRE(validate_transactions(num_shards, shard_logs, global_transactions) == true);
}

TEST_CASE("Atomicity failure: missing transaction in one shard log", "[transaction_validation]") {
    int num_shards = 3;
    // Shard 2 is missing "T8"
    vector<vector<string>> shard_logs = {
        {"T1", "T3", "T5"},
        {"T2", "T4"},
        {"T6"}  
    };
    vector<vector<string>> global_transactions = {
        {"0:T1", "1:T2"},
        {"0:T3", "1:T4", "2:T6"},
        {"0:T5", "2:T8"}   // "T8" is missing in shard log 2.
    };
    REQUIRE(validate_transactions(num_shards, shard_logs, global_transactions) == false);
}

TEST_CASE("Ordering consistency failure: transactions out of order in a shard", "[transaction_validation]") {
    int num_shards = 3;
    // Shard 0 order is not consistent with global transaction initiation order.
    vector<vector<string>> shard_logs = {
        {"T3", "T1", "T5"},
        {"T2", "T4"},
        {"T6", "T8"}
    };
    vector<vector<string>> global_transactions = {
        {"0:T1", "1:T2"},
        {"0:T3", "1:T4", "2:T6"},
        {"0:T5", "2:T8"}
    };
    REQUIRE(validate_transactions(num_shards, shard_logs, global_transactions) == false);
}

TEST_CASE("Ordering consistency failure across shards", "[transaction_validation]") {
    int num_shards = 2;
    // For shard 1, the transaction order is reversed compared to global transaction order.
    vector<vector<string>> shard_logs = {
        {"T1", "T3"},
        {"T4", "T2"}
    };
    vector<vector<string>> global_transactions = {
        {"0:T1", "1:T2"},
        {"0:T3", "1:T4"}
    };
    REQUIRE(validate_transactions(num_shards, shard_logs, global_transactions) == false);
}

TEST_CASE("Single shard global transaction valid", "[transaction_validation]") {
    int num_shards = 2;
    // Only shard 0 is used in the transaction.
    vector<vector<string>> shard_logs = {
        {"A", "B"},
        {"C"}
    };
    vector<vector<string>> global_transactions = {
        {"0:A"},
        {"0:B"}
    };
    REQUIRE(validate_transactions(num_shards, shard_logs, global_transactions) == true);
}

TEST_CASE("Interleaved transactions with multiple shards", "[transaction_validation]") {
    int num_shards = 4;
    vector<vector<string>> shard_logs = {
        {"T1", "T4", "T7"},    // Shard 0
        {"T2", "T5"},          // Shard 1
        {"T3", "T6", "T8"},    // Shard 2
        {"T9"}                 // Shard 3
    };
    vector<vector<string>> global_transactions = {
        {"0:T1", "1:T2", "2:T3"},
        {"0:T4", "1:T5", "2:T6"},
        {"0:T7", "2:T8", "3:T9"}
    };
    // This is valid since the order in each shard respects the global transaction initiation order.
    REQUIRE(validate_transactions(num_shards, shard_logs, global_transactions) == true);
}

TEST_CASE("Edge case: global transaction references non-existent shard", "[transaction_validation]") {
    int num_shards = 2;
    vector<vector<string>> shard_logs = {
        {"T1"},
        {"T2"}
    };
    // Global transaction contains a shard id "2" which is out of range.
    vector<vector<string>> global_transactions = {
        {"0:T1", "2:T3"}
    };
    REQUIRE(validate_transactions(num_shards, shard_logs, global_transactions) == false);
}

TEST_CASE("Edge case: duplicate transactions in global transactions", "[transaction_validation]") {
    int num_shards = 2;
    vector<vector<string>> shard_logs = {
        {"T1", "T3"},
        {"T2", "T4"}
    };
    // Global transactions with duplicate reference to the same shard transaction.
    vector<vector<string>> global_transactions = {
        {"0:T1", "1:T2"},
        {"0:T1", "1:T4"}
    };
    // Even though T1 is duplicated, if the implementation expects unique global transaction entries per shard,
    // then this should be considered invalid.
    REQUIRE(validate_transactions(num_shards, shard_logs, global_transactions) == false);
}