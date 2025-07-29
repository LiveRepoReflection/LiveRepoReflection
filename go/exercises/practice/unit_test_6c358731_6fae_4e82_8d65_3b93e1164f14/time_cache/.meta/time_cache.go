package time_cache

import (
	"sort"
	"sync"
)

type timeEntry struct {
	value     string
	timestamp int
}

type TimeCache struct {
	mu      sync.RWMutex
	data    map[string][]timeEntry
	entries []timeEntryWithKey
	size    int
}

type timeEntryWithKey struct {
	key       string
	value     string
	timestamp int
}

func NewTimeCache() *TimeCache {
	return &TimeCache{
		data: make(map[string][]timeEntry),
	}
}

func (tc *TimeCache) Set(key string, value string, timestamp int) {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	entry := timeEntry{value: value, timestamp: timestamp}
	tc.data[key] = append(tc.data[key], entry)
	tc.entries = append(tc.entries, timeEntryWithKey{
		key:       key,
		value:     value,
		timestamp: timestamp,
	})
	tc.size += len(key) + len(value)
}

func (tc *TimeCache) Get(key string, timestamp int) string {
	tc.mu.RLock()
	defer tc.mu.RUnlock()

	entries, exists := tc.data[key]
	if !exists {
		return ""
	}

	idx := sort.Search(len(entries), func(i int) bool {
		return entries[i].timestamp > timestamp
	})

	if idx == 0 {
		return ""
	}
	return entries[idx-1].value
}

func (tc *TimeCache) Count(key string, startTimestamp int, endTimestamp int) int {
	tc.mu.RLock()
	defer tc.mu.RUnlock()

	entries, exists := tc.data[key]
	if !exists {
		return 0
	}

	startIdx := sort.Search(len(entries), func(i int) bool {
		return entries[i].timestamp >= startTimestamp
	})

	endIdx := sort.Search(len(entries), func(i int) bool {
		return entries[i].timestamp > endTimestamp
	})

	return endIdx - startIdx
}

func (tc *TimeCache) Evict(maxSize int) {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	if tc.size <= maxSize {
		return
	}

	sort.Slice(tc.entries, func(i, j int) bool {
		return tc.entries[i].timestamp < tc.entries[j].timestamp
	})

	for tc.size > maxSize && len(tc.entries) > 0 {
		entry := tc.entries[0]
		tc.entries = tc.entries[1:]

		entries := tc.data[entry.key]
		for i, e := range entries {
			if e.timestamp == entry.timestamp && e.value == entry.value {
				tc.data[entry.key] = append(entries[:i], entries[i+1:]...)
				if len(tc.data[entry.key]) == 0 {
					delete(tc.data, entry.key)
				}
				break
			}
		}

		tc.size -= len(entry.key) + len(entry.value)
	}
}