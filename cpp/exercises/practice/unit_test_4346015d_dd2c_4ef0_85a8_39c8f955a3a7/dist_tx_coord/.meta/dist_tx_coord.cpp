#include "dist_tx_coord.h"
#include <chrono>
#include <thread>

namespace dist_tx_coord {

TxResult TransactionCoordinator::processTransaction(const Transaction& tx) {
    // Simulate processing delay and node behavior.
    
    // Special case: if transaction id indicates timeout, simulate a timeout
    if (tx.id == "tx_timeout") {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        return TxResult::TIMEOUT;
    }
    
    // Process each operation as per node behavior simulation.
    for (const auto& op : tx.operations) {
        if (op.node_id == "fail") {
            // If any operation targets a failed node, simulate a rollback.
            return TxResult::ROLLBACK;
        }
        if (op.node_id == "slow") {
            // Simulate a delay that causes the transaction to timeout.
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            return TxResult::TIMEOUT;
        }
    }
    
    // If there are no errors or delays, simulate a commit.
    return TxResult::COMMIT;
}

} // namespace dist_tx_coord