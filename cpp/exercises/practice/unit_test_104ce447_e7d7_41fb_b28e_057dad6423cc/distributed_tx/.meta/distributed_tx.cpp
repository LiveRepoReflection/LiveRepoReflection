#include "distributed_tx.h"
#include <sstream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>

namespace distributed_tx {

void processTransactions(std::istream &in, std::ostream &out) {
    std::string line;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::istringstream iss(line);
        int tid;
        std::string directive;
        iss >> tid >> directive;
        bool shouldCommit = (directive == "COMMIT");
        bool allAgree = true;
        std::vector<std::pair<int, std::string>> serviceOps;
        
        std::string token;
        while (iss >> token) {
            size_t pos = token.find(':');
            if (pos == std::string::npos) continue;
            int service = std::stoi(token.substr(0, pos));
            std::string op = token.substr(pos + 1);
            serviceOps.push_back({service, op});
        }
        
        // Phase 1: Prepare phase simulation. If any service returns "FAIL", then vote abort.
        for (auto &p : serviceOps) {
            if (p.second == "FAIL") {
                allAgree = false;
                break;
            }
        }
        
        // Phase 2: Decision phase, apply distributed consensus simulation.
        std::string decision;
        if (shouldCommit && allAgree) {
            decision = "COMMIT";
        } else {
            decision = "ROLLBACK";
        }
        
        // Persist decision to secure durability by writing to file.
        {
            std::ofstream ofs("tx_" + std::to_string(tid) + ".log");
            ofs << decision << " " << tid;
        }
        
        // Output the final decision for the transaction.
        out << decision << " " << tid << "\n";
    }
}

} // namespace distributed_tx