#include "distributed_tx.h"
#include <iostream>
#include <sstream>
#include <vector>
#include <thread>
#include <random>
#include <string>

namespace distributed_tx {

struct TransactionData {
    int transactionId;
    std::vector<std::pair<int, double>> participants; // first: participant id, second: commit probability
};

void processTransactions(std::istream& input, std::ostream& output) {
    int numTransactions = 0;
    if (!(input >> numTransactions)) {
        return;
    }

    std::vector<TransactionData> transactions(numTransactions);
    for (int i = 0; i < numTransactions; i++) {
        TransactionData tx;
        int numParticipants = 0;
        input >> tx.transactionId >> numParticipants;
        for (int j = 0; j < numParticipants; j++) {
            int participantId = 0;
            double commitProbability = 0.0;
            input >> participantId >> commitProbability;
            tx.participants.push_back({participantId, commitProbability});
        }
        transactions[i] = tx;
    }

    // Vector to store transaction results in input order.
    std::vector<std::string> results(numTransactions);

    // Create a thread for each transaction.
    std::vector<std::thread> threads;
    for (size_t i = 0; i < transactions.size(); i++) {
        threads.emplace_back([i, &transactions, &results]() {
            bool allAgree = true;
            // Each thread has its own random engine.
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dis(0.0, 1.0);

            // First phase: collect votes from all participants.
            for (const auto &participant : transactions[i].participants) {
                // Generate a random vote.
                if (dis(gen) >= participant.second) {
                    allAgree = false;
                    break;
                }
            }
            // Second phase: instruct commit or rollback.
            if (allAgree) {
                results[i] = "Transaction " + std::to_string(transactions[i].transactionId) + ": Committed\n";
            } else {
                results[i] = "Transaction " + std::to_string(transactions[i].transactionId) + ": Rolled Back\n";
            }
        });
    }

    // Wait for all threads to complete.
    for (auto &thr : threads) {
        if (thr.joinable()) {
            thr.join();
        }
    }

    // Output the results preserving the input order.
    for (const auto &result : results) {
        output << result;
    }
}

}