package logaggregation

import (
	"sort"
	"sync"
)

// LogEntry represents a single log entry in the system
type LogEntry struct {
	Timestamp  int64
	DataCenter string
	Severity   string
	Message    string
}

// TimeIndex represents an index structure for quick time-based lookups
type TimeIndex struct {
	timestamps []int64
	entries    map[int64][]LogEntry
	mu         sync.RWMutex
}

// LogAggregator represents the main system for log aggregation
type LogAggregator struct {
	// Primary indices
	timeIndex    *TimeIndex
	severityIdx  map[string]*TimeIndex
	dcIdx        map[string]*TimeIndex
	
	// Mutex for protecting concurrent access to indices
	mu sync.RWMutex
}

// NewTimeIndex creates a new TimeIndex
func NewTimeIndex() *TimeIndex {
	return &TimeIndex{
		timestamps: make([]int64, 0),
		entries:    make(map[int64][]LogEntry),
	}
}

// NewLogAggregator creates a new instance of LogAggregator
func NewLogAggregator() *LogAggregator {
	return &LogAggregator{
		timeIndex:    NewTimeIndex(),
		severityIdx:  make(map[string]*TimeIndex),
		dcIdx:        make(map[string]*TimeIndex),
	}
}

// insertIntoTimeIndex inserts a log entry into a TimeIndex
func (ti *TimeIndex) insertIntoTimeIndex(entry LogEntry) {
	ti.mu.Lock()
	defer ti.mu.Unlock()

	// Add timestamp if it doesn't exist
	if _, exists := ti.entries[entry.Timestamp]; !exists {
		ti.timestamps = append(ti.timestamps, entry.Timestamp)
		sort.Slice(ti.timestamps, func(i, j int) bool {
			return ti.timestamps[i] < ti.timestamps[j]
		})
	}

	// Add entry to the timestamp bucket
	ti.entries[entry.Timestamp] = append(ti.entries[entry.Timestamp], entry)
}

// IngestLog ingests a new log entry into the system
func (la *LogAggregator) IngestLog(entry LogEntry) {
	la.mu.Lock()
	
	// Ensure indices exist for severity and data center
	if _, exists := la.severityIdx[entry.Severity]; !exists {
		la.severityIdx[entry.Severity] = NewTimeIndex()
	}
	if _, exists := la.dcIdx[entry.DataCenter]; !exists {
		la.dcIdx[entry.DataCenter] = NewTimeIndex()
	}
	
	la.mu.Unlock()

	// Insert into all indices
	la.timeIndex.insertIntoTimeIndex(entry)
	la.severityIdx[entry.Severity].insertIntoTimeIndex(entry)
	la.dcIdx[entry.DataCenter].insertIntoTimeIndex(entry)
}

// findEntriesInTimeRange finds all entries in a TimeIndex within the given time range
func (ti *TimeIndex) findEntriesInTimeRange(startTime, endTime int64) []LogEntry {
	ti.mu.RLock()
	defer ti.mu.RUnlock()

	var results []LogEntry

	// Binary search for start position
	startIdx := sort.Search(len(ti.timestamps), func(i int) bool {
		return ti.timestamps[i] >= startTime
	})

	// Collect all entries within range
	for i := startIdx; i < len(ti.timestamps) && ti.timestamps[i] <= endTime; i++ {
		results = append(results, ti.entries[ti.timestamps[i]]...)
	}

	return results
}

// QueryLogs queries logs based on time range and severity
func (la *LogAggregator) QueryLogs(startTime, endTime int64, severity string) map[string][]LogEntry {
	la.mu.RLock()
	severityIndex, exists := la.severityIdx[severity]
	if !exists {
		la.mu.RUnlock()
		return make(map[string][]LogEntry)
	}
	
	// Get all entries matching severity and time range
	matchingEntries := severityIndex.findEntriesInTimeRange(startTime, endTime)
	la.mu.RUnlock()

	// Group results by data center
	result := make(map[string][]LogEntry)
	for _, entry := range matchingEntries {
		result[entry.DataCenter] = append(result[entry.DataCenter], entry)
	}

	// Sort entries within each data center by timestamp
	for dc := range result {
		sort.Slice(result[dc], func(i, j int) bool {
			return result[dc][i].Timestamp < result[dc][j].Timestamp
		})
	}

	return result
}