#include "tx_validation.h"
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <sstream>
#include <algorithm>

namespace tx_validation {

enum class ServiceState {
    NONE,       // Initial state
    PREPARED,   // Service received prepare message
    VOTED,      // Service has voted
    COMPLETED   // Service has completed the transaction
};

enum class TransactionState {
    PENDING,    // Transaction has been prepared but not all services have voted
    COMMITTED,  // Transaction has been committed
    ABORTED     // Transaction has been aborted
};

enum class VoteType {
    NONE,       // No vote yet
    COMMIT,     // Vote to commit
    ABORT       // Vote to abort
};

// Structure to track service state for a transaction
struct ServiceInfo {
    ServiceState state = ServiceState::NONE;
    VoteType vote = VoteType::NONE;
};

// Structure to track overall transaction state
struct TransactionInfo {
    TransactionState state = TransactionState::PENDING;
    std::unordered_map<std::string, ServiceInfo> services;
    bool hasAbortVote = false;
    int votesReceived = 0;
    int expectedVotes = 0;  // This will be determined dynamically
};

// Parse a log entry into its components
bool parseLine(const std::string& line, std::string& action, int& tid, std::string& serviceId) {
    std::istringstream iss(line);
    std::string tidStr;
    
    if (!(iss >> action)) return false;
    
    if (action == "COMMIT" || action == "ABORT") {
        if (!(iss >> tidStr)) return false;
        tid = std::stoi(tidStr);
        serviceId = "";
        return true;
    } else {
        if (!(iss >> tidStr >> serviceId)) return false;
        tid = std::stoi(tidStr);
        return true;
    }
}

bool validate_transactions(const std::vector<std::string>& logs) {
    std::unordered_map<int, TransactionInfo> transactions;
    std::unordered_set<int> preparedServices;

    for (const auto& line : logs) {
        std::string action, serviceId;
        int tid;
        
        if (!parseLine(line, action, tid, serviceId)) {
            return false;
        }
        
        // Get or create transaction record
        if (transactions.find(tid) == transactions.end()) {
            transactions[tid] = TransactionInfo();
        }
        TransactionInfo& txInfo = transactions[tid];
        
        if (action == "PREPARE") {
            // Constraint 1: A service must receive a PREPARE message before voting
            if (txInfo.services[serviceId].state != ServiceState::NONE) {
                return false;  // Service already prepared or in a later state
            }
            
            txInfo.services[serviceId].state = ServiceState::PREPARED;
            txInfo.expectedVotes++;
            
        } else if (action == "VOTE_COMMIT" || action == "VOTE_ABORT") {
            // Get or create service record
            ServiceInfo& svcInfo = txInfo.services[serviceId];
            
            // Constraint 1: Must prepare before vote
            if (svcInfo.state != ServiceState::PREPARED) {
                return false;
            }
            
            // Constraint 2: Can only vote once
            if (svcInfo.state == ServiceState::VOTED) {
                return false;
            }
            
            svcInfo.state = ServiceState::VOTED;
            txInfo.votesReceived++;
            
            if (action == "VOTE_COMMIT") {
                svcInfo.vote = VoteType::COMMIT;
            } else { // VOTE_ABORT
                svcInfo.vote = VoteType::ABORT;
                txInfo.hasAbortVote = true;
            }
            
        } else if (action == "COMMIT") {
            // Constraint 3: All services must vote before commit/abort
            if (txInfo.votesReceived != txInfo.expectedVotes || txInfo.expectedVotes == 0) {
                return false;
            }
            
            // Constraint 4: Cannot commit if any service voted to abort
            if (txInfo.hasAbortVote) {
                return false;
            }
            
            txInfo.state = TransactionState::COMMITTED;
            
        } else if (action == "ABORT") {
            // Constraint 3: All services must vote before commit/abort
            if (txInfo.votesReceived != txInfo.expectedVotes || txInfo.expectedVotes == 0) {
                return false;
            }
            
            // Constraint 4: Cannot abort if no service voted to abort
            if (!txInfo.hasAbortVote) {
                return false;
            }
            
            txInfo.state = TransactionState::ABORTED;
            
        } else if (action == "COMPLETE") {
            // Constraint 5: Can only complete after commit/abort decision
            if (txInfo.state != TransactionState::COMMITTED && txInfo.state != TransactionState::ABORTED) {
                return false;
            }
            
            ServiceInfo& svcInfo = txInfo.services[serviceId];
            
            // Constraint 6: Service can't complete if it didn't participate
            if (svcInfo.state != ServiceState::VOTED) {
                return false;
            }
            
            // Constraint 7: Service can complete only once
            if (svcInfo.state == ServiceState::COMPLETED) {
                return false;
            }
            
            svcInfo.state = ServiceState::COMPLETED;
        }
    }
    
    return true;
}

bool validate_transactions(std::istream& log_stream) {
    std::vector<std::string> logs;
    std::string line;
    while (std::getline(log_stream, line)) {
        if (!line.empty()) {
            logs.push_back(line);
        }
    }
    return validate_transactions(logs);
}

}  // namespace tx_validation