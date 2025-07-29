#ifndef TRANSACTION_COORDINATOR_H
#define TRANSACTION_COORDINATOR_H

#include <vector>

namespace transaction_coordinator {

bool coordinate_transaction(int N, const std::vector<bool>& prepare_results, const std::vector<double>& commit_success_probabilities);

} // namespace transaction_coordinator

#endif // TRANSACTION_COORDINATOR_H