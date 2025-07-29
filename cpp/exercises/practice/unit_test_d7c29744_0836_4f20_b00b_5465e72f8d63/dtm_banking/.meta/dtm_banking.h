#ifndef DTM_BANKING_H
#define DTM_BANKING_H

#include <string>
#include <vector>

namespace dtm_banking {

struct Operation {
    std::string server_id;
    std::string account_id;
    std::string operation;
    int amount;
};

std::string processTransaction(const std::vector<Operation>& ops);
void recoverTransactions();

} // namespace dtm_banking

#endif // DTM_BANKING_H