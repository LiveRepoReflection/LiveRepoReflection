#ifndef TX_ORDERING_H
#define TX_ORDERING_H

#include <vector>
#include <cstdint>

namespace tx_ordering {

struct TransactionProposal {
    uint64_t txID;
    uint8_t nodeID;
    std::vector<uint64_t> dataItems;
    uint32_t duration;
    bool readOnly;
};

std::vector<uint64_t> orderTransactions(const std::vector<TransactionProposal>& proposals);

}

#endif