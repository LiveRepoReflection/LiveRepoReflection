#include <sstream>
#include <string>
#include <vector>
#include <iomanip>
#include "catch.hpp"
#include "traffic_router.h"

using namespace std;

// Helper function to run a test case by providing input as string and capturing output as string.
string run_test_case(const string& input_data) {
    istringstream iss(input_data);
    ostringstream oss;
    traffic_router::solve(iss, oss);
    return oss.str();
}

TEST_CASE("Single road - simple case") {
    // Graph:
    // 2 intersections, 1 road: 0 -> 1 with capacity=10 and base time=5.
    // Trip requests: 1 trip from 0 to 1 carrying 5 vehicles.
    // Global parameters: congestion_factor = 0.5, exponent = 2.
    // Expected: Flow on the only road is 5.00 (since the only available route is used).
    string input = "2\n"          // Number of intersections
                   "1\n"          // Number of roads
                   "0 1 10 5\n"   // Road: u, v, capacity, base_time
                   "1\n"          // Number of trip requests
                   "0 1 5\n"      // Trip: source, destination, vehicles
                   "0.5\n"        // congestion_factor
                   "2\n";         // exponent

    string expected_output = "5.00\n";
    REQUIRE(run_test_case(input) == expected_output);
}

TEST_CASE("Parallel roads - choose faster road") {
    // Graph:
    // 2 intersections, 2 roads (parallel routes from 0 to 1).
    // Road1: capacity=100, base time=10.
    // Road2: capacity=10, base time=5.
    // Trip request: 0 to 1 with 5 vehicles.
    // Global parameters: congestion_factor = 0.5, exponent = 2.
    // Expected: The optimal solution assigns all 5 vehicles to road2 (the faster route).
    // Therefore, the output should be "0.00" for the first road and "5.00" for the second, in order.
    string input = "2\n"           // Number of intersections
                   "2\n"           // Number of roads
                   "0 1 100 10\n"  // Road1: u, v, capacity, base_time
                   "0 1 10 5\n"    // Road2: u, v, capacity, base_time
                   "1\n"           // Number of trip requests
                   "0 1 5\n"       // Trip: source, destination, vehicles
                   "0.5\n"         // congestion_factor
                   "2\n";          // exponent

    string expected_output = "0.00\n5.00\n";
    REQUIRE(run_test_case(input) == expected_output);
}

TEST_CASE("Unreachable destination - no valid route") {
    // Graph:
    // 3 intersections, 2 roads: 0->1 and 1->0.
    // Trip request: from 0 to 2 carrying 5 vehicles.
    // Global parameters: congestion_factor = 0.2, exponent = 2.
    // Expected: Since destination 2 is unreachable, optimal flows on both roads remain 0.00.
    string input = "3\n"         // Number of intersections
                   "2\n"         // Number of roads
                   "0 1 10 5\n"  // Road1: 0 -> 1
                   "1 0 10 5\n"  // Road2: 1 -> 0
                   "1\n"         // Number of trip requests
                   "0 2 5\n"     // Trip: source, destination, vehicles
                   "0.2\n"       // congestion_factor
                   "2\n";        // exponent

    string expected_output = "0.00\n0.00\n";
    REQUIRE(run_test_case(input) == expected_output);
}