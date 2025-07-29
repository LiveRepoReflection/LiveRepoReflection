package log_insights

import (
	"errors"
	"sort"
	"strings"
	"sync"
)

// LogEntry represents a log entry.
type LogEntry struct {
	Timestamp int64
	NodeID    string
	Level     string
	Message   string
}

// QueryCriteria represents the filtering criteria for querying logs.
type QueryCriteria struct {
	StartTime int64
	EndTime   int64
	NodeIDs   []string
	Levels    []string
	Keyword   string
}

// Aggregator is responsible for aggregating and querying log entries.
type Aggregator struct {
	lock sync.Mutex
	logs []LogEntry
}

// NewAggregator creates a new Aggregator instance.
func NewAggregator() *Aggregator {
	return &Aggregator{
		logs: make([]LogEntry, 0),
	}
}

// AddLog adds a new log entry to the aggregator.
func (a *Aggregator) AddLog(entry LogEntry) error {
	a.lock.Lock()
	defer a.lock.Unlock()
	a.logs = append(a.logs, entry)
	return nil
}

// QueryLogs returns all log entries that match the given QueryCriteria.
// The returned logs are sorted by timestamp in ascending order.
func (a *Aggregator) QueryLogs(criteria QueryCriteria) ([]LogEntry, error) {
	a.lock.Lock()
	defer a.lock.Unlock()
	
	result := make([]LogEntry, 0)
	nodeFilter := make(map[string]bool)
	for _, id := range criteria.NodeIDs {
		nodeFilter[id] = true
	}
	levelFilter := make(map[string]bool)
	for _, lvl := range criteria.Levels {
		levelFilter[lvl] = true
	}
	
	for _, entry := range a.logs {
		if entry.Timestamp < criteria.StartTime || entry.Timestamp > criteria.EndTime {
			continue
		}
		if len(nodeFilter) > 0 {
			if _, ok := nodeFilter[entry.NodeID]; !ok {
				continue
			}
		}
		if len(levelFilter) > 0 {
			if _, ok := levelFilter[entry.Level]; !ok {
				continue
			}
		}
		if criteria.Keyword != "" && !strings.Contains(entry.Message, criteria.Keyword) {
			continue
		}
		result = append(result, entry)
	}
	
	sort.Slice(result, func(i, j int) bool {
		return result[i].Timestamp < result[j].Timestamp
	})
	return result, nil
}

// CheckAnomaly checks if the number of ERROR logs for the given nodeID exceeds
// the threshold within any sliding window of duration windowSize (in nanoseconds).
func (a *Aggregator) CheckAnomaly(nodeID string, threshold int, windowSize int64) (bool, error) {
	if threshold <= 0 || windowSize <= 0 {
		return false, errors.New("invalid threshold or window size")
	}
	a.lock.Lock()
	defer a.lock.Unlock()
	
	errorLogs := make([]LogEntry, 0)
	for _, entry := range a.logs {
		if entry.NodeID == nodeID && entry.Level == "ERROR" {
			errorLogs = append(errorLogs, entry)
		}
	}
	
	if len(errorLogs) < threshold {
		return false, nil
	}
	
	sort.Slice(errorLogs, func(i, j int) bool {
		return errorLogs[i].Timestamp < errorLogs[j].Timestamp
	})
	
	start := 0
	for end := 0; end < len(errorLogs); end++ {
		for errorLogs[end].Timestamp-errorLogs[start].Timestamp > windowSize {
			start++
		}
		if (end - start + 1) >= threshold {
			return true, nil
		}
	}
	return false, nil
}