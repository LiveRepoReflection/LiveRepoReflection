#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <string>
#include <vector>

struct Transaction {
    int txid;
    std::vector<std::string> services;
    std::string account_from;
    std::string account_to;
    double amount;
    int timeout_ms;
};

class TransactionManager {
public:
    bool executeTransaction(const Transaction& tx);
};

#endif // DISTRIBUTED_TX_H