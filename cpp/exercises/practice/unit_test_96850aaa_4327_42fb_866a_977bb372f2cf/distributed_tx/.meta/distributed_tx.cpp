#include "distributed_tx.h"
#include <algorithm>
#include <vector>

namespace distributed_tx {

// Helper function to check if a given node is in a list.
bool node_in_list(int node, const std::vector<int>& list) {
    return std::find(list.begin(), list.end(), node) != list.end();
}

// Check connectivity between coordinator and a node at time t=0.
// A connection is disrupted if there exists a partition event active at time 0
// such that exactly one of coordinator or node is in the affected set.
bool is_connected_at_start(int coordinator, int node, const std::vector<PartitionEvent>& partitions) {
    // Only check events active at time 0.
    for (const auto& pe : partitions) {
        if (pe.start_time <= 0 && 0 < pe.end_time) {
            bool coordAffected = node_in_list(coordinator, pe.affected_nodes);
            bool nodeAffected = node_in_list(node, pe.affected_nodes);
            if (coordAffected ^ nodeAffected) {
                return false;
            }
        }
    }
    return true;
}

// Check if the coordinator has a scheduled failure within timeout.
bool coordinator_failed(int coordinator, const std::vector<FailureEvent>& failure_events, int timeout) {
    for (const auto& fe : failure_events) {
        if (fe.node_id == coordinator && fe.time <= timeout) {
            return true;
        }
    }
    return false;
}

std::vector<int> simulate_transactions(
    int n,
    const std::vector<int>& initial_assets,
    const std::vector<Transaction>& transactions,
    const std::vector<PartitionEvent>& partitions,
    const std::vector<FailureEvent>& failure_events,
    int timeout
) {
    // Copy initial assets to use as the current state.
    std::vector<int> assets = initial_assets;
    
    // Since transactions are submitted concurrently at time 0,
    // we evaluate each transaction by checking conditions across the entire network fault window.
    for (const auto& txn : transactions) {
        // Collect all involved nodes.
        std::vector<int> involved_nodes;
        for (const auto& tr : txn.transfers) {
            if (std::find(involved_nodes.begin(), involved_nodes.end(), tr.source_node) == involved_nodes.end()) {
                involved_nodes.push_back(tr.source_node);
            }
            if (std::find(involved_nodes.begin(), involved_nodes.end(), tr.destination_node) == involved_nodes.end()) {
                involved_nodes.push_back(tr.destination_node);
            }
        }

        if (involved_nodes.empty()) {
            // Nothing to do.
            continue;
        }
        
        // Determine the coordinator as the smallest node id among involved nodes.
        int coordinator = *std::min_element(involved_nodes.begin(), involved_nodes.end());
        bool abort_txn = false;
        
        // Check connectivity for each involved node relative to the coordinator.
        for (int node : involved_nodes) {
            if (!is_connected_at_start(coordinator, node, partitions)) {
                abort_txn = true;
                break;
            }
        }
        
        // Check coordinator failure event.
        if (!abort_txn && coordinator_failed(coordinator, failure_events, timeout)) {
            abort_txn = true;
        }
        
        // Check if all source nodes have sufficient funds.
        // Aggregate the total required amount per source node for this transaction.
        if (!abort_txn) {
            std::vector<int> required(n, 0);
            for (const auto& tr : txn.transfers) {
                required[tr.source_node] += tr.amount;
            }
            for (int i = 0; i < n; ++i) {
                if (required[i] > assets[i]) {
                    abort_txn = true;
                    break;
                }
            }
        }
        
        // If not aborted, commit the transaction atomically.
        if (!abort_txn) {
            // Deduct amounts from source nodes.
            for (const auto& tr : txn.transfers) {
                assets[tr.source_node] -= tr.amount;
            }
            // Add amounts to destination nodes.
            for (const auto& tr : txn.transfers) {
                assets[tr.destination_node] += tr.amount;
            }
        }
    }
    
    return assets;
}

} // namespace distributed_tx