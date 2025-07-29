#include "transaction_coordinator.h"
#include "catch.hpp"
#include <vector>
#include <cstdlib>
#include <ctime>

namespace {

void seed_rand(unsigned int seed) {
    std::srand(seed);
}

} // namespace

TEST_CASE("prepare failure - any service aborts", "[coordinate_transaction]") {
    int N = 3;
    // One of the services fails to prepare.
    std::vector<bool> prepare_results = { true, false, true };
    // Only services that prepared successfully have probabilities.
    std::vector<double> commit_success_probabilities = { 1.0, 1.0 };
    bool result = transaction_coordinator::coordinate_transaction(N, prepare_results, commit_success_probabilities);
    REQUIRE(result == false);
}

TEST_CASE("commit success - all services commit successfully", "[coordinate_transaction]") {
    int N = 3;
    std::vector<bool> prepare_results = { true, true, true };
    std::vector<double> commit_success_probabilities = { 1.0, 1.0, 1.0 };
    seed_rand(42); // Seed fixed for reproducibility.
    bool result = transaction_coordinator::coordinate_transaction(N, prepare_results, commit_success_probabilities);
    REQUIRE(result == true);
}

TEST_CASE("commit failure - one service fails commit", "[coordinate_transaction]") {
    int N = 4;
    std::vector<bool> prepare_results = { true, true, true, true };
    // One service has zero probability to commit.
    std::vector<double> commit_success_probabilities = { 1.0, 1.0, 0.0, 1.0 };
    seed_rand(100); // Seed fixed for reproducibility.
    bool result = transaction_coordinator::coordinate_transaction(N, prepare_results, commit_success_probabilities);
    REQUIRE(result == false);
}

TEST_CASE("empty inputs - no services provided", "[coordinate_transaction]") {
    int N = 0;
    std::vector<bool> prepare_results = {};
    std::vector<double> commit_success_probabilities = {};
    bool result = transaction_coordinator::coordinate_transaction(N, prepare_results, commit_success_probabilities);
    REQUIRE(result == false);
}

TEST_CASE("invalid probability - probability out of range", "[coordinate_transaction]") {
    int N = 2;
    std::vector<bool> prepare_results = { true, true };
    // Second probability is invalid (greater than 1.0).
    std::vector<double> commit_success_probabilities = { 0.5, 1.2 };
    bool result = transaction_coordinator::coordinate_transaction(N, prepare_results, commit_success_probabilities);
    REQUIRE(result == false);
}