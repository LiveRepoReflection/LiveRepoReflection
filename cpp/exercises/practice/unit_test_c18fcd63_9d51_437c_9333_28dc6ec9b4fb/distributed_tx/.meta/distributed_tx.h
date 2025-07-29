#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <string>

namespace distributed_tx {

struct Transaction {
    int transaction_id;
    int user_id;
    int item_id;
    int quantity;
    int price;
    std::string payment_details;
    bool simulate_failure;
    bool simulate_timeout;
    bool simulate_partial_failure;
};

bool process_transaction(Transaction& txn);

}  // namespace distributed_tx

#endif  // DISTRIBUTED_TX_H