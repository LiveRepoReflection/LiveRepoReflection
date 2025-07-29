#include "distributed_median.h"
#include <algorithm>
#include <vector>

DistributedMedian::DistributedMedian() {}

void DistributedMedian::update(int sensor_id, const std::vector<double>& data) {
    if(data.size() < 6) {
        throw std::invalid_argument("Data vector must contain at least 6 elements.");
    }
    SensorSummary summary;
    summary.count = static_cast<uint64_t>(data[0]);
    summary.sensor_median = data[4];
    
    std::lock_guard<std::mutex> lock(mtx);
    sensors[sensor_id] = summary;
}

double DistributedMedian::get_median() {
    std::lock_guard<std::mutex> lock(mtx);
    if(sensors.empty()) return 0.0;

    std::vector<std::pair<double, uint64_t>> medians;
    uint64_t total_count = 0;
    for(const auto& kv : sensors) {
        total_count += kv.second.count;
        medians.push_back({kv.second.sensor_median, kv.second.count});
    }

    std::sort(medians.begin(), medians.end(), [](const std::pair<double, uint64_t>& a, const std::pair<double, uint64_t>& b) {
        return a.first < b.first;
    });

    bool even = (total_count % 2 == 0);
    uint64_t target1 = total_count / 2;
    uint64_t target2 = target1 + 1;
    uint64_t cumulative = 0;
    double m1 = 0.0, m2 = 0.0;
    bool found_m1 = false, found_m2 = false;
    
    for(const auto& p : medians) {
        cumulative += p.second;
        if(!found_m1 && cumulative >= target1) {
            m1 = p.first;
            found_m1 = true;
        }
        if(!found_m2 && cumulative >= target2) {
            m2 = p.first;
            found_m2 = true;
            break;
        }
    }
    
    if(even) {
        return (m1 + m2) / 2.0;
    } else {
        return m2;
    }
}