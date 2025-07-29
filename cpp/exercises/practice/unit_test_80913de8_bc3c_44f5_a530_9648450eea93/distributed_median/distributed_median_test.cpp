#include "catch.hpp"
#include "distributed_median.h"
#include <vector>
#include <cmath>

TEST_CASE("Empty Aggregator", "[distributed_median]") {
    DistributedMedian dm;
    // When no sensor data has been provided, we expect the median to be 0.0.
    REQUIRE(dm.get_median() == Approx(0.0).epsilon(0.001));
}

TEST_CASE("Single Node Update", "[distributed_median]") {
    DistributedMedian dm;
    // Sensor data summary: count, min, max, q1, median, q3.
    // For one sensor node, the aggregator should report the sensor's median.
    std::vector<double> sensor1 = {10, 1.0, 9.0, 3.0, 5.0, 7.0};
    dm.update(1, sensor1);
    REQUIRE(dm.get_median() == Approx(5.0).epsilon(0.001));
}

TEST_CASE("Multiple Nodes Update", "[distributed_median]") {
    DistributedMedian dm;
    // Update with first sensor node.
    std::vector<double> sensor1 = {10, 1.0, 9.0, 3.0, 5.0, 7.0};
    dm.update(1, sensor1);
    // Update with second sensor node.
    std::vector<double> sensor2 = {10, 10.0, 18.0, 12.0, 14.0, 16.0};
    dm.update(2, sensor2);
    
    // For two nodes with equal counts and medians 5.0 and 14.0, the weighted median
    // is expected to be between 5.0 and 14.0. In this test, we expect approximately (5+14)/2 = 9.5.
    double median_after_two = dm.get_median();
    REQUIRE(median_after_two == Approx(9.5).epsilon(0.05));
    
    // Update with third sensor node.
    std::vector<double> sensor3 = {5, -5.0, 5.0, -2.0, 0.0, 2.0};
    dm.update(3, sensor3);
    
    // Now, the total count = 10 + 10 + 5 = 25.
    // Sorting sensor medians: 0.0 (from sensor3, count 5), 5.0 (sensor1, count 10), 14.0 (sensor2, count 10).
    // The cumulative counts: 5, 15, and 25 respectively. Half of total is 12.5, so the median should be sensor1's median: 5.0.
    double median_after_three = dm.get_median();
    REQUIRE(median_after_three == Approx(5.0).epsilon(0.05));
}

TEST_CASE("Duplicate Node Update (Overwrite)", "[distributed_median]") {
    DistributedMedian dm;
    // Initial update from three sensor nodes.
    std::vector<double> sensor1 = {10, 1.0, 9.0, 3.0, 5.0, 7.0};
    std::vector<double> sensor2 = {10, 10.0, 18.0, 12.0, 14.0, 16.0};
    std::vector<double> sensor3 = {5, -5.0, 5.0, -2.0, 0.0, 2.0};
    dm.update(1, sensor1);
    dm.update(2, sensor2);
    dm.update(3, sensor3);
    
    // Expected median after above updates is approximately 5.0.
    REQUIRE(dm.get_median() == Approx(5.0).epsilon(0.05));
    
    // Now, sensor1 sends updated aggregated summary.
    // New summary from sensor1: count=20, medians shifted to higher values.
    std::vector<double> sensor1_updated = {20, 0.0, 20.0, 5.0, 10.0, 15.0};
    dm.update(1, sensor1_updated);
    
    // Now, the sensor summaries are:
    // Sensor1: median=10.0, count=20.
    // Sensor2: median=14.0, count=10.
    // Sensor3: median=0.0, count=5.
    // Total count = 20 + 10 + 5 = 35.
    // Sorting by sensor medians: 0.0 (count 5), 10.0 (count 20), 14.0 (count 10).
    // Cumulative counts: 5, 25, 35. Half of total = 17.5, which falls into sensor1's summary.
    // Therefore, the expected median is approximately 10.0.
    double median_after_overwrite = dm.get_median();
    REQUIRE(median_after_overwrite == Approx(10.0).epsilon(0.05));
}