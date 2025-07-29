#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <string>
#include <tuple>
#include <vector>
#include "catch.hpp"
#include "event_aggregator.h"

using namespace std;

// Helper struct for expected results
struct EventStats {
    int count;
    double sum;
    double average;
    double min;
    double max;
};

// Helper function to check if the results match the expected values within a tolerance
bool check_results(
    const map<string, AggregatedStats>& actual,
    const map<string, EventStats>& expected,
    double tolerance = 0.000001
) {
    if (actual.size() != expected.size()) {
        return false;
    }

    for (const auto& [event_type, expected_stats] : expected) {
        if (actual.find(event_type) == actual.end()) {
            return false;
        }

        const auto& actual_stats = actual.at(event_type);
        
        if (actual_stats.count != expected_stats.count) {
            return false;
        }
        
        if (abs(actual_stats.sum - expected_stats.sum) > tolerance) {
            return false;
        }
        
        if (abs(actual_stats.average - expected_stats.average) > tolerance) {
            return false;
        }
        
        // Handle special cases for min/max with no events
        if (expected_stats.count == 0) {
            if (!isinf(actual_stats.min) || actual_stats.min <= 0) {
                return false;
            }
            if (!isinf(actual_stats.max) || actual_stats.max >= 0) {
                return false;
            }
        } else {
            if (abs(actual_stats.min - expected_stats.min) > tolerance) {
                return false;
            }
            if (abs(actual_stats.max - expected_stats.max) > tolerance) {
                return false;
            }
        }
    }
    
    return true;
}

TEST_CASE("Basic event aggregation", "[event_aggregator]") {
    vector<EventRecord> events = {
        {1678886400, "item_purchase", 123, 10.0},
        {1678886401, "monster_kill", 456, 20.0},
        {1678886402, "item_purchase", 123, 15.0},
        {1678886403, "player_interaction", 789, 0.0},
        {1678886404, "monster_kill", 456, 25.0},
        {1678886405, "item_purchase", 123, 12.0},
    };
    int64_t window_size = 5;

    auto result = aggregate_events(events, window_size);

    map<string, EventStats> expected = {
        {"item_purchase", {3, 37.0, 37.0/3, 10.0, 15.0}},
        {"monster_kill", {2, 45.0, 22.5, 20.0, 25.0}},
        {"player_interaction", {1, 0.0, 0.0, 0.0, 0.0}}
    };

    REQUIRE(check_results(result, expected));
}

TEST_CASE("Empty input list", "[event_aggregator]") {
    vector<EventRecord> events;
    int64_t window_size = 5;

    auto result = aggregate_events(events, window_size);

    REQUIRE(result.empty());
}

TEST_CASE("Some events outside window", "[event_aggregator]") {
    vector<EventRecord> events = {
        {1678886400, "item_purchase", 123, 10.0}, // Outside window
        {1678886401, "monster_kill", 456, 20.0},  // Outside window
        {1678886405, "item_purchase", 123, 15.0}, // Inside window
        {1678886406, "player_interaction", 789, 0.0}, // Inside window
        {1678886408, "monster_kill", 456, 25.0}, // Inside window
        {1678886409, "item_purchase", 123, 12.0}, // Inside window
    };
    int64_t window_size = 5;

    auto result = aggregate_events(events, window_size);

    map<string, EventStats> expected = {
        {"item_purchase", {2, 27.0, 13.5, 12.0, 15.0}},
        {"monster_kill", {1, 25.0, 25.0, 25.0, 25.0}},
        {"player_interaction", {1, 0.0, 0.0, 0.0, 0.0}}
    };

    REQUIRE(check_results(result, expected));
}

TEST_CASE("Zero window size", "[event_aggregator]") {
    vector<EventRecord> events = {
        {1678886400, "item_purchase", 123, 10.0},
        {1678886401, "monster_kill", 456, 20.0},
    };
    int64_t window_size = 0;

    // Only the latest event should be counted with a zero window size
    auto result = aggregate_events(events, window_size);

    map<string, EventStats> expected = {
        {"monster_kill", {1, 20.0, 20.0, 20.0, 20.0}}
    };

    REQUIRE(check_results(result, expected));
}

TEST_CASE("Negative window size", "[event_aggregator]") {
    vector<EventRecord> events = {
        {1678886400, "item_purchase", 123, 10.0},
        {1678886401, "monster_kill", 456, 20.0},
    };
    int64_t window_size = -5;

    // A negative window size should be treated as if it were zero
    auto result = aggregate_events(events, window_size);

    map<string, EventStats> expected = {
        {"monster_kill", {1, 20.0, 20.0, 20.0, 20.0}}
    };

    REQUIRE(check_results(result, expected));
}

TEST_CASE("Events with identical timestamps", "[event_aggregator]") {
    vector<EventRecord> events = {
        {1678886400, "item_purchase", 123, 10.0},
        {1678886400, "item_purchase", 124, 15.0},
        {1678886400, "monster_kill", 456, 20.0},
        {1678886400, "monster_kill", 457, 25.0},
    };
    int64_t window_size = 5;

    auto result = aggregate_events(events, window_size);

    map<string, EventStats> expected = {
        {"item_purchase", {2, 25.0, 12.5, 10.0, 15.0}},
        {"monster_kill", {2, 45.0, 22.5, 20.0, 25.0}}
    };

    REQUIRE(check_results(result, expected));
}

TEST_CASE("Extreme values", "[event_aggregator]") {
    vector<EventRecord> events = {
        {1678886400, "extreme", 123, std::numeric_limits<double>::max()},
        {1678886401, "extreme", 124, std::numeric_limits<double>::min()},
        {1678886402, "extreme", 125, std::numeric_limits<double>::lowest()},
        {1678886403, "normal", 126, 1.0},
    };
    int64_t window_size = 5;

    auto result = aggregate_events(events, window_size);

    // We don't check the sum and average for extreme values due to potential overflow
    REQUIRE(result.count("extreme") == 1);
    REQUIRE(result.at("extreme").count == 3);
    REQUIRE(result.at("extreme").min == std::numeric_limits<double>::lowest());
    REQUIRE(result.at("extreme").max == std::numeric_limits<double>::max());

    map<string, EventStats> expected_normal = {
        {"normal", {1, 1.0, 1.0, 1.0, 1.0}}
    };

    // Create a new map with just the "normal" event for checking
    map<string, AggregatedStats> normal_result;
    normal_result["normal"] = result.at("normal");
    
    REQUIRE(check_results(normal_result, expected_normal));
}

TEST_CASE("Out of order events", "[event_aggregator]") {
    vector<EventRecord> events = {
        {1678886405, "item_purchase", 123, 15.0}, // 3rd chronologically
        {1678886401, "monster_kill", 456, 20.0},  // 1st chronologically
        {1678886403, "player_interaction", 789, 0.0}, // 2nd chronologically
        {1678886408, "monster_kill", 456, 25.0},  // 4th chronologically
    };
    int64_t window_size = 5;

    auto result = aggregate_events(events, window_size);

    map<string, EventStats> expected = {
        {"item_purchase", {1, 15.0, 15.0, 15.0, 15.0}},
        {"monster_kill", {1, 25.0, 25.0, 25.0, 25.0}},
        {"player_interaction", {1, 0.0, 0.0, 0.0, 0.0}}
    };

    REQUIRE(check_results(result, expected));
}

TEST_CASE("Large number of event types with varying frequencies", "[event_aggregator]") {
    vector<EventRecord> events;
    const int64_t latest_timestamp = 1678886500;
    const int num_event_types = 100;
    const int events_per_type = 100;
    
    // Create events with varying frequencies
    for (int i = 0; i < num_event_types; i++) {
        string event_type = "event_type_" + to_string(i);
        int frequency = i + 1; // Some event types occur more frequently than others
        
        for (int j = 0; j < events_per_type * frequency / num_event_types; j++) {
            int64_t timestamp = latest_timestamp - rand() % 10; // Random timestamp within 10 seconds
            int user_id = 1000 + i;
            double value = static_cast<double>(rand()) / RAND_MAX * 100.0; // Random value between 0 and 100
            
            events.push_back({timestamp, event_type, user_id, value});
        }
    }
    
    int64_t window_size = 10;
    
    // We're not checking exact values here, just making sure it completes without errors
    auto result = aggregate_events(events, window_size);
    
    REQUIRE(result.size() > 0);
    REQUIRE(result.size() <= num_event_types); // Some event types might not have events in the window
}

TEST_CASE("Performance test with large dataset", "[event_aggregator][.][performance]") {
    const int num_events = 1000000; // 1 million events
    const int64_t base_timestamp = 1678886400;
    const int64_t window_size = 3600; // 1 hour
    
    vector<EventRecord> events;
    events.reserve(num_events);
    
    // Generate random events
    srand(42); // Fixed seed for reproducibility
    for (int i = 0; i < num_events; i++) {
        int64_t timestamp = base_timestamp + rand() % 7200; // Random timestamp within 2 hours
        string event_type = "event_type_" + to_string(rand() % 100); // 100 different event types
        int user_id = rand() % 10000; // 10,000 different users
        double value = static_cast<double>(rand()) / RAND_MAX * 1000.0; // Random value between 0 and 1000
        
        events.push_back({timestamp, event_type, user_id, value});
    }
    
    // Measure execution time
    auto start = std::chrono::high_resolution_clock::now();
    auto result = aggregate_events(events, window_size);
    auto end = std::chrono::high_resolution_clock::now();
    
    std::chrono::duration<double, std::milli> duration = end - start;
    std::cout << "Performance test completed in " << duration.count() << " ms" << std::endl;
    
    // Check that we got results for all event types
    REQUIRE(result.size() > 0);
    REQUIRE(result.size() <= 100); // We should have at most 100 different event types
    
    // Check that the execution time is within our latency budget (assuming 10ms)
    // Note: This might fail on slower machines or with debug builds
    // REQUIRE(duration.count() < 10.0); // 10 milliseconds
}