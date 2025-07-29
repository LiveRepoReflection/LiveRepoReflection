#include "distributed_tx.h"
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <regex>
#include <algorithm>

namespace {

struct Operation {
    int node_id;
    int operation_type;
    std::string data;
};

struct Transaction {
    int transaction_id;
    std::vector<int> involved_nodes;
    std::vector<Operation> operations;
    std::vector<int> failed_nodes;
};

std::string trim(const std::string &s) {
    auto start = s.find_first_not_of(" \t\n\r");
    if (start == std::string::npos) return "";
    auto end = s.find_last_not_of(" \t\n\r");
    return s.substr(start, end - start + 1);
}

std::vector<int> parseIntArray(const std::string &s) {
    std::vector<int> result;
    std::istringstream iss(s);
    std::string token;
    while(getline(iss, token, ',')) {
        token = trim(token);
        if (!token.empty()) {
            try {
                int num = std::stoi(token);
                result.push_back(num);
            } catch (...) {
                // ignore conversion errors
            }
        }
    }
    return result;
}

std::vector<Operation> parseOperations(const std::string &s) {
    std::vector<Operation> ops;
    std::regex op_re("\\{\\s*\"node_id\"\\s*:\\s*(\\d+)\\s*,\\s*\"operation_type\"\\s*:\\s*(\\d+)\\s*,\\s*\"data\"\\s*:\\s*\"([^\"]*)\"\\s*\\}");
    auto begin = std::sregex_iterator(s.begin(), s.end(), op_re);
    auto end = std::sregex_iterator();
    for (auto it = begin; it != end; ++it) {
        std::smatch match = *it;
        Operation op;
        op.node_id = std::stoi(match[1].str());
        op.operation_type = std::stoi(match[2].str());
        op.data = match[3].str();
        ops.push_back(op);
    }
    return ops;
}

Transaction parseTransactionLine(const std::string &line) {
    Transaction tx;
    std::regex txid_re("\"transaction_id\"\\s*:\\s*(\\d+)");
    std::regex nodes_re("\"involved_nodes\"\\s*:\\s*\\[([^\\]]*)\\]");
    std::regex failed_re("\"failed_nodes\"\\s*:\\s*\\[([^\\]]*)\\]");
    std::regex ops_re("\"operations\"\\s*:\\s*\\[([^\\]]*)\\]");
    
    std::smatch match;
    if (std::regex_search(line, match, txid_re)) {
        tx.transaction_id = std::stoi(match[1].str());
    }
    if (std::regex_search(line, match, nodes_re)) {
        std::string arr_str = match[1].str();
        tx.involved_nodes = parseIntArray(arr_str);
    }
    if (std::regex_search(line, match, failed_re)) {
        std::string arr_str = match[1].str();
        tx.failed_nodes = parseIntArray(arr_str);
    }
    if (std::regex_search(line, match, ops_re)) {
        std::string ops_str = match[1].str();
        tx.operations = parseOperations(ops_str);
    }
    return tx;
}

}  // namespace

namespace distributed_tx {

// The run function simulates a distributed transaction coordinator using 2PC.
void run(std::istream& in, std::ostream& out) {
    int N, M;
    in >> N >> M;
    in.ignore(); // consume newline

    // For idempotency: store transaction_id to the complete output produced previously.
    std::unordered_map<int, std::string> processed;

    for (int i = 0; i < M; i++) {
        std::string line;
        getline(in, line);
        line = trim(line);
        if (line.empty()) {
            i--;
            continue;
        }
        Transaction tx = parseTransactionLine(line);

        // Check idempotency: if this transaction was processed, output previous result.
        if (processed.find(tx.transaction_id) != processed.end()) {
            out << processed[tx.transaction_id];
            continue;
        }

        // Simulate 2PC.
        // Each involved node logs its decisions for this transaction.
        std::unordered_map<int, std::vector<std::string>> nodeLogs;
        // Phase 1: Prepare Phase.
        // Each node logs "PREPARED <transaction_id>"
        for (int node : tx.involved_nodes) {
            nodeLogs[node].push_back("PREPARED " + std::to_string(tx.transaction_id));
        }
        // Each node votes commit unless it is in failed_nodes.
        bool allVoteCommit = true;
        for (int node : tx.involved_nodes) {
            if (std::find(tx.failed_nodes.begin(), tx.failed_nodes.end(), node) != tx.failed_nodes.end()) {
                allVoteCommit = false;
                // In prepare phase, node simulates failure by voting abort.
            }
        }
        std::string outcome;
        if (allVoteCommit) {
            outcome = "COMMIT";
        } else {
            outcome = "ROLLBACK";
        }
        // Phase 2: Commit/Rollback Phase.
        // For each node, log the final decision.
        for (int node : tx.involved_nodes) {
            if (outcome == "COMMIT") {
                // Node that was not failed should commit
                if (std::find(tx.failed_nodes.begin(), tx.failed_nodes.end(), node) == tx.failed_nodes.end())
                    nodeLogs[node].push_back("COMMITTED " + std::to_string(tx.transaction_id));
                else
                    nodeLogs[node].push_back("ABORTED " + std::to_string(tx.transaction_id));
            } else {
                // Rollback for everyone
                nodeLogs[node].push_back("ABORTED " + std::to_string(tx.transaction_id));
            }
        }
        // Prepare the output for this transaction.
        std::ostringstream oss;
        oss << outcome << "\n";
        // Print logs in the order of node id as in involved_nodes.
        // According to sample, each line: Node <node_id>: [log1, log2]
        for (int node : tx.involved_nodes) {
            oss << "Node " << node << ": [";
            for (size_t j = 0; j < nodeLogs[node].size(); j++) {
                oss << nodeLogs[node][j];
                if (j != nodeLogs[node].size() - 1) {
                    oss << ", ";
                }
            }
            oss << "]\n";
        }
        std::string txOutput = oss.str();
        // Store in idempotency map.
        processed[tx.transaction_id] = txOutput;
        out << txOutput;
    }
}

}  // namespace distributed_tx