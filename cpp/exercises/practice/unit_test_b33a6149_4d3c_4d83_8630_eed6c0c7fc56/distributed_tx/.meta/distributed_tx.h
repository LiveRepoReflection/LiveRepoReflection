#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <functional>
#include <cstdint>

namespace distributed_tx {

using TransactionID = int64_t;

TransactionID beginTransaction();
bool registerOperation(TransactionID txID, std::function<bool()> commit, std::function<void()> rollback);
bool commitTransaction(TransactionID txID);
void abortTransaction(TransactionID txID);

}  // namespace distributed_tx

#endif