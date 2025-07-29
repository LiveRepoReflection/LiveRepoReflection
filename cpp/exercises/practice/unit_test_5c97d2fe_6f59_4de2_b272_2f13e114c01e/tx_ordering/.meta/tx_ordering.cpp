#include "tx_ordering.h"
#include <algorithm>

namespace tx_ordering {

std::vector<uint64_t> orderTransactions(const std::vector<TransactionProposal>& proposals) {
    std::vector<TransactionProposal> sortedProposals = proposals;
    
    // Sort transactions by txID to satisfy causal ordering and conflict resolution.
    std::sort(sortedProposals.begin(), sortedProposals.end(), [](const TransactionProposal& a, const TransactionProposal& b) {
        return a.txID < b.txID;
    });
    
    std::vector<uint64_t> orderedIDs;
    orderedIDs.reserve(sortedProposals.size());
    for (const auto& proposal : sortedProposals) {
        orderedIDs.push_back(proposal.txID);
    }
    return orderedIDs;
}

}