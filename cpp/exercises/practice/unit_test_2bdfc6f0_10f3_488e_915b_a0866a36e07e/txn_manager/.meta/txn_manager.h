#pragma once

#include <map>
#include <vector>
#include <mutex>
#include <atomic>
#include <memory>

namespace txn_manager {

using PrepareFunction = bool (*)();
using CommitFunction = bool (*)();
using RollbackFunction = bool (*)();

class Resource {
public:
    Resource(int id, PrepareFunction pf, CommitFunction cf, RollbackFunction rf)
        : resource_id(id), prepare_fn(pf), commit_fn(cf), rollback_fn(rf) {}

    int resource_id;
    PrepareFunction prepare_fn;
    CommitFunction commit_fn;
    RollbackFunction rollback_fn;
};

class Transaction {
public:
    explicit Transaction(int id) : transaction_id(id) {}
    std::vector<Resource> resources;
    int transaction_id;
    std::mutex transaction_mutex;
};

class DistributedTransactionManager {
public:
    DistributedTransactionManager();
    int begin_transaction();
    bool enlist_resource(int tid, int resource_id, PrepareFunction prepare_fn,
                        CommitFunction commit_fn, RollbackFunction rollback_fn);
    bool commit_transaction(int tid);
    bool rollback_transaction(int tid);

private:
    std::map<int, std::shared_ptr<Transaction>> transactions;
    std::mutex transactions_mutex;
    std::atomic<int> next_transaction_id;

    std::shared_ptr<Transaction> get_transaction(int tid);
    bool execute_prepare_phase(Transaction& transaction);
    bool execute_commit_phase(Transaction& transaction);
    bool execute_rollback_phase(Transaction& transaction);
};

}  // namespace txn_manager