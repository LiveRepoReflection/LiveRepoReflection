#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <chrono>
#include <functional>
#include <memory>
#include <vector>

namespace distributed_tx {

class TransactionCoordinator {
public:
    TransactionCoordinator();
    
    // Set the maximum number of retries for the commit phase
    void set_commit_max_retries(int max_retries);
    
    // Set the timeout for the prepare phase
    void set_prepare_timeout(std::chrono::seconds timeout);
    
    // Begin a transaction with the given list of services
    template <typename Service>
    void begin_transaction(const std::vector<std::shared_ptr<Service>>& services);
    
    // Execute the transaction
    bool execute_transaction();

private:
    // Implementation details to be defined
};

} // namespace distributed_tx

#endif // DISTRIBUTED_TX_H