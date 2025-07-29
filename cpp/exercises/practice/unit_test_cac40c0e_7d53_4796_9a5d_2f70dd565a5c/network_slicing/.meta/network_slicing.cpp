#include "network_slicing.h"
#include <algorithm>
#include <queue>
#include <limits>
#include <unordered_set>

namespace network_slicing {

// Helper struct for tracking resource usage
struct ResourceUsage {
    std::vector<PhysicalNode> remaining_nodes;
    std::vector<std::tuple<int, int, PhysicalEdge>> remaining_edges;
};

// Helper function to check if a path satisfies latency constraints
bool check_latency_constraint(const std::vector<int>& path,
                            const PhysicalNetwork& physical,
                            int max_latency) {
    int total_latency = 0;
    for (size_t i = 0; i < path.size() - 1; ++i) {
        int u = path[i], v = path[i + 1];
        bool found = false;
        for (const auto& edge : physical.edges) {
            if ((std::get<0>(edge) == u && std::get<1>(edge) == v) ||
                (std::get<0>(edge) == v && std::get<1>(edge) == u)) {
                total_latency += std::get<2>(edge).latency;
                found = true;
                break;
            }
        }
        if (!found || total_latency > max_latency) return false;
    }
    return total_latency <= max_latency;
}

// Helper function to find shortest path using Dijkstra's algorithm
std::vector<int> find_shortest_path(const PhysicalNetwork& physical,
                                  const ResourceUsage& usage,
                                  int start, int end,
                                  int required_bandwidth,
                                  int max_latency) {
    const int INF = std::numeric_limits<int>::max();
    std::vector<int> dist(physical.nodes.size(), INF);
    std::vector<int> prev(physical.nodes.size(), -1);
    std::vector<bool> visited(physical.nodes.size(), false);
    
    dist[start] = 0;
    
    for (size_t i = 0; i < physical.nodes.size(); ++i) {
        int u = -1;
        int min_dist = INF;
        
        for (size_t j = 0; j < physical.nodes.size(); ++j) {
            if (!visited[j] && dist[j] < min_dist) {
                u = j;
                min_dist = dist[j];
            }
        }
        
        if (u == -1) break;
        visited[u] = true;
        
        for (const auto& edge : usage.remaining_edges) {
            int v = (std::get<0>(edge) == u) ? std::get<1>(edge) : 
                   (std::get<1>(edge) == u) ? std::get<0>(edge) : -1;
            
            if (v != -1 && !visited[v]) {
                const auto& edge_data = std::get<2>(edge);
                if (edge_data.bandwidth >= required_bandwidth) {
                    int new_dist = dist[u] + edge_data.latency;
                    if (new_dist < dist[v]) {
                        dist[v] = new_dist;
                        prev[v] = u;
                    }
                }
            }
        }
    }
    
    if (dist[end] == INF || dist[end] > max_latency) {
        return std::vector<int>();
    }
    
    std::vector<int> path;
    for (int v = end; v != -1; v = prev[v]) {
        path.push_back(v);
    }
    std::reverse(path.begin(), path.end());
    return path;
}

// Helper function to update resource usage after mapping
void update_resource_usage(ResourceUsage& usage,
                         const SliceMapping& mapping,
                         const NetworkSlice& slice) {
    // Update node resources
    for (size_t i = 0; i < slice.nodes.size(); ++i) {
        int physical_node = mapping.node_mapping.at(i);
        auto& node = usage.remaining_nodes[physical_node];
        node.cpu -= slice.nodes[i].cpu;
        node.memory -= slice.nodes[i].memory;
        node.bandwidth -= slice.nodes[i].bandwidth;
    }
    
    // Update edge resources
    for (size_t i = 0; i < mapping.path_mapping.size(); ++i) {
        const auto& path = mapping.path_mapping[i];
        const auto& virtual_edge = slice.edges[i];
        int bandwidth = std::get<2>(virtual_edge).bandwidth;
        
        for (size_t j = 0; j < path.size() - 1; ++j) {
            int u = path[j], v = path[j + 1];
            for (auto& edge : usage.remaining_edges) {
                if ((std::get<0>(edge) == u && std::get<1>(edge) == v) ||
                    (std::get<0>(edge) == v && std::get<1>(edge) == u)) {
                    std::get<2>(edge).bandwidth -= bandwidth;
                    break;
                }
            }
        }
    }
}

// Helper function to try mapping a single slice
bool try_map_slice(const PhysicalNetwork& physical,
                  const NetworkSlice& slice,
                  const ResourceUsage& current_usage,
                  SliceMapping& mapping) {
    // Try to map nodes first
    std::unordered_map<int, int> node_mapping;
    std::vector<bool> used_physical_nodes(physical.nodes.size(), false);
    
    for (size_t i = 0; i < slice.nodes.size(); ++i) {
        const auto& vnode = slice.nodes[i];
        bool mapped = false;
        
        for (size_t j = 0; j < physical.nodes.size(); ++j) {
            if (!used_physical_nodes[j]) {
                const auto& pnode = current_usage.remaining_nodes[j];
                if (pnode.cpu >= vnode.cpu &&
                    pnode.memory >= vnode.memory &&
                    pnode.bandwidth >= vnode.bandwidth) {
                    node_mapping[i] = j;
                    used_physical_nodes[j] = true;
                    mapped = true;
                    break;
                }
            }
        }
        
        if (!mapped) return false;
    }
    
    // Try to map edges
    std::vector<std::vector<int>> path_mapping;
    for (const auto& edge : slice.edges) {
        int v1 = std::get<0>(edge);
        int v2 = std::get<1>(edge);
        int bandwidth = std::get<2>(edge).bandwidth;
        
        int p1 = node_mapping[v1];
        int p2 = node_mapping[v2];
        
        // Find max latency requirement for this edge
        int max_latency = std::numeric_limits<int>::max();
        for (const auto& req : slice.latency_requirements) {
            if ((req.from_node == v1 && req.to_node == v2) ||
                (req.from_node == v2 && req.to_node == v1)) {
                max_latency = std::min(max_latency, req.max_latency);
            }
        }
        
        auto path = find_shortest_path(physical, current_usage, p1, p2, 
                                     bandwidth, max_latency);
        if (path.empty()) return false;
        
        path_mapping.push_back(path);
    }
    
    mapping.node_mapping = node_mapping;
    mapping.path_mapping = path_mapping;
    return true;
}

OptimizationResult optimize_network_slicing(
    const PhysicalNetwork& physical,
    const std::vector<NetworkSlice>& slices) {
    
    OptimizationResult result;
    result.revenue = 0;
    
    if (physical.nodes.empty() || slices.empty()) {
        return result;
    }
    
    // Sort slices by revenue (descending)
    std::vector<size_t> slice_indices(slices.size());
    for (size_t i = 0; i < slices.size(); ++i) {
        slice_indices[i] = i;
    }
    std::sort(slice_indices.begin(), slice_indices.end(),
              [&slices](size_t i1, size_t i2) {
                  return slices[i1].revenue > slices[i2].revenue;
              });
    
    // Initialize resource usage
    ResourceUsage usage;
    usage.remaining_nodes = physical.nodes;
    usage.remaining_edges = physical.edges;
    
    // Try to map each slice
    for (size_t idx : slice_indices) {
        const auto& slice = slices[idx];
        SliceMapping mapping;
        
        if (try_map_slice(physical, slice, usage, mapping)) {
            result.mappings.push_back(mapping);
            result.revenue += slice.revenue;
            update_resource_usage(usage, mapping, slice);
        }
    }
    
    return result;
}

} // namespace network_slicing