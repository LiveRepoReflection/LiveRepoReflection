# Event Aggregator

This project implements an efficient event stream aggregation system that processes real-time event data and provides statistical aggregations within a sliding time window. The system is designed to handle high-volume event streams with low latency.

## Solution Overview

The solution uses a custom data structure called `SlidingWindowTracker` to efficiently track and aggregate events within a sliding time window. The implementation has the following key features:

1. **Efficient Event Storage**: Events are stored in a sorted multimap for each event type, which allows for efficient insertion, deletion, and traversal based on timestamp.

2. **Automatic Window Management**: The system automatically manages the sliding window by removing expired events as new events are processed.

3. **Statistical Aggregations**: For each event type, the system maintains running counts, sums, minimums, and maximums, which are used to compute statistical aggregations.

4. **Handling Out-of-Order Events**: The system properly handles events that arrive out of order, as long as they fall within the current window.

## Time and Space Complexity

- **Time Complexity**:
  - Adding an event: O(log n) per event, where n is the number of events of that type in the window
  - Removing expired events: O(m * log n), where m is the number of event types and n is the average number of events per type
  - Computing aggregated stats: O(m), where m is the number of event types

- **Space Complexity**: O(W), where W is the total number of events in the window across all event types

## Optimizations

1. **Lazy Min/Max Recalculation**: When removing expired events, min and max values are recalculated only when necessary.

2. **Event Filtering**: Events outside the current window are immediately filtered out without being processed.

3. **Memory Efficiency**: Event types with no events in the current window are automatically removed from the tracking data structures.

## Potential Scaling Strategies

The system could be scaled horizontally by:

1. **Sharding by Event Type**: Different servers could handle different event types.

2. **Time-Based Partitioning**: Events could be partitioned based on their timestamp, with different servers handling different time ranges.

3. **Distributed Aggregation**: A map-reduce approach could be used to distribute the aggregation work across multiple machines.