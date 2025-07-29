#include "network_control.h"
#include <algorithm>

NetworkNode::NetworkNode(int node_id, int num_nodes, std::vector<std::pair<int, int>> outgoing_links)
    : node_id_(node_id), num_nodes_(num_nodes) {
    
    // Initialize link capacities
    for (const auto& link : outgoing_links) {
        link_capacities_[link.first] = link.second;
    }
    
    initialize_rates();
}

void NetworkNode::initialize_rates() {
    // Set initial rates for all outgoing links
    for (const auto& link : link_capacities_) {
        current_rates_[link.first] = INITIAL_RATE;
    }
}

double NetworkNode::adjust_rate(double current_rate, double congestion_factor) {
    double new_rate = current_rate;
    
    if (congestion_factor < THRESHOLD1) {
        // Additive increase
        new_rate = current_rate + ALPHA;
    } else if (congestion_factor > THRESHOLD2) {
        // Multiplicative decrease
        new_rate = current_rate * BETA;
    }
    // else: maintain current rate
    
    // Ensure rate stays within bounds
    new_rate = std::max(0.0, std::min(new_rate, MAX_RATE));
    
    return new_rate;
}

void NetworkNode::update_rates(std::unordered_map<int, double> congestion_factors) {
    for (auto& rate_entry : current_rates_) {
        int dest_node = rate_entry.first;
        
        // Only update if we have congestion information for this link
        if (congestion_factors.find(dest_node) != congestion_factors.end()) {
            double current_rate = rate_entry.second;
            double congestion_factor = congestion_factors[dest_node];
            
            // Calculate and update new rate
            rate_entry.second = adjust_rate(current_rate, congestion_factor);
        }
    }
}

double NetworkNode::get_rate(int destination_node_id) {
    // Return 0 if no direct link exists to the destination
    if (current_rates_.find(destination_node_id) == current_rates_.end()) {
        return 0.0;
    }
    
    return current_rates_[destination_node_id];
}