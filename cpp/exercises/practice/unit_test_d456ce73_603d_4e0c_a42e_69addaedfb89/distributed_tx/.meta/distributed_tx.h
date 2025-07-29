#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include <vector>
#include <future>
#include <mutex>
#include <atomic>
#include <iostream>
#include <random>

namespace distributed_tx {

// Interface for Service operations
template <typename Service>
class ServiceOperations {
public:
    virtual bool prepare(Service& service) = 0;
    virtual void commit(Service& service) = 0;
    virtual void rollback(Service& service) = 0;
    virtual ~ServiceOperations() = default;
};

// Default implementation of ServiceOperations
template <typename Service>
class DefaultServiceOperations : public ServiceOperations<Service> {
public:
    bool prepare(Service& service) override {
        return service.prepare();
    }

    void commit(Service& service) override {
        service.commit();
    }

    void rollback(Service& service) override {
        service.rollback();
    }
};

class TransactionCoordinator {
public:
    TransactionCoordinator();
    
    // Set the maximum number of retries for the commit phase
    void set_commit_max_retries(int max_retries);
    
    // Set the timeout for the prepare phase
    void set_prepare_timeout(std::chrono::seconds timeout);
    
    // Begin a transaction with the given list of services
    template <typename Service>
    void begin_transaction(const std::vector<std::shared_ptr<Service>>& services) {
        services_.clear();
        for (const auto& service : services) {
            services_.push_back([service]() -> bool {
                return service->prepare();
            });
            
            commits_.push_back([service]() {
                service->commit();
            });
            
            rollbacks_.push_back([service]() {
                service->rollback();
            });
            
            service_names_.push_back(typeid(Service).name());
        }
    }
    
    // Execute the transaction
    bool execute_transaction();

private:
    // Type-erased function wrappers for service operations
    std::vector<std::function<bool()>> services_;
    std::vector<std::function<void()>> commits_;
    std::vector<std::function<void()>> rollbacks_;
    std::vector<std::string> service_names_;
    
    int commit_max_retries_;
    std::chrono::seconds prepare_timeout_;
    
    // Internal methods
    bool prepare_phase();
    bool commit_phase();
    void rollback_all();
    
    // Helper for exponential backoff
    void exponential_backoff(int attempt);
    
    // Logging helper
    void log(const std::string& message);
    
    // Thread-safe logging
    std::mutex log_mutex_;
};

} // namespace distributed_tx

#endif // DISTRIBUTED_TX_H