#include "tx_coordinator.h"
#include <iostream>

std::string TransactionCoordinator::statusToString(TransactionStatus status) {
    switch (status) {
        case TransactionStatus::PENDING:
            return "PENDING";
        case TransactionStatus::PREPARING:
            return "PREPARING";
        case TransactionStatus::COMMITTED:
            return "COMMITTED";
        case TransactionStatus::ABORTED:
            return "ABORTED";
        default:
            return "UNKNOWN";
    }
}

bool TransactionCoordinator::validateTransaction(int transaction_id, bool should_exist) {
    bool exists = transaction_status.find(transaction_id) != transaction_status.end();
    
    if (should_exist && !exists) {
        return false;
    } else if (!should_exist && exists) {
        return false;
    }
    
    return true;
}

std::string TransactionCoordinator::createTransaction(int transaction_id) {
    // Check if transaction already exists
    if (!validateTransaction(transaction_id, false)) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " already exists";
    }
    
    // Create the transaction with PENDING status
    transaction_status[transaction_id] = TransactionStatus::PENDING;
    transaction_operations[transaction_id] = std::vector<Operation>();
    transaction_node_ops[transaction_id] = std::unordered_map<int, std::set<int>>();
    
    return "OK";
}

std::string TransactionCoordinator::registerOperation(int transaction_id, int node_id, int operation_id, int cost) {
    // Check if transaction exists
    if (!validateTransaction(transaction_id)) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " does not exist";
    }
    
    // Check if transaction is already committed
    if (transaction_status[transaction_id] == TransactionStatus::COMMITTED) {
        return "ERROR: Cannot modify committed transaction " + std::to_string(transaction_id);
    }
    
    // Check if cost is positive
    if (cost <= 0) {
        return "ERROR: Cost must be positive";
    }
    
    // Check if operation already exists for this node in this transaction
    auto& node_ops = transaction_node_ops[transaction_id];
    if (node_ops.find(node_id) != node_ops.end() &&
        node_ops[node_id].find(operation_id) != node_ops[node_id].end()) {
        return "ERROR: Operation " + std::to_string(operation_id) + " already exists for node " + 
               std::to_string(node_id) + " in transaction " + std::to_string(transaction_id);
    }
    
    // Add the operation
    transaction_operations[transaction_id].emplace_back(node_id, operation_id, cost);
    
    // Add to node operations lookup
    if (node_ops.find(node_id) == node_ops.end()) {
        node_ops[node_id] = std::set<int>();
    }
    node_ops[node_id].insert(operation_id);
    
    // Update critical node on each operation registration
    updateCriticalNode(transaction_id);
    
    return "OK";
}

void TransactionCoordinator::updateCriticalNode(int transaction_id) {
    // Calculate total cost per node
    std::unordered_map<int, int> nodeTotalCost;
    
    for (const auto& op : transaction_operations[transaction_id]) {
        nodeTotalCost[op.node_id] += op.cost;
    }
    
    // Find node with highest total cost
    int maxCost = -1;
    int criticalNode = -1;
    
    for (const auto& [node, cost] : nodeTotalCost) {
        if (cost > maxCost || (cost == maxCost && node < criticalNode)) {
            maxCost = cost;
            criticalNode = node;
        }
    }
    
    if (criticalNode != -1) {
        transaction_critical_node[transaction_id] = criticalNode;
    }
}

std::string TransactionCoordinator::executeTwoPhaseCommit(int transaction_id) {
    // Set status to PREPARING
    transaction_status[transaction_id] = TransactionStatus::PREPARING;
    
    // In a real system, we would send prepare messages to all nodes
    // and wait for responses. Since in our simplified version, all nodes
    // are assumed to always respond positively, we can skip that step.
    
    // Directly move to commit phase
    transaction_status[transaction_id] = TransactionStatus::COMMITTED;
    
    return "OK";
}

std::string TransactionCoordinator::prepareTransaction(int transaction_id) {
    // Check if transaction exists
    if (!validateTransaction(transaction_id)) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " does not exist";
    }
    
    // Check if transaction has any operations
    if (transaction_operations[transaction_id].empty()) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " has no operations";
    }
    
    // Check if transaction is already committed or aborted
    TransactionStatus status = transaction_status[transaction_id];
    if (status == TransactionStatus::COMMITTED) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " is already COMMITTED";
    } else if (status == TransactionStatus::ABORTED) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " is already ABORTED";
    } else if (status == TransactionStatus::PREPARING) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " is already being prepared";
    }
    
    // Execute two-phase commit
    return executeTwoPhaseCommit(transaction_id);
}

std::string TransactionCoordinator::getTransactionStatus(int transaction_id) {
    // Check if transaction exists
    if (!validateTransaction(transaction_id)) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " does not exist";
    }
    
    return statusToString(transaction_status[transaction_id]);
}

std::string TransactionCoordinator::getCriticalNode(int transaction_id) {
    // Check if transaction exists
    if (!validateTransaction(transaction_id)) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " does not exist";
    }
    
    // Check if transaction has any operations
    if (transaction_operations[transaction_id].empty()) {
        return "ERROR: Transaction " + std::to_string(transaction_id) + " has no operations";
    }
    
    return std::to_string(transaction_critical_node[transaction_id]);
}

std::string TransactionCoordinator::executeCommand(const std::string& command) {
    std::istringstream iss(command);
    std::string cmd;
    iss >> cmd;
    
    if (cmd == "CREATE_TRANSACTION") {
        int transaction_id;
        if (iss >> transaction_id) {
            return createTransaction(transaction_id);
        }
    } else if (cmd == "REGISTER_OPERATION") {
        int transaction_id, node_id, operation_id, cost;
        if (iss >> transaction_id >> node_id >> operation_id >> cost) {
            return registerOperation(transaction_id, node_id, operation_id, cost);
        }
    } else if (cmd == "PREPARE") {
        int transaction_id;
        if (iss >> transaction_id) {
            return prepareTransaction(transaction_id);
        }
    } else if (cmd == "GET_STATUS") {
        int transaction_id;
        if (iss >> transaction_id) {
            return getTransactionStatus(transaction_id);
        }
    } else if (cmd == "GET_CRITICAL_NODE") {
        int transaction_id;
        if (iss >> transaction_id) {
            return getCriticalNode(transaction_id);
        }
    }
    
    return "ERROR: Invalid command format: " + command;
}