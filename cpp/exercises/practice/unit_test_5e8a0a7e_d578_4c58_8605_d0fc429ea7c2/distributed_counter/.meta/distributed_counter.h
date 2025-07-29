#ifndef DISTRIBUTED_COUNTER_H
#define DISTRIBUTED_COUNTER_H

#include <unordered_map>
#include <mutex>

namespace distributed_counter {

class DistributedCounter {
public:
    DistributedCounter();
    void increment(int value);
    int get_count() const;
    void sync_with(const DistributedCounter &other);
private:
    int replica_id;
    std::unordered_map<int, int> pos;
    std::unordered_map<int, int> neg;
    mutable std::mutex mtx;
    void merge_maps(const std::unordered_map<int, int>& other_map, std::unordered_map<int, int>& self_map);
    static int get_next_id();
};

}

#endif