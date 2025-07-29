#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <vector>
#include <string>

namespace distributed_tx {

bool process_transaction(const std::vector<std::string>& services, const std::string& user_action);
int recover_transactions();

}

#endif  // DISTRIBUTED_TX_H