package timekeystore

import (
    "sort"
    "sync"
)

// TimeMap represents the time-based key-value store
type TimeMap struct {
    store map[string][]timeValue
    mu    sync.RWMutex
}

// timeValue represents a value with its timestamp
type timeValue struct {
    timestamp int
    value     string
}

// Constructor initializes the TimeMap
func Constructor() TimeMap {
    return TimeMap{
        store: make(map[string][]timeValue),
    }
}

// Set stores the key-value pair at the given timestamp
func (tm *TimeMap) Set(key string, value string, timestamp int) {
    tm.mu.Lock()
    defer tm.mu.Unlock()

    if _, exists := tm.store[key]; !exists {
        tm.store[key] = make([]timeValue, 0)
    }

    // Since timestamps are strictly increasing, we can append
    tm.store[key] = append(tm.store[key], timeValue{
        timestamp: timestamp,
        value:     value,
    })
}

// Get retrieves the value for the given key at or before the given timestamp
func (tm *TimeMap) Get(key string, timestamp int) string {
    tm.mu.RLock()
    defer tm.mu.RUnlock()

    values, exists := tm.store[key]
    if !exists || len(values) == 0 {
        return ""
    }

    // Binary search to find the latest value before or at the timestamp
    idx := sort.Search(len(values), func(i int) bool {
        return values[i].timestamp > timestamp
    })

    if idx == 0 {
        return ""
    }

    return values[idx-1].value
}

// For testing and debugging purposes
func (tm *TimeMap) getValues(key string) []timeValue {
    tm.mu.RLock()
    defer tm.mu.RUnlock()

    if values, exists := tm.store[key]; exists {
        result := make([]timeValue, len(values))
        copy(result, values)
        return result
    }
    return nil
}