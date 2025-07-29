#include "network_deploy.h"
#include <vector>
#include <iostream>
#include <stdexcept>
#include <cmath>
#include "catch.hpp"

bool areVectorsEqual(const std::vector<int>& a, const std::vector<int>& b) {
    if (a.size() != b.size()) return false;
    
    for (size_t i = 0; i < a.size(); ++i) {
        if (a[i] != b[i]) return false;
    }
    
    return true;
}

double calculateExpectedThroughput(
    const std::vector<int>& placement,
    const std::vector<std::vector<int>>& network_graph,
    const std::vector<double>& failure_probabilities,
    const std::vector<std::vector<double>>& throughput_matrix
) {
    double expected_throughput = 0.0;
    
    for (size_t i = 0; i < placement.size(); ++i) {
        if (placement[i] == 0) continue;
        
        for (size_t j = i + 1; j < placement.size(); ++j) {
            if (placement[j] == 0) continue;
            if (network_graph[i][j] == -1) continue;
            
            double prob_i_working = 1.0 - failure_probabilities[i];
            double prob_j_working = 1.0 - failure_probabilities[j];
            double both_working = prob_i_working * prob_j_working;
            
            double contribution = 0.0;
            if (network_graph[i][j] > 0) {
                contribution = (1.0 / network_graph[i][j]) * throughput_matrix[i][j];
            }
            
            expected_throughput += both_working * contribution;
        }
    }
    
    return expected_throughput;
}

bool isValidPlacement(
    const std::vector<int>& placement,
    const std::vector<int>& capacity,
    int min_nodes
) {
    if (placement.size() != capacity.size()) return false;
    
    int total_nodes = 0;
    for (size_t i = 0; i < placement.size(); ++i) {
        if (placement[i] < 0 || placement[i] > capacity[i]) return false;
        total_nodes += placement[i];
    }
    
    return total_nodes >= min_nodes;
}

TEST_CASE("Simple case with 2 data centers") {
    int num_datacenters = 2;
    std::vector<int> capacity = {2, 3};
    std::vector<std::vector<int>> network_graph = {
        {0, 10},
        {10, 0}
    };
    int min_nodes = 3;
    std::vector<double> failure_probabilities = {0.1, 0.2};
    std::vector<std::vector<double>> throughput_matrix = {
        {0, 100},
        {100, 0}
    };
    
    std::vector<int> result = network_deploy::optimal_placement(
        num_datacenters, capacity, network_graph, min_nodes, 
        failure_probabilities, throughput_matrix
    );
    
    REQUIRE(isValidPlacement(result, capacity, min_nodes));
    
    // The optimal solution should have some placement with total nodes >= min_nodes
    int total_nodes = 0;
    for (int nodes : result) {
        total_nodes += nodes;
    }
    
    REQUIRE(total_nodes >= min_nodes);
    
    // We can't assert the exact expected throughput, but we can verify it's greater than 0
    double throughput = calculateExpectedThroughput(
        result, network_graph, failure_probabilities, throughput_matrix
    );
    
    REQUIRE(throughput > 0.0);
}

TEST_CASE("Multiple data centers with some disconnected") {
    int num_datacenters = 4;
    std::vector<int> capacity = {2, 3, 1, 2};
    std::vector<std::vector<int>> network_graph = {
        {0, 10, -1, 20},
        {10, 0, 15, -1},
        {-1, 15, 0, 5},
        {20, -1, 5, 0}
    };
    int min_nodes = 5;
    std::vector<double> failure_probabilities = {0.1, 0.2, 0.15, 0.25};
    std::vector<std::vector<double>> throughput_matrix = {
        {0, 100, 0, 80},
        {100, 0, 120, 0},
        {0, 120, 0, 150},
        {80, 0, 150, 0}
    };
    
    std::vector<int> result = network_deploy::optimal_placement(
        num_datacenters, capacity, network_graph, min_nodes, 
        failure_probabilities, throughput_matrix
    );
    
    REQUIRE(isValidPlacement(result, capacity, min_nodes));
    
    double throughput = calculateExpectedThroughput(
        result, network_graph, failure_probabilities, throughput_matrix
    );
    
    REQUIRE(throughput > 0.0);
}

TEST_CASE("Edge case: Minimum nodes equals total capacity") {
    int num_datacenters = 3;
    std::vector<int> capacity = {2, 3, 1};
    std::vector<std::vector<int>> network_graph = {
        {0, 10, 20},
        {10, 0, 15},
        {20, 15, 0}
    };
    int min_nodes = 6; // Equal to sum of capacities
    std::vector<double> failure_probabilities = {0.1, 0.2, 0.15};
    std::vector<std::vector<double>> throughput_matrix = {
        {0, 100, 80},
        {100, 0, 120},
        {80, 120, 0}
    };
    
    std::vector<int> result = network_deploy::optimal_placement(
        num_datacenters, capacity, network_graph, min_nodes, 
        failure_probabilities, throughput_matrix
    );
    
    REQUIRE(isValidPlacement(result, capacity, min_nodes));
    
    // Should use all available capacity
    REQUIRE(result[0] == capacity[0]);
    REQUIRE(result[1] == capacity[1]);
    REQUIRE(result[2] == capacity[2]);
}

TEST_CASE("Edge case: Minimum nodes greater than total capacity") {
    int num_datacenters = 3;
    std::vector<int> capacity = {2, 3, 1};
    std::vector<std::vector<int>> network_graph = {
        {0, 10, 20},
        {10, 0, 15},
        {20, 15, 0}
    };
    int min_nodes = 7; // Greater than sum of capacities (6)
    std::vector<double> failure_probabilities = {0.1, 0.2, 0.15};
    std::vector<std::vector<double>> throughput_matrix = {
        {0, 100, 80},
        {100, 0, 120},
        {80, 120, 0}
    };
    
    std::vector<int> result = network_deploy::optimal_placement(
        num_datacenters, capacity, network_graph, min_nodes, 
        failure_probabilities, throughput_matrix
    );
    
    // Should return empty vector as no valid placement exists
    REQUIRE(result.empty());
}

TEST_CASE("Edge case: All data centers have high failure probability") {
    int num_datacenters = 3;
    std::vector<int> capacity = {2, 3, 1};
    std::vector<std::vector<int>> network_graph = {
        {0, 10, 20},
        {10, 0, 15},
        {20, 15, 0}
    };
    int min_nodes = 4;
    std::vector<double> failure_probabilities = {0.9, 0.95, 0.99}; // High failure probabilities
    std::vector<std::vector<double>> throughput_matrix = {
        {0, 100, 80},
        {100, 0, 120},
        {80, 120, 0}
    };
    
    std::vector<int> result = network_deploy::optimal_placement(
        num_datacenters, capacity, network_graph, min_nodes, 
        failure_probabilities, throughput_matrix
    );
    
    REQUIRE(isValidPlacement(result, capacity, min_nodes));
    
    double throughput = calculateExpectedThroughput(
        result, network_graph, failure_probabilities, throughput_matrix
    );
    
    // Expected throughput should be low due to high failure rates
    REQUIRE(throughput >= 0.0);
}

TEST_CASE("Edge case: All connections have very high latency") {
    int num_datacenters = 3;
    std::vector<int> capacity = {2, 3, 1};
    std::vector<std::vector<int>> network_graph = {
        {0, 1000, 1000},  // Very high latency
        {1000, 0, 1000},
        {1000, 1000, 0}
    };
    int min_nodes = 4;
    std::vector<double> failure_probabilities = {0.1, 0.2, 0.15};
    std::vector<std::vector<double>> throughput_matrix = {
        {0, 100, 80},
        {100, 0, 120},
        {80, 120, 0}
    };
    
    std::vector<int> result = network_deploy::optimal_placement(
        num_datacenters, capacity, network_graph, min_nodes, 
        failure_probabilities, throughput_matrix
    );
    
    REQUIRE(isValidPlacement(result, capacity, min_nodes));
    
    double throughput = calculateExpectedThroughput(
        result, network_graph, failure_probabilities, throughput_matrix
    );
    
    // Expected throughput should be low due to high latencies
    REQUIRE(throughput >= 0.0);
}

TEST_CASE("Larger network with varying parameters") {
    int num_datacenters = 5;
    std::vector<int> capacity = {5, 3, 4, 2, 6};
    std::vector<std::vector<int>> network_graph = {
        {0, 10, 20, -1, 15},
        {10, 0, 15, 25, -1},
        {20, 15, 0, 10, 30},
        {-1, 25, 10, 0, 20},
        {15, -1, 30, 20, 0}
    };
    int min_nodes = 10;
    std::vector<double> failure_probabilities = {0.1, 0.15, 0.2, 0.25, 0.3};
    std::vector<std::vector<double>> throughput_matrix = {
        {0, 100, 80, 0, 120},
        {100, 0, 90, 110, 0},
        {80, 90, 0, 70, 130},
        {0, 110, 70, 0, 85},
        {120, 0, 130, 85, 0}
    };
    
    std::vector<int> result = network_deploy::optimal_placement(
        num_datacenters, capacity, network_graph, min_nodes, 
        failure_probabilities, throughput_matrix
    );
    
    REQUIRE(isValidPlacement(result, capacity, min_nodes));
    
    double throughput = calculateExpectedThroughput(
        result, network_graph, failure_probabilities, throughput_matrix
    );
    
    REQUIRE(throughput > 0.0);
}

TEST_CASE("Maximum size problem") {
    int num_datacenters = 15;
    std::vector<int> capacity(num_datacenters, 10);  // Each datacenter has capacity 10
    
    // Create a fully connected network with random latencies
    std::vector<std::vector<int>> network_graph(num_datacenters, std::vector<int>(num_datacenters, 0));
    for (int i = 0; i < num_datacenters; ++i) {
        for (int j = i + 1; j < num_datacenters; ++j) {
            network_graph[i][j] = 10 + (i * j) % 50;  // Some deterministic variation
            network_graph[j][i] = network_graph[i][j];
        }
    }
    
    int min_nodes = 50;
    
    std::vector<double> failure_probabilities(num_datacenters, 0.1);  // All have 10% failure rate
    
    // Create throughput matrix with random values
    std::vector<std::vector<double>> throughput_matrix(num_datacenters, std::vector<double>(num_datacenters, 0));
    for (int i = 0; i < num_datacenters; ++i) {
        for (int j = i + 1; j < num_datacenters; ++j) {
            throughput_matrix[i][j] = 50 + (i * j) % 100;  // Some deterministic variation
            throughput_matrix[j][i] = throughput_matrix[i][j];
        }
    }
    
    // This test might take longer to run due to the problem size
    std::vector<int> result = network_deploy::optimal_placement(
        num_datacenters, capacity, network_graph, min_nodes, 
        failure_probabilities, throughput_matrix
    );
    
    REQUIRE(isValidPlacement(result, capacity, min_nodes));
    
    double throughput = calculateExpectedThroughput(
        result, network_graph, failure_probabilities, throughput_matrix
    );
    
    REQUIRE(throughput > 0.0);
}