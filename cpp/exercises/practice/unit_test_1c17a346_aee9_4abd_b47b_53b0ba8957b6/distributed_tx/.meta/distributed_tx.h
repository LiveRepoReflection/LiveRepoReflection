#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <string>
#include <vector>
#include <map>

namespace distributed_tx {

struct TransactionRequest {
    std::string tid;
    std::vector<std::string> services;
    std::map<std::string, std::string> serviceData;
};

struct TransactionResponse {
    std::string tid;
    std::string status; // "Commit", "Rollback", "Pending"
    std::string errorMessage;
};

TransactionResponse process_transaction(const TransactionRequest& req);
void recover_incomplete_transactions();
TransactionResponse query_transaction_status(const std::string& tid);

} // namespace distributed_tx

#endif // DISTRIBUTED_TX_H