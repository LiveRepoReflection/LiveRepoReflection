#include <sstream>
#include <string>
#include <iostream>
#include "catch.hpp"
#include "task_scheduler.h"

// Helper function to run a test case by redirecting input and output.
void runTest(const std::string &input, const std::string &expected_output) {
    std::istringstream iss(input);
    std::ostringstream oss;
    // Assume that the main solution function is defined as:
    // void scheduleTasks(std::istream& in, std::ostream& out);
    scheduleTasks(iss, oss);
    std::string result = oss.str();
    // Trim trailing newlines or spaces for comparison.
    while (!result.empty() && (result.back() == '\n' || result.back() == ' ')) {
        result.pop_back();
    }
    std::string expected = expected_output;
    while (!expected.empty() && (expected.back() == '\n' || expected.back() == ' ')) {
        expected.pop_back();
    }
    REQUIRE(result == expected);
}

TEST_CASE("Single task meets deadline") {
    std::string input = "1\n"
                        "1 5 5 0\n";
    std::string expected_output = "1";
    runTest(input, expected_output);
}

TEST_CASE("Single task misses deadline") {
    std::string input = "1\n"
                        "1 10 5 0\n";
    std::string expected_output = "0";
    runTest(input, expected_output);
}

TEST_CASE("Two independent tasks both completable") {
    std::string input = "2\n"
                        "1 5 10 0\n"
                        "2 3 10 0\n";
    std::string expected_output = "2";
    runTest(input, expected_output);
}

TEST_CASE("Two tasks with dependency and both completable") {
    std::string input = "2\n"
                        "1 5 10 0\n"
                        "2 6 12 1 1\n";
    std::string expected_output = "2";
    runTest(input, expected_output);
}

TEST_CASE("Dependent task exceeds deadline") {
    std::string input = "2\n"
                        "1 10 10 0\n"
                        "2 5 12 1 1\n";
    // Only task 1 can be completed because including task 2 forces task1 completion which delays task2 past its deadline.
    std::string expected_output = "1";
    runTest(input, expected_output);
}

TEST_CASE("Sample test with 4 tasks") {
    std::string input = "4\n"
                        "1 10 20 0\n"
                        "2 15 30 1 1\n"
                        "3 5 25 1 1\n"
                        "4 20 40 2 2 3\n";
    std::string expected_output = "4";
    runTest(input, expected_output);
}

TEST_CASE("Complex dependency graph with selective scheduling") {
    std::string input = "6\n"
                        "1 3 10 0\n"
                        "2 4 12 1 1\n"
                        "3 5 20 1 1\n"
                        "4 8 18 1 2\n"
                        "5 2 15 2 2 3\n"
                        "6 1 16 1 5\n";
    // Optimal schedule is to complete tasks 1, 2, 3, 5, 6.
    std::string expected_output = "5";
    runTest(input, expected_output);
}