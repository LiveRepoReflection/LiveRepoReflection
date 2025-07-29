#ifndef TX_COORDINATOR_H
#define TX_COORDINATOR_H

#include <string>
#include <unordered_map>
#include <map>
#include <set>
#include <vector>
#include <limits>
#include <sstream>
#include <algorithm>

// Transaction status enum
enum class TransactionStatus {
    PENDING,
    PREPARING,
    COMMITTED,
    ABORTED
};

// Structure to hold operation information
struct Operation {
    int node_id;
    int operation_id;
    int cost;

    Operation(int n, int op, int c) : node_id(n), operation_id(op), cost(c) {}
};

// Class to represent the transaction coordinator
class TransactionCoordinator {
private:
    // Map of transaction ID to its status
    std::unordered_map<int, TransactionStatus> transaction_status;
    
    // Map of transaction ID to all operations
    std::unordered_map<int, std::vector<Operation>> transaction_operations;
    
    // Map of transaction ID to map of node ID to set of operation IDs (for quick lookup)
    std::unordered_map<int, std::unordered_map<int, std::set<int>>> transaction_node_ops;
    
    // Map of transaction ID to critical node
    std::unordered_map<int, int> transaction_critical_node;

    // Returns string representation of transaction status
    std::string statusToString(TransactionStatus status);
    
    // Calculate and cache the critical node for a transaction
    void updateCriticalNode(int transaction_id);
    
    // Execute the two-phase commit protocol
    std::string executeTwoPhaseCommit(int transaction_id);

    // Parse command string and execute the corresponding action
    bool validateTransaction(int transaction_id, bool should_exist = true);

public:
    // Create a new transaction
    std::string createTransaction(int transaction_id);
    
    // Register an operation with a transaction
    std::string registerOperation(int transaction_id, int node_id, int operation_id, int cost);
    
    // Prepare a transaction for commit (initiates two-phase commit)
    std::string prepareTransaction(int transaction_id);
    
    // Get the status of a transaction
    std::string getTransactionStatus(int transaction_id);
    
    // Get the critical node for a transaction
    std::string getCriticalNode(int transaction_id);
    
    // Process a command string
    std::string executeCommand(const std::string& command);
};

#endif // TX_COORDINATOR_H