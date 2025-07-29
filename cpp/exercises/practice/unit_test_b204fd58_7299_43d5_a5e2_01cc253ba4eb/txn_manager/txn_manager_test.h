#if !defined(TXN_MANAGER_TEST_H)
#define TXN_MANAGER_TEST_H

#include <string>

class TxnManager {
public:
    TxnManager(int num_nodes);
    bool begin(int tid);
    bool write(int tid, int node, const std::string& key, int value);
    int read(int tid, int node, const std::string& key);
    bool commit(int tid);
    bool rollback(int tid);
};

#endif