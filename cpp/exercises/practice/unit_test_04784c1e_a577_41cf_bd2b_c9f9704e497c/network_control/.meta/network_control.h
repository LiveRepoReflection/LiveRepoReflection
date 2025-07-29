#ifndef NETWORK_CONTROL_H
#define NETWORK_CONTROL_H

#include <vector>
#include <unordered_map>

class NetworkNode {
public:
    NetworkNode(int node_id, int num_nodes, std::vector<std::pair<int, int>> outgoing_links);
    void update_rates(std::unordered_map<int, double> congestion_factors);
    double get_rate(int destination_node_id);

private:
    int node_id_;
    int num_nodes_;
    std::unordered_map<int, int> link_capacities_;
    std::unordered_map<int, double> current_rates_;
    
    // Constants for rate adjustment
    const double INITIAL_RATE = 1.0;
    const double MAX_RATE = 1000.0;
    const double THRESHOLD1 = 0.7;
    const double THRESHOLD2 = 0.9;
    const double ALPHA = 0.1;
    const double BETA = 0.5;

    void initialize_rates();
    double adjust_rate(double current_rate, double congestion_factor);
};

#endif // NETWORK_CONTROL_H