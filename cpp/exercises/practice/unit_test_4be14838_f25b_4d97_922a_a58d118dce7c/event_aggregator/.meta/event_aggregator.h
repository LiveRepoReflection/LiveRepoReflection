#ifndef EVENT_AGGREGATOR_H
#define EVENT_AGGREGATOR_H

#include <cstdint>
#include <map>
#include <string>
#include <vector>

// Structure to represent an event record
struct EventRecord {
    int64_t timestamp;    // Unix timestamp (seconds since epoch)
    std::string event_type; // Type of event (e.g., "item_purchase")
    int32_t user_id;      // ID of the user who triggered the event
    double value;         // Numerical value associated with the event
};

// Structure to hold aggregated statistics for an event type
struct AggregatedStats {
    int count;      // Total number of events
    double sum;     // Sum of values
    double average; // Average value (sum / count)
    double min;     // Minimum value
    double max;     // Maximum value
};

// Function to aggregate event statistics within a sliding time window
std::map<std::string, AggregatedStats> aggregate_events(
    const std::vector<EventRecord>& events,
    int64_t window_size
);

#endif // EVENT_AGGREGATOR_H