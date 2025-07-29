#include "distributed_tx.h"
#include <thread>
#include <future>
#include <mutex>
#include <algorithm>
#include <iostream>
#include <chrono>

namespace distributed_tx {

// Shard Implementation

Shard::Shard() : id_(0), last_transaction_id_(-1), last_vote_(Vote::Abort) {}

Shard::Shard(int id) : id_(id), last_transaction_id_(-1), last_vote_(Vote::Abort) {}

int Shard::getId() const {
    return id_;
}

Vote Shard::prepare(int transaction_id, const Operation& op, std::chrono::milliseconds timeout) {
    // Simulate delay to trigger timeout if the key is "timeout"
    if (op.key == "timeout") {
        std::this_thread::sleep_for(timeout + std::chrono::milliseconds(100));
        last_transaction_id_ = transaction_id;
        last_vote_ = Vote::Timeout;
        return Vote::Timeout;
    }
    // Force an abort vote if the key is "abort"
    if (op.key == "abort") {
        last_transaction_id_ = transaction_id;
        last_vote_ = Vote::Abort;
        return Vote::Abort;
    }
    // Simulate normal processing time
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    last_transaction_id_ = transaction_id;
    last_vote_ = Vote::Commit;
    return Vote::Commit;
}

void Shard::commit(int transaction_id) {
    // Commit only if the transaction id matches and last vote was commit
    if (last_transaction_id_ == transaction_id && last_vote_ == Vote::Commit) {
        // For simulation purposes, the commit finalization is a no-op.
    }
}

void Shard::rollback(int transaction_id) {
    // Rollback the transaction if the transaction id matches
    if (last_transaction_id_ == transaction_id) {
        last_vote_ = Vote::Abort;
    }
}

bool Shard::recover(int transaction_id) {
    // On recovery, if last vote was commit, then complete commit; otherwise, rollback.
    if (last_transaction_id_ == transaction_id) {
        if (last_vote_ == Vote::Commit) {
            commit(transaction_id);
            return true;
        } else {
            rollback(transaction_id);
            return false;
        }
    }
    return false;
}

// TransactionCoordinator Implementation

TransactionCoordinator::TransactionCoordinator() : next_transaction_id_(1) {
    // Initialize shards with ids 0 through 100
    shards_.reserve(101);
    for (int i = 0; i <= 100; i++) {
        shards_.push_back(Shard(i));
    }
}

Shard* TransactionCoordinator::getShard(int shard_id) {
    if (shard_id >= 0 && shard_id < static_cast<int>(shards_.size())) {
        return &shards_[shard_id];
    }
    return nullptr;
}

bool TransactionCoordinator::submitTransaction(const std::vector<Operation>& ops, std::chrono::milliseconds timeout) {
    int transaction_id = next_transaction_id_++;
    bool all_commit = true;
    // Gather unique shard ids involved in the transaction
    std::vector<int> shard_ids;
    for (const auto& op : ops) {
        if (std::find(shard_ids.begin(), shard_ids.end(), op.shard_id) == shard_ids.end()) {
            shard_ids.push_back(op.shard_id);
        }
    }
    
    // Phase 1: Prepare
    for (const auto& op : ops) {
        Shard* shard = getShard(op.shard_id);
        if (shard) {
            Vote vote = shard->prepare(transaction_id, op, timeout);
            if (vote != Vote::Commit) {
                all_commit = false;
            }
        } else {
            all_commit = false;
        }
    }
    
    // Phase 2: Commit or Rollback
    if (all_commit) {
        // Commit concurrently on all involved shards
        std::vector<std::thread> commit_threads;
        for (int id : shard_ids) {
            commit_threads.emplace_back([this, transaction_id, id]() {
                Shard* shard = getShard(id);
                if (shard) {
                    shard->commit(transaction_id);
                }
            });
        }
        for (auto& t : commit_threads) {
            t.join();
        }
        return true;
    } else {
        // Rollback sequentially on all involved shards
        for (int id : shard_ids) {
            Shard* shard = getShard(id);
            if (shard) {
                shard->rollback(transaction_id);
            }
        }
        return false;
    }
}

bool TransactionCoordinator::submitTransactionWithCrash(const std::vector<Operation>& ops, std::chrono::milliseconds timeout) {
    int transaction_id = next_transaction_id_++;
    bool all_commit = true;
    std::vector<int> shard_ids;
    for (const auto& op : ops) {
        if (std::find(shard_ids.begin(), shard_ids.end(), op.shard_id) == shard_ids.end()) {
            shard_ids.push_back(op.shard_id);
        }
    }
    
    // Phase 1: Prepare, then simulate a crash before sending commit/rollback
    for (const auto& op : ops) {
        Shard* shard = getShard(op.shard_id);
        if (shard) {
            Vote vote = shard->prepare(transaction_id, op, timeout);
            if (vote != Vote::Commit) {
                all_commit = false;
            }
        } else {
            all_commit = false;
        }
    }
    
    // Simulate crash by storing pending transaction details for later recovery
    PendingTransaction pt;
    pt.id = transaction_id;
    pt.shard_ids = shard_ids;
    pt.all_commit = all_commit;
    pending_transactions_.push_back(pt);
    
    // Return false since the transaction did not complete
    return false;
}

bool TransactionCoordinator::recoverTransaction() {
    bool overallCommit = true;
    // Process each pending transaction
    for (auto& pt : pending_transactions_) {
        if (pt.all_commit) {
            // Attempt to commit concurrently
            std::vector<std::thread> commit_threads;
            for (int id : pt.shard_ids) {
                commit_threads.emplace_back([this, pt, id]() {
                    Shard* shard = getShard(id);
                    if (shard) {
                        shard->commit(pt.id);
                    }
                });
            }
            for (auto& t : commit_threads) {
                t.join();
            }
        } else {
            // Rollback if not all shards voted commit
            for (int id : pt.shard_ids) {
                Shard* shard = getShard(id);
                if (shard) {
                    shard->rollback(pt.id);
                }
            }
            overallCommit = false;
        }
    }
    pending_transactions_.clear();
    return overallCommit;
}

} // namespace distributed_tx