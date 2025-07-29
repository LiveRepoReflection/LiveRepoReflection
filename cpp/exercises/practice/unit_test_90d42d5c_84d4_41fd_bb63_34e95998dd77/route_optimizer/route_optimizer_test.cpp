#include "route_optimizer.h"
#include "catch.hpp"
#include <vector>
#include <utility>

TEST_CASE("Single delivery with perfect reliability") {
    // City graph
    std::vector<std::pair<int, int>> edges = {{0, 1}, {1, 2}};
    std::vector<int> travel_times = {10, 15};
    std::vector<double> toll_costs = {2.5, 3.0};
    std::vector<double> reliabilities = {1.0, 1.0};
    
    // Truck fleet
    std::vector<std::pair<int, double>> trucks = {{1000, 0.2}};
    
    // Delivery requests
    std::vector<std::tuple<int, int, int, int, int>> deliveries = {
        {0, 2, 500, 0, 60}
    };
    
    // Penalty costs
    double late_penalty = 1.0;
    double early_penalty = 0.5;
    double failure_penalty = 1000.0;
    double reliability_threshold = 0.9;
    
    double total_cost = route_optimizer::calculate_optimal_routes(
        edges, travel_times, toll_costs, reliabilities,
        trucks,
        deliveries,
        late_penalty, early_penalty, failure_penalty,
        reliability_threshold
    );
    
    REQUIRE(total_cost == Approx(25 * 0.2 + 5.5).epsilon(0.01));
}

TEST_CASE("Multiple deliveries with truck assignment") {
    // City graph
    std::vector<std::pair<int, int>> edges = {{0, 1}, {1, 2}, {0, 2}};
    std::vector<int> travel_times = {10, 15, 30};
    std::vector<double> toll_costs = {2.5, 3.0, 1.0};
    std::vector<double> reliabilities = {0.95, 0.95, 0.99};
    
    // Truck fleet
    std::vector<std::pair<int, double>> trucks = {{500, 0.2}, {1000, 0.3}};
    
    // Delivery requests
    std::vector<std::tuple<int, int, int, int, int>> deliveries = {
        {0, 2, 400, 0, 60},
        {0, 1, 600, 0, 30}
    };
    
    // Penalty costs
    double late_penalty = 1.0;
    double early_penalty = 0.5;
    double failure_penalty = 1000.0;
    double reliability_threshold = 0.9;
    
    double total_cost = route_optimizer::calculate_optimal_routes(
        edges, travel_times, toll_costs, reliabilities,
        trucks,
        deliveries,
        late_penalty, early_penalty, failure_penalty,
        reliability_threshold
    );
    
    REQUIRE(total_cost > 0);
}

TEST_CASE("Unreliable route penalty") {
    // City graph
    std::vector<std::pair<int, int>> edges = {{0, 1}, {1, 2}};
    std::vector<int> travel_times = {10, 15};
    std::vector<double> toll_costs = {2.5, 3.0};
    std::vector<double> reliabilities = {0.8, 0.7};
    
    // Truck fleet
    std::vector<std::pair<int, double>> trucks = {{1000, 0.2}};
    
    // Delivery requests
    std::vector<std::tuple<int, int, int, int, int>> deliveries = {
        {0, 2, 500, 0, 60}
    };
    
    // Penalty costs
    double late_penalty = 1.0;
    double early_penalty = 0.5;
    double failure_penalty = 1000.0;
    double reliability_threshold = 0.9;
    
    double total_cost = route_optimizer::calculate_optimal_routes(
        edges, travel_times, toll_costs, reliabilities,
        trucks,
        deliveries,
        late_penalty, early_penalty, failure_penalty,
        reliability_threshold
    );
    
    REQUIRE(total_cost == Approx(1000.0).epsilon(0.01));
}

TEST_CASE("Late delivery penalty calculation") {
    // City graph
    std::vector<std::pair<int, int>> edges = {{0, 1}, {1, 2}};
    std::vector<int> travel_times = {30, 40};
    std::vector<double> toll_costs = {2.5, 3.0};
    std::vector<double> reliabilities = {1.0, 1.0};
    
    // Truck fleet
    std::vector<std::pair<int, double>> trucks = {{1000, 0.2}};
    
    // Delivery requests
    std::vector<std::tuple<int, int, int, int, int>> deliveries = {
        {0, 2, 500, 0, 60}
    };
    
    // Penalty costs
    double late_penalty = 1.0;
    double early_penalty = 0.5;
    double failure_penalty = 1000.0;
    double reliability_threshold = 0.9;
    
    double total_cost = route_optimizer::calculate_optimal_routes(
        edges, travel_times, toll_costs, reliabilities,
        trucks,
        deliveries,
        late_penalty, early_penalty, failure_penalty,
        reliability_threshold
    );
    
    REQUIRE(total_cost == Approx(70 * 0.2 + 5.5 + 10 * 1.0).epsilon(0.01));
}

TEST_CASE("Early delivery penalty calculation") {
    // City graph
    std::vector<std::pair<int, int>> edges = {{0, 1}, {1, 2}};
    std::vector<int> travel_times = {10, 15};
    std::vector<double> toll_costs = {2.5, 3.0};
    std::vector<double> reliabilities = {1.0, 1.0};
    
    // Truck fleet
    std::vector<std::pair<int, double>> trucks = {{1000, 0.2}};
    
    // Delivery requests
    std::vector<std::tuple<int, int, int, int, int>> deliveries = {
        {0, 2, 500, 30, 60}
    };
    
    // Penalty costs
    double late_penalty = 1.0;
    double early_penalty = 0.5;
    double failure_penalty = 1000.0;
    double reliability_threshold = 0.9;
    
    double total_cost = route_optimizer::calculate_optimal_routes(
        edges, travel_times, toll_costs, reliabilities,
        trucks,
        deliveries,
        late_penalty, early_penalty, failure_penalty,
        reliability_threshold
    );
    
    REQUIRE(total_cost == Approx(25 * 0.2 + 5.5 + 5 * 0.5).epsilon(0.01));
}