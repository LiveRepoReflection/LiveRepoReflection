#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <vector>

namespace distributed_tx {

struct Transfer {
    int source_node;
    int destination_node;
    int amount;
};

struct Transaction {
    std::vector<Transfer> transfers;
};

struct PartitionEvent {
    int start_time;
    int end_time;
    std::vector<int> affected_nodes;
};

struct FailureEvent {
    int time;
    int node_id;
};

std::vector<int> simulate_transactions(
    int n,
    const std::vector<int>& initial_assets,
    const std::vector<Transaction>& transactions,
    const std::vector<PartitionEvent>& partitions,
    const std::vector<FailureEvent>& failure_events,
    int timeout
);

} // namespace distributed_tx

#endif // DISTRIBUTED_TX_H