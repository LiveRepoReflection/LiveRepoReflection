#include "distributed_tx.h"
#include <algorithm>
#include <chrono>
#include <thread>
#include <numeric>

namespace distributed_tx {

DistributedTxCoordinator::DistributedTxCoordinator() {
    // Initialization if necessary.
}

void DistributedTxCoordinator::addMicroservice(const Microservice& microservice) {
    microservices.push_back(microservice);
}

TransactionResult DistributedTxCoordinator::executeTransaction(const TransactionRequest& request) {
    using namespace std::chrono;
    auto start = high_resolution_clock::now();

    TransactionResult result;
    bool commit = true;
    
    // Scheduling: sort operations by the latency of the target microservice (lower latency first)
    std::vector<Operation> sortedOps = request.operations;
    std::sort(sortedOps.begin(), sortedOps.end(), [this](const Operation &a, const Operation &b) {
        int latA = 1000, latB = 1000;
        for(const auto &ms : microservices) {
            if(ms.id == a.serviceId) { latA = ms.latency; break; }
        }
        for(const auto &ms : microservices) {
            if(ms.id == b.serviceId) { latB = ms.latency; break; }
        }
        return latA < latB;
    });

    // Two-phase commit simulation: prepare phase.
    for(const auto& op : sortedOps) {
        int latency = 50; // default latency
        for(const auto &ms : microservices) {
            if(ms.id == op.serviceId) {
                latency = ms.latency;
                break;
            }
        }
        std::this_thread::sleep_for(milliseconds(latency));
        if(!op.succeed) {
            commit = false;
            break;
        }
    }

    // If any prepare failed, rollback the transaction.
    if(!commit) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        result.status = TxStatus::ROLLED_BACK;
    } else {
        // Commit phase: simulate commit delay for each operation.
        for(const auto& op : sortedOps) {
            int latency = 50;
            for(const auto &ms : microservices) {
                if(ms.id == op.serviceId) {
                    latency = ms.latency;
                    break;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(latency));
        }
        result.status = TxStatus::COMMITTED;
    }
    
    auto end = high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;
    
    // Fill performance metrics.
    result.metrics.completion_time = diff.count();
    int opCount = static_cast<int>(sortedOps.size());
    result.metrics.throughput = static_cast<int>(opCount / (diff.count() > 0 ? diff.count() : 1));
    
    // Aggregate resource utilization for microservices involved in the transaction.
    std::vector<int> usage;
    for(const auto &op : sortedOps) {
        for(const auto &ms : microservices) {
            if(ms.id == op.serviceId) {
                usage.push_back(ms.cpu);
                break;
            }
        }
    }
    result.metrics.resource_utilization = usage;
    
    return result;
}

bool DistributedTxCoordinator::recover() {
    // Simulate recovery delay.
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    // In a realistic scenario, logs would be read and the state restored.
    // For this simulation, we simply return true.
    return true;
}

} // namespace distributed_tx