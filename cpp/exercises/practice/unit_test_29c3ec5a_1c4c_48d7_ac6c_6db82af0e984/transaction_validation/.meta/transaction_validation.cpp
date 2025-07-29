#include "transaction_validation.h"
#include <vector>
#include <string>
#include <unordered_map>
#include <sstream>
#include <cstdlib>
#include <algorithm>

using namespace std;

namespace transaction_validation {

bool validate_transactions(int num_shards, const vector<vector<string>>& shard_logs,
                           const vector<vector<string>>& global_transactions) {
    // Build a mapping for each shard: transaction id -> index in the shard log.
    vector<unordered_map<string, int>> shard_map(num_shards);
    for (int s = 0; s < num_shards; s++) {
        // Populate the mapping for shard s.
        for (int idx = 0; idx < static_cast<int>(shard_logs[s].size()); idx++) {
            shard_map[s][shard_logs[s][idx]] = idx;
        }
    }

    // For each shard, record a vector of (global transaction order, index in shard log)
    vector<vector<pair<int, int>>> shard_entries(num_shards);

    // Process each global transaction according to its initiation order.
    // Global transactions are expected in the input order, i.e. index 0 is earliest.
    for (int g = 0; g < static_cast<int>(global_transactions.size()); g++) {
        const auto& global_tx = global_transactions[g];
        // Track usage per shard within the same global transaction to avoid duplicate references.
        vector<bool> used_in_shard(num_shards, false);
        for (const string& entry : global_tx) {
            size_t colon_pos = entry.find(':');
            if (colon_pos == string::npos) return false; // Malformed entry.
            string shard_id_str = entry.substr(0, colon_pos);
            string txn_id = entry.substr(colon_pos + 1);
            int shard_id = std::atoi(shard_id_str.c_str());
            if (shard_id < 0 || shard_id >= num_shards) return false; // Invalid shard id.
            if (used_in_shard[shard_id]) return false; // Duplicate transaction reference for this shard in the same global transaction.
            used_in_shard[shard_id] = true;
            if (shard_map[shard_id].find(txn_id) == shard_map[shard_id].end()) return false; // Transaction not found in shard log.
            int txn_index = shard_map[shard_id][txn_id];
            shard_entries[shard_id].push_back({g, txn_index});
        }
    }

    // Verify ordering consistency and no phantom reads for each shard.
    // For each shard, transactions from global transactions must appear in the shard log in ascending order.
    for (int s = 0; s < num_shards; s++) {
        // Sort the entries by the global transaction order.
        sort(shard_entries[s].begin(), shard_entries[s].end(), [](const pair<int, int>& a, const pair<int, int>& b) {
            return a.first < b.first;
        });
        // Check that the shard log indices are strictly increasing.
        for (size_t i = 1; i < shard_entries[s].size(); i++) {
            if (shard_entries[s][i].second <= shard_entries[s][i - 1].second) return false;
        }
    }

    return true;
}

}  // namespace transaction_validation