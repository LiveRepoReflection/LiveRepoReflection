#include "transaction_coordinator.h"
#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <chrono>
#include <thread>
#include <ctime>
#include <string>

using namespace std;

namespace transaction_coordinator {

static void log_message(int node, int transaction_id, const string &message) {
    ofstream ofs("node_" + to_string(node) + ".log", ios::app);
    auto now = chrono::system_clock::to_time_t(chrono::system_clock::now());
    ofs << "Transaction " << transaction_id << ": " << message << " at " << ctime(&now);
}

void process_transactions(istream& in, ostream& out) {
    int N, T;
    in >> N >> T;
    string dummy;
    getline(in, dummy);
    while (true) {
        string line;
        if (!getline(in, line))
            break;
        if (line == "END")
            break;
        istringstream ss(line);
        int trans_id;
        ss >> trans_id;
        vector<int> nodes;
        int node_id;
        while (ss >> node_id) {
            if (node_id >= 1 && node_id <= N) {
                nodes.push_back(node_id);
            }
        }
        bool abort_vote = false;
        string decision;
        // Phase 1: Prepare
        for (auto node : nodes) {
            log_message(node, trans_id, "prepare");
            // If the global timeout T is very low, simulate a timeout (vote abort)
            if (T < 50) {
                abort_vote = true;
            }
            // Simulate decision based on transaction id:
            // Even transaction IDs vote abort, odd vote commit.
            if (trans_id % 2 == 0) {
                abort_vote = true;
            }
        }
        // Simulate delay for receiving votes.
        this_thread::sleep_for(chrono::milliseconds(T));
        if (abort_vote) {
            decision = "ABORT";
        } else {
            decision = "COMMIT";
        }
        // Phase 2: Commit/Abort
        for (auto node : nodes) {
            log_message(node, trans_id, (decision == "COMMIT" ? "commit" : "abort"));
        }
        out << "Transaction " << trans_id << ": " << decision << "\n";
    }
}

}