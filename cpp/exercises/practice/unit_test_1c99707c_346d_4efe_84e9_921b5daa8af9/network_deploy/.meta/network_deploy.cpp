#include "network_deploy.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>
#include <queue>

namespace network_deploy {

// Calculate the expected throughput for a given placement of service nodes
double calculate_expected_throughput(
    const std::vector<int>& placement,
    const std::vector<std::vector<int>>& network_graph,
    const std::vector<double>& failure_probabilities,
    const std::vector<std::vector<double>>& throughput_matrix) {
    
    double expected_throughput = 0.0;
    int num_datacenters = static_cast<int>(placement.size());
    
    for (int i = 0; i < num_datacenters; ++i) {
        if (placement[i] == 0) continue;
        
        for (int j = i + 1; j < num_datacenters; ++j) {
            if (placement[j] == 0) continue;
            if (network_graph[i][j] == -1) continue;
            
            // Probability that both data centers are operational
            double prob_i_operational = 1.0 - failure_probabilities[i];
            double prob_j_operational = 1.0 - failure_probabilities[j];
            double both_operational = prob_i_operational * prob_j_operational;
            
            // Calculate throughput contribution
            double latency_factor = 1.0 / network_graph[i][j];
            double throughput_contribution = latency_factor * throughput_matrix[i][j];
            
            // Add to expected throughput
            expected_throughput += both_operational * throughput_contribution;
        }
    }
    
    return expected_throughput;
}

// Check if a placement is valid
bool is_valid_placement(
    const std::vector<int>& placement,
    const std::vector<int>& capacity,
    int min_nodes) {
    
    int total_nodes = 0;
    for (size_t i = 0; i < placement.size(); ++i) {
        if (placement[i] < 0 || placement[i] > capacity[i]) {
            return false;
        }
        total_nodes += placement[i];
    }
    
    return total_nodes >= min_nodes;
}

// Structure to represent state for the optimization process
struct State {
    std::vector<int> placement;
    int total_nodes;
    double expected_throughput;
    
    State(const std::vector<int>& p, int n, double t)
        : placement(p), total_nodes(n), expected_throughput(t) {}
    
    // For priority queue (max heap based on throughput)
    bool operator<(const State& other) const {
        return expected_throughput < other.expected_throughput;
    }
};

// Recursive function with memoization to explore placements
std::vector<int> explore_optimal_placement(
    int datacenter_idx,
    std::vector<int>& current_placement,
    int current_nodes,
    int min_nodes,
    const std::vector<int>& capacity,
    const std::vector<std::vector<int>>& network_graph,
    const std::vector<double>& failure_probabilities,
    const std::vector<std::vector<double>>& throughput_matrix,
    double& best_throughput,
    std::vector<int>& best_placement) {
    
    int num_datacenters = static_cast<int>(capacity.size());
    
    // If we've processed all datacenters, check if the placement is valid
    if (datacenter_idx == num_datacenters) {
        if (current_nodes >= min_nodes) {
            double throughput = calculate_expected_throughput(
                current_placement, network_graph, failure_probabilities, throughput_matrix);
            
            if (throughput > best_throughput) {
                best_throughput = throughput;
                best_placement = current_placement;
            }
        }
        return best_placement;
    }
    
    // Pruning: if even placing all remaining capacity won't reach min_nodes, return early
    int max_possible_nodes = current_nodes;
    for (int i = datacenter_idx; i < num_datacenters; ++i) {
        max_possible_nodes += capacity[i];
    }
    
    if (max_possible_nodes < min_nodes) {
        return best_placement;
    }
    
    // Try different allocations for the current datacenter
    for (int nodes = 0; nodes <= capacity[datacenter_idx]; ++nodes) {
        current_placement[datacenter_idx] = nodes;
        explore_optimal_placement(
            datacenter_idx + 1,
            current_placement,
            current_nodes + nodes,
            min_nodes,
            capacity,
            network_graph,
            failure_probabilities,
            throughput_matrix,
            best_throughput,
            best_placement
        );
    }
    
    return best_placement;
}

// Enhanced beam search approach with pruning
std::vector<int> beam_search_placement(
    int num_datacenters,
    const std::vector<int>& capacity,
    const std::vector<std::vector<int>>& network_graph,
    int min_nodes,
    const std::vector<double>& failure_probabilities,
    const std::vector<std::vector<double>>& throughput_matrix) {
    
    const int BEAM_WIDTH = 1000;  // Adjust based on problem size and time constraints
    
    // Initialize with empty placement
    std::vector<int> initial_placement(num_datacenters, 0);
    std::priority_queue<State> beam;
    beam.push(State(initial_placement, 0, 0.0));
    
    std::vector<int> best_placement;
    double best_throughput = -1.0;
    
    while (!beam.empty()) {
        // Get the current best states
        std::vector<State> current_states;
        for (int i = 0; i < BEAM_WIDTH && !beam.empty(); ++i) {
            current_states.push_back(beam.top());
            beam.pop();
        }
        
        // For each state, generate next states
        for (const State& state : current_states) {
            // If this is a complete placement and satisfies min_nodes
            if (state.total_nodes >= min_nodes) {
                double throughput = calculate_expected_throughput(
                    state.placement, network_graph, failure_probabilities, throughput_matrix);
                
                if (throughput > best_throughput) {
                    best_throughput = throughput;
                    best_placement = state.placement;
                }
            }
            
            // Find the next datacenter to update
            int next_dc = -1;
            for (int i = 0; i < num_datacenters; ++i) {
                if (state.placement[i] < capacity[i]) {
                    next_dc = i;
                    break;
                }
            }
            
            if (next_dc == -1) continue;  // All datacenters at capacity
            
            // Try incrementing the node count for this datacenter
            std::vector<int> new_placement = state.placement;
            new_placement[next_dc]++;
            
            double new_throughput = calculate_expected_throughput(
                new_placement, network_graph, failure_probabilities, throughput_matrix);
            
            beam.push(State(new_placement, state.total_nodes + 1, new_throughput));
        }
        
        // If beam is empty but we haven't found a valid solution, 
        // it means we can't satisfy min_nodes constraint
        if (beam.empty() && best_placement.empty()) {
            return {};  // Return empty vector
        }
    }
    
    return best_placement;
}

// Use simulated annealing for larger problem sizes
std::vector<int> simulated_annealing(
    int num_datacenters,
    const std::vector<int>& capacity,
    const std::vector<std::vector<int>>& network_graph,
    int min_nodes,
    const std::vector<double>& failure_probabilities,
    const std::vector<std::vector<double>>& throughput_matrix) {
    
    // Check if it's even possible to meet min_nodes
    int total_capacity = 0;
    for (int cap : capacity) {
        total_capacity += cap;
    }
    
    if (total_capacity < min_nodes) {
        return {};  // Not possible to meet min_nodes
    }
    
    // Parameters for simulated annealing
    const double INITIAL_TEMP = 100.0;
    const double COOLING_RATE = 0.995;
    const int MAX_ITERATIONS = 10000;
    
    // Start with a random valid placement
    std::vector<int> current_placement(num_datacenters, 0);
    int nodes_to_place = min_nodes;
    
    // Distribute nodes randomly but ensure we meet min_nodes
    for (int i = 0; i < num_datacenters && nodes_to_place > 0; ++i) {
        int nodes = std::min(capacity[i], nodes_to_place);
        current_placement[i] = nodes;
        nodes_to_place -= nodes;
    }
    
    double current_throughput = calculate_expected_throughput(
        current_placement, network_graph, failure_probabilities, throughput_matrix);
    
    std::vector<int> best_placement = current_placement;
    double best_throughput = current_throughput;
    
    double temperature = INITIAL_TEMP;
    
    // Main simulated annealing loop
    for (int iteration = 0; iteration < MAX_ITERATIONS; ++iteration) {
        // Generate a neighbor state by moving a node
        std::vector<int> neighbor = current_placement;
        
        // Pick a random source and destination datacenter
        int source_dc = rand() % num_datacenters;
        int dest_dc = rand() % num_datacenters;
        
        // Ensure source has nodes to move and destination has capacity
        if (source_dc != dest_dc && neighbor[source_dc] > 0 && neighbor[dest_dc] < capacity[dest_dc]) {
            neighbor[source_dc]--;
            neighbor[dest_dc]++;
            
            // Calculate new throughput
            double neighbor_throughput = calculate_expected_throughput(
                neighbor, network_graph, failure_probabilities, throughput_matrix);
            
            // Decide whether to accept the new state
            double delta = neighbor_throughput - current_throughput;
            
            if (delta > 0 || (std::exp(delta / temperature) > (rand() / static_cast<double>(RAND_MAX)))) {
                current_placement = neighbor;
                current_throughput = neighbor_throughput;
                
                // Update best if this is better
                if (current_throughput > best_throughput) {
                    best_throughput = current_throughput;
                    best_placement = current_placement;
                }
            }
        }
        
        // Cool down
        temperature *= COOLING_RATE;
    }
    
    return best_placement;
}

// Combined approach using both exact and heuristic methods
std::vector<int> optimal_placement(
    int num_datacenters,
    const std::vector<int>& capacity,
    const std::vector<std::vector<int>>& network_graph,
    int min_nodes,
    const std::vector<double>& failure_probabilities,
    const std::vector<std::vector<double>>& throughput_matrix) {
    
    // Sanity check for input validity
    if (num_datacenters <= 0 || 
        capacity.size() != static_cast<size_t>(num_datacenters) ||
        network_graph.size() != static_cast<size_t>(num_datacenters) ||
        failure_probabilities.size() != static_cast<size_t>(num_datacenters) ||
        throughput_matrix.size() != static_cast<size_t>(num_datacenters)) {
        return {};  // Invalid input
    }
    
    for (const auto& row : network_graph) {
        if (row.size() != static_cast<size_t>(num_datacenters)) {
            return {};  // Invalid network graph
        }
    }
    
    for (const auto& row : throughput_matrix) {
        if (row.size() != static_cast<size_t>(num_datacenters)) {
            return {};  // Invalid throughput matrix
        }
    }
    
    // Check if total capacity can support min_nodes
    int total_capacity = 0;
    for (int cap : capacity) {
        if (cap < 0) return {}; // Invalid capacity
        total_capacity += cap;
    }
    
    if (total_capacity < min_nodes) {
        return {};  // Not possible to meet min_nodes
    }
    
    // For small problems, use exact approach with recursion
    if (num_datacenters <= 10) {
        std::vector<int> current_placement(num_datacenters, 0);
        double best_throughput = -1.0;
        std::vector<int> best_placement;
        
        return explore_optimal_placement(
            0, 
            current_placement, 
            0, 
            min_nodes, 
            capacity, 
            network_graph, 
            failure_probabilities, 
            throughput_matrix, 
            best_throughput, 
            best_placement
        );
    }
    // For medium problems, use beam search
    else if (num_datacenters <= 12) {
        return beam_search_placement(
            num_datacenters, 
            capacity, 
            network_graph, 
            min_nodes, 
            failure_probabilities, 
            throughput_matrix
        );
    }
    // For larger problems, use simulated annealing
    else {
        return simulated_annealing(
            num_datacenters, 
            capacity, 
            network_graph, 
            min_nodes, 
            failure_probabilities, 
            throughput_matrix
        );
    }
}

} // namespace network_deploy