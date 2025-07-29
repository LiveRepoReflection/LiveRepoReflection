#ifndef TRANSACTION_ORCHESTRATOR_H
#define TRANSACTION_ORCHESTRATOR_H

#include <vector>
#include <mutex>

// Abstract service interface to be implemented by concrete services.
class ServiceInterface {
public:
    virtual ~ServiceInterface() {}
    virtual bool prepare() = 0;
    virtual void commit() = 0;
    virtual void abort() = 0;
};

// TransactionOrchestrator implements a simplified two-phase commit protocol for distributed transactions.
class TransactionOrchestrator {
public:
    // Constructor
    // services: vector of pointers to ServiceInterface instances participating in the transaction.
    // timeout_ms: timeout in milliseconds for the prepare phase.
    TransactionOrchestrator(const std::vector<ServiceInterface*>& services, int timeout_ms);

    // runTransaction executes the two-phase commit:
    // 1. Prepare phase: concurrently calls prepare() on each service.
    // 2. If all services are ready within timeout, transitions to commit phase.
    // 3. Otherwise, performs abort on all services.
    // Returns true if transaction committed, false otherwise.
    bool runTransaction();

    // finalizeTransaction allows idempotent re-finalization of the transaction.
    // Useful in cases where commit messages need to be retried.
    void finalizeTransaction();

private:
    std::vector<ServiceInterface*> services_;
    int timeout_ms_;
    bool committed_;
    bool finalized_;
    std::mutex mtx_;
};

#endif // TRANSACTION_ORCHESTRATOR_H