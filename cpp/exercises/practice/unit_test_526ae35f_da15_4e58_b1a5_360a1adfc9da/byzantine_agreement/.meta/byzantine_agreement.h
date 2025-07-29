#ifndef BYZANTINE_AGREEMENT_H
#define BYZANTINE_AGREEMENT_H

#include <set>

namespace byzantine_agreement {

int simulate_byzantine_agreement(int num_nodes, const std::set<int>& faulty_nodes, int leader_id, int proposed_value);

}

#endif  // BYZANTINE_AGREEMENT_H