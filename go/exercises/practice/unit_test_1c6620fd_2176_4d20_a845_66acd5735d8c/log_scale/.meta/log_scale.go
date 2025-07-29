package log_scale

import (
	"encoding/json"
	"sort"
	"strings"
	"sync"
	"time"
)

type LogEntry struct {
	Timestamp   time.Time `json:"timestamp"`
	ServiceName string    `json:"service_name"`
	LogLevel    string    `json:"log_level"`
	Message     string    `json:"message"`
	TraceID     string    `json:"trace_id"`
}

type QueryFilter struct {
	StartTime        time.Time
	EndTime          time.Time
	ServiceName      string
	LogLevel         string
	MessageSubstring string
	TraceID          string
}

var (
	logEntries []LogEntry
	mu         sync.RWMutex
)

// ResetStorage clears the current in-memory log storage.
func ResetStorage() {
	mu.Lock()
	defer mu.Unlock()
	logEntries = make([]LogEntry, 0)
}

// IngestLog takes a JSON string representing a log entry, parses it, and stores it.
func IngestLog(logData string) error {
	var temp struct {
		Timestamp   string `json:"timestamp"`
		ServiceName string `json:"service_name"`
		LogLevel    string `json:"log_level"`
		Message     string `json:"message"`
		TraceID     string `json:"trace_id"`
	}

	err := json.Unmarshal([]byte(logData), &temp)
	if err != nil {
		return err
	}

	parsedTime, err := time.Parse(time.RFC3339, temp.Timestamp)
	if err != nil {
		return err
	}

	entry := LogEntry{
		Timestamp:   parsedTime,
		ServiceName: temp.ServiceName,
		LogLevel:    temp.LogLevel,
		Message:     temp.Message,
		TraceID:     temp.TraceID,
	}

	mu.Lock()
	logEntries = append(logEntries, entry)
	mu.Unlock()

	return nil
}

// QueryLogs returns log entries that match the given filter criteria. 
// The results are sorted by Timestamp in ascending order.
func QueryLogs(filter QueryFilter) ([]LogEntry, error) {
	mu.RLock()
	defer mu.RUnlock()

	var results []LogEntry
	for _, entry := range logEntries {
		if !filter.StartTime.IsZero() && entry.Timestamp.Before(filter.StartTime) {
			continue
		}
		if !filter.EndTime.IsZero() && entry.Timestamp.After(filter.EndTime) {
			continue
		}
		if filter.ServiceName != "" && entry.ServiceName != filter.ServiceName {
			continue
		}
		if filter.LogLevel != "" && entry.LogLevel != filter.LogLevel {
			continue
		}
		if filter.MessageSubstring != "" && !strings.Contains(entry.Message, filter.MessageSubstring) {
			continue
		}
		if filter.TraceID != "" && entry.TraceID != filter.TraceID {
			continue
		}
		results = append(results, entry)
	}

	sort.Slice(results, func(i, j int) bool {
		return results[i].Timestamp.Before(results[j].Timestamp)
	})

	return results, nil
}