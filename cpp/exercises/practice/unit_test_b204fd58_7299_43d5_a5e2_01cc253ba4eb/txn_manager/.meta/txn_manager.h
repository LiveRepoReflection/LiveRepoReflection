#ifndef TXN_MANAGER_H
#define TXN_MANAGER_H

#include <string>
#include <unordered_map>
#include <map>
#include <set>
#include <vector>
#include <mutex>
#include <shared_mutex>
#include <memory>

class TxnManager {
private:
    struct NodeData {
        std::unordered_map<std::string, int> data;
        mutable std::shared_mutex mutex;
    };

    struct Transaction {
        bool active;
        std::unordered_map<int, std::unordered_map<std::string, int>> writes;
        std::set<std::pair<int, std::string>> reads;
        std::mutex mutex;
    };

    int num_nodes;
    std::vector<std::unique_ptr<NodeData>> nodes;
    std::map<int, std::unique_ptr<Transaction>> transactions;
    std::mutex txn_mutex;

    bool validateTransaction(Transaction* txn);
    void cleanupTransaction(int tid);

public:
    explicit TxnManager(int n);
    bool begin(int tid);
    bool write(int tid, int node, const std::string& key, int value);
    int read(int tid, int node, const std::string& key);
    bool commit(int tid);
    bool rollback(int tid);
};

#endif