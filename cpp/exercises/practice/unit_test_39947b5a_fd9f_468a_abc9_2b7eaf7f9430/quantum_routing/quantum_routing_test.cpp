#include "quantum_routing.h"
#include "catch.hpp"
#include <cmath>
#include <vector>

bool is_close(double a, double b, double epsilon = 1e-9) {
    return std::abs(a - b) < epsilon;
}

TEST_CASE("Same source and destination", "[quantum_routing]") {
    int n = 5;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    
    int start = 3;
    int end = 3;
    
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), 1.0));
}

TEST_CASE("Direct connection", "[quantum_routing]") {
    int n = 5;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    probabilities[0][1] = 0.5;
    
    int start = 0;
    int end = 1;
    
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), 0.5));
}

TEST_CASE("No path exists", "[quantum_routing]") {
    int n = 5;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    
    int start = 0;
    int end = 4;
    
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), 0.0));
}

TEST_CASE("Indirect connection with better probability", "[quantum_routing]") {
    int n = 3;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    probabilities[0][1] = 0.5;
    probabilities[1][2] = 0.5;
    probabilities[0][2] = 0.1;
    
    int start = 0;
    int end = 2;
    
    // Direct: 0->2 with 0.1 probability
    // Indirect: 0->1->2 with 0.5*0.5 = 0.25 probability
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), 0.25));
}

TEST_CASE("Complex network", "[quantum_routing]") {
    int n = 5;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    probabilities[0][1] = 0.9;
    probabilities[0][2] = 0.8;
    probabilities[1][2] = 0.7;
    probabilities[1][3] = 0.6;
    probabilities[2][3] = 0.5;
    probabilities[2][4] = 0.4;
    probabilities[3][4] = 0.9;
    
    int start = 0;
    int end = 4;
    
    // Path options:
    // 0->2->4 with 0.8*0.4 = 0.32 probability
    // 0->1->3->4 with 0.9*0.6*0.9 = 0.486 probability
    // 0->2->3->4 with 0.8*0.5*0.9 = 0.36 probability
    // 0->1->2->4 with 0.9*0.7*0.4 = 0.252 probability
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), 0.486));
}

TEST_CASE("Asymmetric probabilities", "[quantum_routing]") {
    int n = 4;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    probabilities[0][1] = 0.8;
    probabilities[1][0] = 0.5; // Different from 0->1
    probabilities[1][2] = 0.7;
    probabilities[2][1] = 0.4; // Different from 1->2
    probabilities[2][3] = 0.6;
    probabilities[3][2] = 0.3; // Different from 2->3
    
    int start = 0;
    int end = 3;
    
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), 0.8 * 0.7 * 0.6));
}

TEST_CASE("Multiple paths", "[quantum_routing]") {
    int n = 7;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    // Path 1: 0->1->3->6
    probabilities[0][1] = 0.9;
    probabilities[1][3] = 0.8;
    probabilities[3][6] = 0.7;
    
    // Path 2: 0->2->4->6
    probabilities[0][2] = 0.8;
    probabilities[2][4] = 0.9;
    probabilities[4][6] = 0.8;
    
    // Path 3: 0->5->6
    probabilities[0][5] = 0.75;
    probabilities[5][6] = 0.85;
    
    int start = 0;
    int end = 6;
    
    // Path 1: 0.9*0.8*0.7 = 0.504
    // Path 2: 0.8*0.9*0.8 = 0.576
    // Path 3: 0.75*0.85 = 0.6375
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), 0.6375));
}

TEST_CASE("Cycle in the network", "[quantum_routing]") {
    int n = 4;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    probabilities[0][1] = 0.9;
    probabilities[1][2] = 0.8;
    probabilities[2][0] = 0.7; // Creates a cycle
    probabilities[1][3] = 0.6;
    
    int start = 0;
    int end = 3;
    
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), 0.9 * 0.6));
}

TEST_CASE("Large network", "[quantum_routing]") {
    int n = 100;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    
    // Create a chain: 0->1->2->...->99
    for (int i = 0; i < n - 1; i++) {
        probabilities[i][i+1] = 0.99;
    }
    
    int start = 0;
    int end = n - 1;
    
    // Expected probability: 0.99^99
    double expected = std::pow(0.99, 99);
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), expected));
}

TEST_CASE("Network with disconnected components", "[quantum_routing]") {
    int n = 10;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    
    // Component 1: 0, 1, 2, 3, 4
    probabilities[0][1] = 0.9;
    probabilities[1][2] = 0.8;
    probabilities[2][3] = 0.7;
    probabilities[3][4] = 0.6;
    
    // Component 2: 5, 6, 7, 8, 9
    probabilities[5][6] = 0.9;
    probabilities[6][7] = 0.8;
    probabilities[7][8] = 0.7;
    probabilities[8][9] = 0.6;
    
    // No path from component 1 to component 2
    int start = 0;
    int end = 9;
    
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), 0.0));
}

TEST_CASE("Edge case: very small probabilities", "[quantum_routing]") {
    int n = 5;
    std::vector<std::vector<double>> probabilities(n, std::vector<double>(n, 0.0));
    probabilities[0][1] = 1e-9;
    probabilities[1][2] = 1e-9;
    probabilities[2][3] = 1e-9;
    probabilities[3][4] = 1e-9;
    
    int start = 0;
    int end = 4;
    
    double expected = 1e-36;
    // Use a larger epsilon for very small numbers
    REQUIRE(is_close(quantum_routing::find_highest_probability(probabilities, start, end), expected, 1e-40));
}