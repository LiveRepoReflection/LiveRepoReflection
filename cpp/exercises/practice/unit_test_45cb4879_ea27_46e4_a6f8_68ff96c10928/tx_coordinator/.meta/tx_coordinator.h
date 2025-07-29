#ifndef TX_COORDINATOR_H
#define TX_COORDINATOR_H

#include "service.h"
#include <vector>
#include <unordered_set>
#include <mutex>
#include <condition_variable>
#include <chrono>

class TransactionCoordinator {
public:
    bool BeginTransaction(std::vector<Service*> services);
    void RegisterService(Service* service);
    void UnregisterService(Service* service);

private:
    std::unordered_set<Service*> registered_services;
    std::mutex services_mutex;
    std::condition_variable cv;
    const std::chrono::milliseconds timeout{5000};

    bool PreparePhase(const std::vector<Service*>& services);
    bool CommitPhase(const std::vector<Service*>& services);
    void RollbackPhase(const std::vector<Service*>& services);
    bool IsServiceRegistered(Service* service);
};

#endif