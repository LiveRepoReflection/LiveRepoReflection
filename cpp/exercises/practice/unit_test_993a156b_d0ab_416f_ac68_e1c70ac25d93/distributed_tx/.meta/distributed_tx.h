#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <vector>
#include <string>
#include <chrono>

namespace distributed_tx {

struct Operation {
    int shard_id;
    std::string operation_type;
    std::string key;
    std::string value;
};

enum class Vote { Commit, Abort, Timeout };

class Shard {
public:
    Shard();
    Shard(int id);
    Vote prepare(int transaction_id, const Operation& op, std::chrono::milliseconds timeout);
    void commit(int transaction_id);
    void rollback(int transaction_id);
    bool recover(int transaction_id);
    int getId() const;
private:
    int id_;
    int last_transaction_id_;
    Vote last_vote_;
};

class TransactionCoordinator {
public:
    TransactionCoordinator();
    bool submitTransaction(const std::vector<Operation>& ops, std::chrono::milliseconds timeout = std::chrono::milliseconds(5000));
    bool submitTransactionWithCrash(const std::vector<Operation>& ops, std::chrono::milliseconds timeout = std::chrono::milliseconds(5000));
    bool recoverTransaction();
private:
    int next_transaction_id_;
    struct PendingTransaction {
        int id;
        std::vector<int> shard_ids;
        bool all_commit;
    };
    std::vector<PendingTransaction> pending_transactions_;
    std::vector<Shard> shards_;
    Shard* getShard(int shard_id);
};

} // namespace distributed_tx

#endif