#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <vector>
#include <string>

namespace distributed_tx {

enum class TxStatus {
    COMMITTED,
    ROLLED_BACK
};

struct PerformanceMetrics {
    double completion_time;
    int throughput;
    std::vector<int> resource_utilization;
};

struct Operation {
    int serviceId;
    std::string description;
    bool succeed;
};

struct TransactionRequest {
    std::vector<Operation> operations;
};

struct TransactionResult {
    TxStatus status;
    PerformanceMetrics metrics;
};

struct Microservice {
    int id;
    int cpu;
    int memory;
    int network;
    int latency;
};

class DistributedTxCoordinator {
public:
    DistributedTxCoordinator();
    void addMicroservice(const Microservice& microservice);
    TransactionResult executeTransaction(const TransactionRequest& request);
    bool recover();
private:
    std::vector<Microservice> microservices;
};

} // namespace distributed_tx

#endif // DISTRIBUTED_TX_H