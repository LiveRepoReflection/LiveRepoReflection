#pragma once
#include <vector>
#include <unordered_map>
#include <cstdint>
#include <stdexcept>
#include <mutex>

class DistributedMedian {
public:
    DistributedMedian();
    void update(int sensor_id, const std::vector<double>& data);
    double get_median();

private:
    struct SensorSummary {
        uint64_t count;
        double sensor_median;
    };
    std::unordered_map<int, SensorSummary> sensors;
    std::mutex mtx;
};