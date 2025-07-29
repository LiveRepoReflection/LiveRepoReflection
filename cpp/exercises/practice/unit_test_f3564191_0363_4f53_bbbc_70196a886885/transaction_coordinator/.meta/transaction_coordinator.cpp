#include "transaction_coordinator.h"
#include <cstdlib>

namespace transaction_coordinator {

bool coordinate_transaction(int N, const std::vector<bool>& prepare_results, const std::vector<double>& commit_success_probabilities) {
    // Check for valid input size.
    if (N <= 0 || prepare_results.size() != static_cast<std::size_t>(N)) {
        return false;
    }
    
    // Prepare Phase: If any service fails during the prepare phase, abort immediately.
    for (std::size_t i = 0; i < prepare_results.size(); ++i) {
        if (!prepare_results[i]) {
            return false;
        }
    }

    // The commit phase requires exactly N commit probability values.
    if (commit_success_probabilities.size() != static_cast<std::size_t>(N)) {
        return false;
    }

    // Validate probabilities are in range [0.0, 1.0]
    for (std::size_t i = 0; i < commit_success_probabilities.size(); ++i) {
        if (commit_success_probabilities[i] < 0.0 || commit_success_probabilities[i] > 1.0) {
            return false;
        }
    }

    // Commit Phase: For each service, simulate a commit using its success probability.
    // A random value in [0,1) is generated. If the value is greater than or equal to the probability,
    // the commit is considered to have failed.
    for (std::size_t i = 0; i < static_cast<std::size_t>(N); ++i) {
        double random_value = static_cast<double>(std::rand()) / (static_cast<double>(RAND_MAX) + 1.0);
        if (random_value >= commit_success_probabilities[i]) {
            return false;
        }
    }
    
    // If all services successfully commit, the transaction as a whole is considered committed.
    return true;
}

} // namespace transaction_coordinator