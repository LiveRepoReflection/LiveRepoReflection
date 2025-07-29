#ifndef TRANSACTION_VALIDATION_H
#define TRANSACTION_VALIDATION_H

#include <vector>
#include <string>

namespace transaction_validation {

bool validate_transactions(int num_shards, const std::vector<std::vector<std::string>>& shard_logs,
                           const std::vector<std::vector<std::string>>& global_transactions);

}  // namespace transaction_validation

#endif