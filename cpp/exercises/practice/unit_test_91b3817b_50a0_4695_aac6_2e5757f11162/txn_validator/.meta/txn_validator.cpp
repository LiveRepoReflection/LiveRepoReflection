#include "txn_validator.h"
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <vector>
#include <algorithm>
#include <chrono>

std::string validateTransaction(
    int num_resources,
    const TransactionGraph& transaction_graph,
    const std::unordered_map<int, std::vector<LogEntry>>& node_logs
) {
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Check for cycles in the transaction graph - if present, abort
    std::unordered_map<int, std::vector<int>> adj_list;
    std::unordered_map<int, int> in_degree;
    
    // Initialize adjacency list and in-degree map
    for (const auto& op : transaction_graph.operations) {
        adj_list[op.node_id] = {};
        in_degree[op.node_id] = 0;
    }
    
    // Build the adjacency list and in-degree map
    for (const auto& dep : transaction_graph.dependencies) {
        adj_list[dep.source_node_id].push_back(dep.destination_node_id);
        in_degree[dep.destination_node_id]++;
    }
    
    // Topological sort to detect cycles
    std::queue<int> q;
    std::unordered_set<int> visited_nodes;
    
    // Add all nodes with in-degree 0 to the queue
    for (const auto& [node_id, degree] : in_degree) {
        if (degree == 0) {
            q.push(node_id);
        }
    }
    
    // Perform topological sort
    while (!q.empty()) {
        int current = q.front();
        q.pop();
        visited_nodes.insert(current);
        
        for (int neighbor : adj_list[current]) {
            in_degree[neighbor]--;
            if (in_degree[neighbor] == 0) {
                q.push(neighbor);
            }
        }
        
        // Check if we're exceeding time limit
        auto current_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - start_time).count();
        if (duration > 950) { // Leave 50ms buffer
            return "ABORT"; // Time exceeded
        }
    }
    
    // If not all nodes were visited, there's a cycle
    if (visited_nodes.size() != transaction_graph.operations.size()) {
        return "ABORT";
    }
    
    // Check completeness: all operations should be in the logs
    std::unordered_set<int> executed_nodes;
    for (const auto& [node_id, logs] : node_logs) {
        for (const auto& log : logs) {
            executed_nodes.insert(log.node_id);
        }
    }
    
    if (executed_nodes.size() != transaction_graph.operations.size()) {
        return "ABORT";
    }
    
    // Build a map for quick lookup of operations by node_id
    std::unordered_map<int, Operation> operations_by_node;
    for (const auto& op : transaction_graph.operations) {
        operations_by_node[op.node_id] = op;
    }
    
    // Check version consistency
    for (const auto& [node_id, logs] : node_logs) {
        for (const auto& log : logs) {
            const auto& operation = operations_by_node[log.node_id];
            
            // Check if the read version matches what was expected
            if (operation.read_version != log.version_at_execution) {
                return "ABORT";
            }
        }
    }
    
    // Check dependency order and version continuity
    // For each dependency, verify that dependent operations saw the correct resource versions
    std::unordered_map<int, std::unordered_map<int, int>> node_execution_order;
    
    // Build the execution order map
    for (const auto& [node_id, logs] : node_logs) {
        for (size_t i = 0; i < logs.size(); ++i) {
            const auto& log = logs[i];
            node_execution_order[node_id][log.node_id] = i;
        }
    }
    
    // Track the latest version of each resource by node
    std::unordered_map<int, std::unordered_map<int, int>> latest_resource_version;
    
    // Initialize with default versions
    for (int i = 0; i < num_resources; ++i) {
        for (const auto& [node_id, _] : node_logs) {
            latest_resource_version[node_id][i] = -1; // Start with an invalid version
        }
    }
    
    // Now process the logs in execution order for each node
    for (const auto& [node_id, logs] : node_logs) {
        std::vector<std::pair<int, LogEntry>> ordered_logs;
        for (size_t i = 0; i < logs.size(); ++i) {
            ordered_logs.push_back({i, logs[i]});
        }
        
        // Sort by execution order
        std::sort(ordered_logs.begin(), ordered_logs.end(), 
                 [](const auto& a, const auto& b) { return a.first < b.first; });
        
        for (const auto& [_, log] : ordered_logs) {
            const auto& operation = operations_by_node[log.node_id];
            
            // If this is a write operation, update the latest version
            if (operation.write_version.has_value()) {
                latest_resource_version[node_id][operation.resource_id] = operation.write_version.value();
            } else {
                // For read-only, just track the version seen
                latest_resource_version[node_id][operation.resource_id] = 
                    std::max(latest_resource_version[node_id][operation.resource_id], log.version_at_execution);
            }
        }
    }
    
    // Now validate dependencies and resource version consistency
    for (const auto& dep : transaction_graph.dependencies) {
        // Find the nodes where these operations were executed
        int source_node_id = -1;
        int dest_node_id = -1;
        
        for (const auto& [node_id, logs] : node_logs) {
            for (const auto& log : logs) {
                if (log.node_id == dep.source_node_id) {
                    source_node_id = node_id;
                }
                if (log.node_id == dep.destination_node_id) {
                    dest_node_id = node_id;
                }
            }
        }
        
        // If either operation wasn't found in logs, abort
        if (source_node_id == -1 || dest_node_id == -1) {
            return "ABORT";
        }
        
        // If on the same node, check execution order
        if (source_node_id == dest_node_id) {
            if (node_execution_order[source_node_id][dep.source_node_id] >= 
                node_execution_order[source_node_id][dep.destination_node_id]) {
                return "ABORT"; // Dependency violation
            }
        }
        
        // If source writes to a resource that destination reads, check consistency
        const auto& source_op = operations_by_node[dep.source_node_id];
        const auto& dest_op = operations_by_node[dep.destination_node_id];
        
        if (source_op.write_version.has_value() && source_op.resource_id == dest_op.resource_id) {
            // The destination should see at least the version written by the source
            for (const auto& log : node_logs.at(dest_node_id)) {
                if (log.node_id == dep.destination_node_id && 
                    log.resource_id == source_op.resource_id && 
                    log.version_at_execution < source_op.write_version.value()) {
                    return "ABORT"; // Dependency version inconsistency
                }
            }
        }
    }
    
    // All checks passed, commit the transaction
    return "COMMIT";
}