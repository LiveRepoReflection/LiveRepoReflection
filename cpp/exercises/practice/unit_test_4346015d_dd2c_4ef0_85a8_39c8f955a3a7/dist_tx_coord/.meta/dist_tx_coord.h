#ifndef DIST_TX_COORD_H
#define DIST_TX_COORD_H

#include <string>
#include <vector>

namespace dist_tx_coord {

enum class TxResult { COMMIT, ROLLBACK, TIMEOUT };

struct Operation {
    enum Type { READ, WRITE };
    std::string node_id;
    std::string key;
    std::string value;
    Type op_type;
};

struct Transaction {
    std::string id;
    std::vector<Operation> operations;
};

class TransactionCoordinator {
public:
    TxResult processTransaction(const Transaction& tx);
};

} // namespace dist_tx_coord

#endif // DIST_TX_COORD_H