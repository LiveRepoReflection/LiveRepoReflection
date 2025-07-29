#ifndef TRANSACTION_COORDINATOR_H_
#define TRANSACTION_COORDINATOR_H_

#include <set>
#include <map>
#include <mutex>

namespace transaction_coordinator {

enum class TransactionStatus {
    ONGOING,
    COMMITTED,
    ABORTED
};

struct Transaction {
    int id;
    std::set<int> participants;
    std::map<int, bool> votes;
    TransactionStatus status;
};

class TransactionCoordinator {
public:
    TransactionCoordinator();
    void processBeginTransaction(int transaction_id, const std::set<int>& participants);
    void processVoteRequest(int transaction_id, int node_id, bool commitVote);
    void processCoordinatorTimeout(int transaction_id);
private:
    std::mutex mtx;
    std::map<int, Transaction> transactions;
};

} // namespace transaction_coordinator

#endif // TRANSACTION_COORDINATOR_H_