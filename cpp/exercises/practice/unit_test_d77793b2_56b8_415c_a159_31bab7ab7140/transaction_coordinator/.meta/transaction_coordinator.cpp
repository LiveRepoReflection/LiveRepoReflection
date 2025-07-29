#include "transaction_coordinator.h"
#include <iostream>

namespace transaction_coordinator {

TransactionCoordinator::TransactionCoordinator() {
}

void TransactionCoordinator::processBeginTransaction(int transaction_id, const std::set<int>& participants) {
    std::lock_guard<std::mutex> lock(mtx);
    Transaction t;
    t.id = transaction_id;
    t.participants = participants;
    t.status = TransactionStatus::ONGOING;
    transactions[transaction_id] = t;
}

void TransactionCoordinator::processVoteRequest(int transaction_id, int node_id, bool commitVote) {
    std::lock_guard<std::mutex> lock(mtx);
    auto it = transactions.find(transaction_id);
    if (it == transactions.end()) {
        std::cout << "Invalid transaction ID " << transaction_id << "\n";
        if (commitVote) {
            std::cout << "Node " << node_id << " COMMIT vote received for transaction " << transaction_id << ".\n";
        } else {
            std::cout << "Node " << node_id << " ABORT vote received for transaction " << transaction_id << ".\n";
        }
        return;
    }
    
    if (commitVote) {
        std::cout << "Node " << node_id << " COMMIT vote received for transaction " << transaction_id << ".\n";
    } else {
        std::cout << "Node " << node_id << " ABORT vote received for transaction " << transaction_id << ".\n";
    }
    
    Transaction &t = it->second;
    if (t.status == TransactionStatus::COMMITTED || t.status == TransactionStatus::ABORTED) {
        return;
    }
    
    if (!commitVote) {
        t.status = TransactionStatus::ABORTED;
        std::cout << "Transaction " << transaction_id << " aborted.\n";
        for (const auto &node : t.participants) {
            std::cout << "Node " << node << " instructed to ROLLBACK for transaction " << transaction_id << ".\n";
        }
        std::cout << "Transaction " << transaction_id << " rolled back.\n";
    } else {
        t.votes[node_id] = true;
        if (t.votes.size() == t.participants.size()) {
            t.status = TransactionStatus::COMMITTED;
            std::cout << "Transaction " << transaction_id << " prepared to commit (all nodes voted COMMIT).\n";
            std::cout << "Transaction " << transaction_id << " committed.\n";
            for (const auto &node : t.participants) {
                std::cout << "Node " << node << " instructed to COMMIT for transaction " << transaction_id << ".\n";
            }
        }
    }
}

void TransactionCoordinator::processCoordinatorTimeout(int transaction_id) {
    std::lock_guard<std::mutex> lock(mtx);
    auto it = transactions.find(transaction_id);
    if (it == transactions.end()) {
        std::cout << "Invalid transaction ID " << transaction_id << "\n";
        return;
    }
    std::cout << "Coordinator timed out waiting for votes for transaction " << transaction_id << ".\n";
    Transaction &t = it->second;
    if (t.status == TransactionStatus::COMMITTED || t.status == TransactionStatus::ABORTED) {
        return;
    }
    t.status = TransactionStatus::ABORTED;
    std::cout << "Transaction " << transaction_id << " aborted.\n";
    for (const auto &node : t.participants) {
        std::cout << "Node " << node << " instructed to ROLLBACK for transaction " << transaction_id << ".\n";
    }
    std::cout << "Transaction " << transaction_id << " rolled back.\n";
}

} // namespace transaction_coordinator