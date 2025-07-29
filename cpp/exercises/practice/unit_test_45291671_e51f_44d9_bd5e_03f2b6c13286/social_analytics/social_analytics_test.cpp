#include <sstream>
#include <string>
#include <vector>
#include "catch.hpp"
#include "social_analytics.h"

TEST_CASE("Reachability queries and connection updates", "[social_analytics]") {
    std::string commands =
        "ADD_USER 1\n"
        "ADD_USER 2\n"
        "ADD_USER 3\n"
        "ADD_USER 4\n"
        "ADD_CONNECTION 1 2\n"
        "ADD_CONNECTION 2 3\n"
        "ARE_REACHABLE 1 3\n"
        "ARE_REACHABLE 1 4\n"
        "ADD_CONNECTION 3 4\n"
        "ARE_REACHABLE 1 4\n"
        "REMOVE_CONNECTION 2 3\n"
        "ARE_REACHABLE 1 3\n";
    
    std::istringstream iss(commands);
    std::ostringstream oss;
    
    // processCommands reads from istream and writes to ostream.
    social_analytics::processCommands(iss, oss);
    
    std::string output = oss.str();
    std::istringstream outputStream(output);
    std::string line;
    std::vector<std::string> results;
    while (std::getline(outputStream, line)) {
        if (!line.empty()) {
            results.push_back(line);
        }
    }
    
    // Expected outputs:
    // ARE_REACHABLE 1 3 -> "TRUE" (1-2-3 exists)
    // ARE_REACHABLE 1 4 -> "FALSE" (no connection yet)
    // ARE_REACHABLE 1 4 -> "TRUE" (after adding 3-4, path 1-2-3-4 exists)
    // ARE_REACHABLE 1 3 -> "FALSE" (after removing 2-3, disconnects 3 from 1)
    REQUIRE(results.size() == 4);
    REQUIRE(results[0] == "TRUE");
    REQUIRE(results[1] == "FALSE");
    REQUIRE(results[2] == "TRUE");
    REQUIRE(results[3] == "FALSE");
}

TEST_CASE("Influence score queries with varying degrees", "[social_analytics]") {
    std::string commands =
        "ADD_USER 10\n"
        "ADD_USER 20\n"
        "ADD_USER 30\n"
        "ADD_USER 40\n"
        "ADD_USER 50\n"
        "ADD_CONNECTION 10 20\n"
        "ADD_CONNECTION 20 30\n"
        "ADD_CONNECTION 30 40\n"
        "ADD_CONNECTION 40 50\n"
        "INFLUENCE_SCORE 20 1\n"  // For user 20, degree 1 neighbors: 10 and 30 => count: 2
        "INFLUENCE_SCORE 20 2\n"; // For user 20, degree 2: reachable nodes are 10, 30, and 40 => count: 3
    
    std::istringstream iss(commands);
    std::ostringstream oss;
    
    social_analytics::processCommands(iss, oss);
    
    std::string output = oss.str();
    std::istringstream outputStream(output);
    std::string line;
    std::vector<std::string> results;
    while (std::getline(outputStream, line)) {
        if (!line.empty()) {
            results.push_back(line);
        }
    }
    
    REQUIRE(results.size() == 2);
    REQUIRE(results[0] == "2");
    REQUIRE(results[1] == "3");
}

TEST_CASE("User removal and subsequent operations", "[social_analytics]") {
    std::string commands =
        "ADD_USER 100\n"
        "ADD_USER 200\n"
        "ADD_CONNECTION 100 200\n"
        "ARE_REACHABLE 100 200\n"  // Should output "TRUE"
        "REMOVE_USER 200\n"
        "ARE_REACHABLE 100 200\n"  // After removal, output "FALSE"
        "INFLUENCE_SCORE 100 1\n"  // Now, user 100 has no neighbors => 0
        "ADD_USER 200\n"
        "ADD_CONNECTION 100 200\n"
        "INFLUENCE_SCORE 100 1\n"; // Re-established connection: now neighbor count => 1
    
    std::istringstream iss(commands);
    std::ostringstream oss;
    
    social_analytics::processCommands(iss, oss);
    
    std::string output = oss.str();
    std::istringstream outputStream(output);
    std::string line;
    std::vector<std::string> results;
    while (std::getline(outputStream, line)) {
        if (!line.empty()) {
            results.push_back(line);
        }
    }
    
    // Expected outputs in order:
    // 1st ARE_REACHABLE: "TRUE"
    // 2nd ARE_REACHABLE: "FALSE"
    // 1st INFLUENCE_SCORE: "0"
    // 2nd INFLUENCE_SCORE: "1"
    REQUIRE(results.size() == 4);
    REQUIRE(results[0] == "TRUE");
    REQUIRE(results[1] == "FALSE");
    REQUIRE(results[2] == "0");
    REQUIRE(results[3] == "1");
}