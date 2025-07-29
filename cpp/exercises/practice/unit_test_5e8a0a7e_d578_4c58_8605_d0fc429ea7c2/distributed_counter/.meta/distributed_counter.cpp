#include "distributed_counter.h"
#include <atomic>
#include <algorithm>

namespace distributed_counter {

static std::atomic<int> global_id{0};

int DistributedCounter::get_next_id() {
    return global_id.fetch_add(1);
}

DistributedCounter::DistributedCounter() {
    replica_id = get_next_id();
    pos[replica_id] = 0;
    neg[replica_id] = 0;
}

void DistributedCounter::increment(int value) {
    std::lock_guard<std::mutex> lock(mtx);
    if (value > 0) {
        pos[replica_id] += value;
    } else if (value < 0) {
        neg[replica_id] += -value;
    }
    // Zero increments are recorded as an operation but do not affect the local state.
}

int DistributedCounter::get_count() const {
    std::lock_guard<std::mutex> lock(mtx);
    int sum_pos = 0;
    int sum_neg = 0;
    for (const auto &entry : pos) {
        sum_pos += entry.second;
    }
    for (const auto &entry : neg) {
        sum_neg += entry.second;
    }
    return sum_pos - sum_neg;
}

void DistributedCounter::merge_maps(const std::unordered_map<int, int>& other_map, std::unordered_map<int, int>& self_map) {
    for (const auto &entry : other_map) {
        int id = entry.first;
        int value = entry.second;
        auto it = self_map.find(id);
        if (it == self_map.end()) {
            self_map[id] = value;
        } else {
            // Merge by taking the maximum recorded value.
            if (value > it->second) {
                it->second = value;
            }
        }
    }
}

void DistributedCounter::sync_with(const DistributedCounter &other) {
    // To avoid deadlocks, lock both mutexes in a fixed order using std::lock.
    std::unique_lock<std::mutex> lock1(mtx, std::defer_lock);
    std::unique_lock<std::mutex> lock2(other.mtx, std::defer_lock);
    std::lock(lock1, lock2);

    merge_maps(other.pos, pos);
    merge_maps(other.neg, neg);
}

}