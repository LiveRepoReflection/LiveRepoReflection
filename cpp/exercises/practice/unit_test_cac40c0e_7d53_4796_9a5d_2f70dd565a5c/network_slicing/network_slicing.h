#if !defined(NETWORK_SLICING_H)
#define NETWORK_SLICING_H

#include <vector>
#include <unordered_map>
#include <utility>

struct PhysicalNode {
    int cpu;
    int memory;
    int bandwidth;
};

struct PhysicalEdge {
    int bandwidth;
    int latency;
};

struct VirtualNode {
    int cpu;
    int memory;
    int bandwidth;
};

struct VirtualEdge {
    int bandwidth;
};

struct LatencyRequirement {
    int from_node;
    int to_node;
    int max_latency;
};

struct PhysicalNetwork {
    std::vector<PhysicalNode> nodes;
    std::vector<std::tuple<int, int, PhysicalEdge>> edges;
};

struct NetworkSlice {
    std::vector<VirtualNode> nodes;
    std::vector<std::tuple<int, int, VirtualEdge>> edges;
    std::vector<LatencyRequirement> latency_requirements;
    int revenue;
};

struct SliceMapping {
    std::unordered_map<int, int> node_mapping;  // virtual node -> physical node
    std::vector<std::vector<int>> path_mapping;  // virtual edge -> physical path
};

struct OptimizationResult {
    std::vector<SliceMapping> mappings;
    int revenue;
};

namespace network_slicing {
    OptimizationResult optimize_network_slicing(const PhysicalNetwork& physical, 
                                              const std::vector<NetworkSlice>& slices);
}

#endif // NETWORK_SLICING_H