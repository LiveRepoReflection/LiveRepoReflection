#include "txn_manager.h"
#include "catch.hpp"
#include <thread>
#include <chrono>
#include <atomic>
#include <vector>

namespace {
    bool prepare_success() { return true; }
    bool prepare_fail() { return false; }
    bool commit_success() { return true; }
    bool commit_fail() { return false; }
    bool rollback_success() { return true; }
    
    bool throw_exception() {
        throw std::runtime_error("Simulated failure");
        return false;
    }

    std::atomic<int> prepare_count{0};
    std::atomic<int> commit_count{0};
    std::atomic<int> rollback_count{0};

    bool counting_prepare() {
        prepare_count++;
        return true;
    }

    bool counting_commit() {
        commit_count++;
        return true;
    }

    bool counting_rollback() {
        rollback_count++;
        return true;
    }

    void reset_counters() {
        prepare_count = 0;
        commit_count = 0;
        rollback_count = 0;
    }
}

TEST_CASE("Simple successful transaction", "[basic]") {
    txn_manager::DistributedTransactionManager dtm;
    auto tid = dtm.begin_transaction();
    
    REQUIRE(dtm.enlist_resource(tid, 1, prepare_success, commit_success, rollback_success));
    REQUIRE(dtm.commit_transaction(tid));
}

TEST_CASE("Transaction with multiple resources - all succeed", "[basic]") {
    txn_manager::DistributedTransactionManager dtm;
    auto tid = dtm.begin_transaction();
    
    reset_counters();
    
    REQUIRE(dtm.enlist_resource(tid, 1, counting_prepare, counting_commit, counting_rollback));
    REQUIRE(dtm.enlist_resource(tid, 2, counting_prepare, counting_commit, counting_rollback));
    REQUIRE(dtm.enlist_resource(tid, 3, counting_prepare, counting_commit, counting_rollback));
    
    REQUIRE(dtm.commit_transaction(tid));
    
    REQUIRE(prepare_count == 3);
    REQUIRE(commit_count == 3);
    REQUIRE(rollback_count == 0);
}

TEST_CASE("Transaction with prepare failure should rollback", "[failure]") {
    txn_manager::DistributedTransactionManager dtm;
    auto tid = dtm.begin_transaction();
    
    reset_counters();
    
    REQUIRE(dtm.enlist_resource(tid, 1, counting_prepare, counting_commit, counting_rollback));
    REQUIRE(dtm.enlist_resource(tid, 2, prepare_fail, counting_commit, counting_rollback));
    REQUIRE(dtm.enlist_resource(tid, 3, counting_prepare, counting_commit, counting_rollback));
    
    REQUIRE_FALSE(dtm.commit_transaction(tid));
    
    REQUIRE(rollback_count > 0);
}

TEST_CASE("Transaction with commit failure should return false", "[failure]") {
    txn_manager::DistributedTransactionManager dtm;
    auto tid = dtm.begin_transaction();
    
    REQUIRE(dtm.enlist_resource(tid, 1, prepare_success, commit_fail, rollback_success));
    REQUIRE_FALSE(dtm.commit_transaction(tid));
}

TEST_CASE("Exception during prepare should trigger rollback", "[exception]") {
    txn_manager::DistributedTransactionManager dtm;
    auto tid = dtm.begin_transaction();
    
    reset_counters();
    
    REQUIRE(dtm.enlist_resource(tid, 1, counting_prepare, counting_commit, counting_rollback));
    REQUIRE(dtm.enlist_resource(tid, 2, throw_exception, counting_commit, counting_rollback));
    
    REQUIRE_FALSE(dtm.commit_transaction(tid));
    REQUIRE(rollback_count > 0);
}

TEST_CASE("Empty transaction should succeed", "[edge]") {
    txn_manager::DistributedTransactionManager dtm;
    auto tid = dtm.begin_transaction();
    
    REQUIRE(dtm.commit_transaction(tid));
}

TEST_CASE("Concurrent transactions should not interfere", "[concurrent]") {
    txn_manager::DistributedTransactionManager dtm;
    std::atomic<int> success_count{0};
    
    auto execute_transaction = [&]() {
        auto tid = dtm.begin_transaction();
        if (dtm.enlist_resource(tid, 1, prepare_success, commit_success, rollback_success)) {
            if (dtm.commit_transaction(tid)) {
                success_count++;
            }
        }
    };
    
    std::vector<std::thread> threads;
    for (int i = 0; i < 10; i++) {
        threads.emplace_back(execute_transaction);
    }
    
    for (auto& thread : threads) {
        thread.join();
    }
    
    REQUIRE(success_count == 10);
}

TEST_CASE("Duplicate resource IDs should fail", "[validation]") {
    txn_manager::DistributedTransactionManager dtm;
    auto tid = dtm.begin_transaction();
    
    REQUIRE(dtm.enlist_resource(tid, 1, prepare_success, commit_success, rollback_success));
    REQUIRE_FALSE(dtm.enlist_resource(tid, 1, prepare_success, commit_success, rollback_success));
}

TEST_CASE("Invalid transaction ID should fail", "[validation]") {
    txn_manager::DistributedTransactionManager dtm;
    
    REQUIRE_FALSE(dtm.enlist_resource(999, 1, prepare_success, commit_success, rollback_success));
    REQUIRE_FALSE(dtm.commit_transaction(999));
    REQUIRE_FALSE(dtm.rollback_transaction(999));
}

TEST_CASE("Manual rollback should succeed", "[rollback]") {
    txn_manager::DistributedTransactionManager dtm;
    auto tid = dtm.begin_transaction();
    
    reset_counters();
    
    REQUIRE(dtm.enlist_resource(tid, 1, counting_prepare, counting_commit, counting_rollback));
    REQUIRE(dtm.enlist_resource(tid, 2, counting_prepare, counting_commit, counting_rollback));
    
    REQUIRE(dtm.rollback_transaction(tid));
    REQUIRE(rollback_count == 2);
}