#include "txn_validator.h"
#include <sstream>
#include <unordered_map>
#include <set>
#include <vector>

struct TransactionEvent {
    std::string serviceId;
    std::string eventType;
    long long timestamp;
};

class Transaction {
private:
    std::set<std::string> preparedServices;
    std::set<std::string> committedServices;
    std::set<std::string> abortedServices;
    bool hasCoordinatorCommit = false;
    bool hasCoordinatorAbort = false;

public:
    void addEvent(const std::string& serviceId, const std::string& eventType) {
        if (eventType == "PREPARE") {
            preparedServices.insert(serviceId);
        } else if (eventType == "COMMIT") {
            committedServices.insert(serviceId);
        } else if (eventType == "ABORT") {
            abortedServices.insert(serviceId);
        } else if (eventType == "COORDINATOR_COMMIT") {
            hasCoordinatorCommit = true;
        } else if (eventType == "COORDINATOR_ABORT") {
            hasCoordinatorAbort = true;
        }
    }

    std::string getStatus() const {
        // Check for inconsistent coordinator decisions
        if (hasCoordinatorCommit && hasCoordinatorAbort) {
            return "INCONSISTENT";
        }

        // Check for commits without prepares
        for (const auto& service : committedServices) {
            if (preparedServices.find(service) == preparedServices.end()) {
                return "INCONSISTENT";
            }
        }

        // Check for aborts after commits
        for (const auto& service : abortedServices) {
            if (committedServices.find(service) != committedServices.end()) {
                return "INCONSISTENT";
            }
        }

        // Check for successful commit
        if (hasCoordinatorCommit) {
            if (!abortedServices.empty()) {
                return "INCONSISTENT";
            }
            if (preparedServices == committedServices && !preparedServices.empty()) {
                return "COMMITTED";
            }
            return "INCONSISTENT";
        }

        // Check for abort
        if (hasCoordinatorAbort || !abortedServices.empty()) {
            if (!committedServices.empty()) {
                return "INCONSISTENT";
            }
            return "ABORTED";
        }

        // No coordinator decision but some services committed or aborted
        if (!committedServices.empty() || !abortedServices.empty()) {
            return "INCONSISTENT";
        }

        // If we only have prepares, it's inconsistent
        if (!preparedServices.empty()) {
            return "INCONSISTENT";
        }

        return "INCONSISTENT";
    }
};

std::string validate_transactions(const std::string& log) {
    std::unordered_map<std::string, Transaction> transactions;
    std::set<std::string> transactionIds;
    std::istringstream stream(log);
    std::string line;

    // Parse log file
    while (std::getline(stream, line)) {
        std::istringstream lineStream(line);
        std::string txnId, serviceId, eventType, timestamp;

        if (std::getline(lineStream, txnId, ',') &&
            std::getline(lineStream, serviceId, ',') &&
            std::getline(lineStream, eventType, ',') &&
            std::getline(lineStream, timestamp)) {

            transactionIds.insert(txnId);
            transactions[txnId].addEvent(serviceId, eventType);
        }
    }

    // Generate output
    std::string result;
    for (const auto& txnId : transactionIds) {
        result += txnId + "," + transactions[txnId].getStatus() + "\n";
    }

    return result;
}