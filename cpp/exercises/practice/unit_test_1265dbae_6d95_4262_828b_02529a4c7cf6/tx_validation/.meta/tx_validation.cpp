#include "tx_validation.h"
#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include <map>
#include <functional>
#include <algorithm>

using namespace std;

namespace tx_validation {

struct Transaction {
    // Map key: "node#data_item_key", value: 0 for READ only, 1 for WRITE encountered.
    map<string, int> accesses;
};

void solve(istream &in, ostream &out) {
    int N, M, T;
    in >> N;
    in >> M;
    in >> T;
    vector<Transaction> transactions(T);
    
    for (int i = 0; i < T; i++) {
        int num_ops;
        in >> num_ops;
        for (int j = 0; j < num_ops; j++) {
            string op;
            in >> op;
            int node;
            in >> node;
            string key;
            in >> key;
            int mode = (op == "READ") ? 0 : 1;
            // Create a compound key of node and data_item_key.
            string compound_key = to_string(node) + "#" + key;
            // If key already exists, update to WRITE if any WRITE appears.
            if (transactions[i].accesses.find(compound_key) == transactions[i].accesses.end()) {
                transactions[i].accesses[compound_key] = mode;
            } else {
                transactions[i].accesses[compound_key] = max(transactions[i].accesses[compound_key], mode);
            }
            // For a WRITE operation, also read the value (unused for conflict detection).
            if (op == "WRITE") {
                int value;
                in >> value;
            }
        }
    }
    
    // Build conflict matrix: conflict[i][j] is true if transactions i and j conflict.
    // Two transactions conflict if they both access the same (node, key) and at least one access is a WRITE.
    vector<vector<bool>> conflict(T, vector<bool>(T, false));
    for (int i = 0; i < T; i++) {
        for (int j = i + 1; j < T; j++) {
            bool conf = false;
            // Iterate over the smaller map.
            if (transactions[i].accesses.size() <= transactions[j].accesses.size()) {
                for (auto &entry : transactions[i].accesses) {
                    auto it = transactions[j].accesses.find(entry.first);
                    if (it != transactions[j].accesses.end()) {
                        if (entry.second == 1 || it->second == 1) {
                            conf = true;
                            break;
                        }
                    }
                }
            } else {
                for (auto &entry : transactions[j].accesses) {
                    auto it = transactions[i].accesses.find(entry.first);
                    if (it != transactions[i].accesses.end()) {
                        if (entry.second == 1 || it->second == 1) {
                            conf = true;
                            break;
                        }
                    }
                }
            }
            conflict[i][j] = conflict[j][i] = conf;
        }
    }
    
    // Find the maximum independent set in the conflict graph.
    // For a set of transactions to be serializable, no two transactions in the set may conflict.
    int best = 0;
    // For small T, use recursive backtracking.
    if (T <= 20) {
        vector<int> chosen;
        function<void(int)> dfs = [&](int idx) {
            if (idx == T) {
                best = max(best, (int)chosen.size());
                return;
            }
            // Branch and bound: if even taking all remaining cannot beat best, return early.
            if ((int)chosen.size() + (T - idx) <= best) return;
            // Option 1: Skip current transaction.
            dfs(idx + 1);
            // Option 2: Include current transaction if no conflict with already chosen ones.
            bool canInclude = true;
            for (int sel : chosen) {
                if (conflict[sel][idx]) {
                    canInclude = false;
                    break;
                }
            }
            if (canInclude) {
                chosen.push_back(idx);
                dfs(idx + 1);
                chosen.pop_back();
            }
        };
        dfs(0);
    } else {
        // For larger T, use a greedy heuristic.
        vector<bool> inSet(T, true);
        bool changed = true;
        while (changed) {
            changed = false;
            for (int i = 0; i < T; i++) {
                if (!inSet[i]) continue;
                for (int j = i + 1; j < T; j++) {
                    if (!inSet[j]) continue;
                    if (conflict[i][j]) {
                        // Remove one of the conflicting transactions based on conflict degree.
                        int degree_i = 0, degree_j = 0;
                        for (int k = 0; k < T; k++) {
                            if (inSet[k] && k != i && conflict[i][k])
                                degree_i++;
                            if (inSet[k] && k != j && conflict[j][k])
                                degree_j++;
                        }
                        if (degree_i <= degree_j)
                            inSet[j] = false;
                        else
                            inSet[i] = false;
                        changed = true;
                        break;
                    }
                }
            }
        }
        for (int i = 0; i < T; i++) {
            if (inSet[i])
                best++;
        }
    }
    
    out << best;
}

} // namespace tx_validation