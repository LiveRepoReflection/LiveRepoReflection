#include "tx_coordinator.h"
#include <algorithm>
#include <thread>

using namespace std;

bool TransactionCoordinator::BeginTransaction(vector<Service*> services) {
    // Verify all services are registered
    for (auto service : services) {
        if (!IsServiceRegistered(service)) {
            throw runtime_error("Attempted to use unregistered service");
        }
    }

    // Prepare phase
    if (!PreparePhase(services)) {
        RollbackPhase(services);
        return false;
    }

    // Commit phase
    if (!CommitPhase(services)) {
        RollbackPhase(services);
        return false;
    }

    return true;
}

void TransactionCoordinator::RegisterService(Service* service) {
    lock_guard<mutex> lock(services_mutex);
    registered_services.insert(service);
}

void TransactionCoordinator::UnregisterService(Service* service) {
    lock_guard<mutex> lock(services_mutex);
    registered_services.erase(service);
}

bool TransactionCoordinator::PreparePhase(const vector<Service*>& services) {
    vector<thread> threads;
    atomic<bool> all_prepared(true);

    for (auto service : services) {
        threads.emplace_back([service, &all_prepared]() {
            if (!service->Prepare()) {
                all_prepared = false;
            }
        });
    }

    for (auto& t : threads) {
        t.join();
    }

    return all_prepared;
}

bool TransactionCoordinator::CommitPhase(const vector<Service*>& services) {
    vector<thread> threads;
    atomic<bool> all_committed(true);

    for (auto service : services) {
        threads.emplace_back([service, &all_committed]() {
            if (!service->Commit()) {
                all_committed = false;
            }
        });
    }

    for (auto& t : threads) {
        t.join();
    }

    return all_committed;
}

void TransactionCoordinator::RollbackPhase(const vector<Service*>& services) {
    vector<thread> threads;

    for (auto service : services) {
        threads.emplace_back([service]() {
            service->Rollback();
        });
    }

    for (auto& t : threads) {
        t.join();
    }
}

bool TransactionCoordinator::IsServiceRegistered(Service* service) {
    lock_guard<mutex> lock(services_mutex);
    return registered_services.find(service) != registered_services.end();
}