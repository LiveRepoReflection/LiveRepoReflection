#include "event_aggregator.h"
#include <algorithm>
#include <limits>
#include <unordered_map>
#include <map>
#include <vector>
#include <deque>
#include <cmath>

using namespace std;

// Custom comparator for the event ring buffer
struct EventComparator {
    bool operator()(const EventRecord& a, const EventRecord& b) const {
        return a.timestamp < b.timestamp;
    }
};

// Efficient data structure for tracking events in a sliding window
class SlidingWindowTracker {
private:
    struct EventTypeStats {
        int count = 0;
        double sum = 0.0;
        double min = std::numeric_limits<double>::infinity();
        double max = -std::numeric_limits<double>::infinity();
        // We use a multimap to efficiently maintain events sorted by timestamp
        // and to handle removing events as they expire from the window
        multimap<int64_t, double> events;
    };

    unordered_map<string, EventTypeStats> stats;
    int64_t window_size;
    int64_t latest_timestamp = 0;

public:
    SlidingWindowTracker(int64_t window_size) : window_size(window_size) {}

    // Add a new event to the tracker
    void add_event(const EventRecord& event) {
        latest_timestamp = max(latest_timestamp, event.timestamp);
        
        // Update the event type stats
        auto& type_stats = stats[event.event_type];
        type_stats.count++;
        type_stats.sum += event.value;
        type_stats.min = min(type_stats.min, event.value);
        type_stats.max = max(type_stats.max, event.value);
        
        // Add to the events map
        type_stats.events.insert({event.timestamp, event.value});
    }

    // Remove expired events from all trackers
    void remove_expired_events() {
        int64_t cutoff_timestamp = latest_timestamp - (window_size > 0 ? window_size : 0);
        
        for (auto it = stats.begin(); it != stats.end(); ) {
            auto& type_stats = it->second;
            
            // Remove all events with timestamps before the cutoff
            auto events_it = type_stats.events.begin();
            while (events_it != type_stats.events.end() && events_it->first < cutoff_timestamp) {
                type_stats.count--;
                type_stats.sum -= events_it->second;
                events_it = type_stats.events.erase(events_it);
            }
            
            // If there are no more events of this type, remove the tracker
            if (type_stats.count == 0) {
                it = stats.erase(it);
            } else {
                // If there are still events, recalculate min and max
                // This is more efficient than maintaining a heap for min/max
                // when the number of events per type is relatively small
                type_stats.min = std::numeric_limits<double>::infinity();
                type_stats.max = -std::numeric_limits<double>::infinity();
                
                for (const auto& [_, value] : type_stats.events) {
                    type_stats.min = min(type_stats.min, value);
                    type_stats.max = max(type_stats.max, value);
                }
                
                ++it;
            }
        }
    }

    // Get the aggregated stats for all event types
    map<string, AggregatedStats> get_aggregated_stats() const {
        map<string, AggregatedStats> result;
        
        for (const auto& [event_type, type_stats] : stats) {
            AggregatedStats agg_stats;
            agg_stats.count = type_stats.count;
            agg_stats.sum = type_stats.sum;
            agg_stats.average = type_stats.count > 0 ? type_stats.sum / type_stats.count : 0.0;
            agg_stats.min = type_stats.min;
            agg_stats.max = type_stats.max;
            
            result[event_type] = agg_stats;
        }
        
        return result;
    }
};

map<string, AggregatedStats> aggregate_events(
    const vector<EventRecord>& events,
    int64_t window_size
) {
    if (events.empty()) {
        return {};
    }

    // Ensure window_size is non-negative
    window_size = max(window_size, int64_t(0));
    
    // Find the latest timestamp to establish the window end
    int64_t latest_timestamp = events[0].timestamp;
    for (const auto& event : events) {
        latest_timestamp = max(latest_timestamp, event.timestamp);
    }
    
    // Create and initialize the sliding window tracker
    SlidingWindowTracker tracker(window_size);
    
    // Process all events
    for (const auto& event : events) {
        // Only process events within the window
        if (event.timestamp >= latest_timestamp - window_size) {
            tracker.add_event(event);
        }
    }
    
    // Remove any expired events (this shouldn't be necessary but ensures consistency)
    tracker.remove_expired_events();
    
    // Return the aggregated stats
    return tracker.get_aggregated_stats();
}