#ifndef TX_COORDINATOR_H
#define TX_COORDINATOR_H

#include <string>
#include <vector>

namespace tx_coordinator {

struct TransactionResult {
    std::string transactionId;
    std::string status; // "committed", "rolled_back", or "failed"
    std::vector<std::string> errors;
};

void setMockResponse(const std::string &url, const std::string &phase, const std::string &response, int delay_ms = 0);
void clearMockResponses();
TransactionResult processTransaction(const std::vector<std::string> &prepareUrls, int timeout_ms);
void recoverPendingTransactions();
void resetCoordinator();

} // namespace tx_coordinator

#endif // TX_COORDINATOR_H