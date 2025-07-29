#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <iostream>
#include <istream>
#include <ostream>

namespace distributed_tx {

void processTransactions(std::istream &in, std::ostream &out);

} // namespace distributed_tx

#endif // DISTRIBUTED_TX_H