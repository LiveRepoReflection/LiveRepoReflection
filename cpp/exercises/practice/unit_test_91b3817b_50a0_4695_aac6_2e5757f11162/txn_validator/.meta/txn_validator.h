#ifndef TXN_VALIDATOR_H
#define TXN_VALIDATOR_H

#include <vector>
#include <string>
#include <optional>
#include <unordered_map>

// Represents an operation in the transaction graph
struct Operation {
    int node_id;                // ID of the node executing the operation
    int resource_id;            // Resource being accessed
    int read_version;           // Expected version for reading
    std::optional<int> write_version; // New version if writing (nullopt if read-only)
};

// Represents a dependency between operations
struct Dependency {
    int source_node_id;         // Source operation
    int destination_node_id;    // Operation dependent on source
};

// Represents the transaction graph
struct TransactionGraph {
    std::vector<Operation> operations;       // List of operations
    std::vector<Dependency> dependencies;    // List of dependencies between operations
};

// Represents a log entry from a node
struct LogEntry {
    int node_id;                // ID of the node that executed the operation
    int resource_id;            // Resource accessed
    int version_at_execution;   // Actual version seen during execution
};

// Function to validate the transaction
std::string validateTransaction(
    int num_resources,
    const TransactionGraph& transaction_graph,
    const std::unordered_map<int, std::vector<LogEntry>>& node_logs
);

#endif // TXN_VALIDATOR_H