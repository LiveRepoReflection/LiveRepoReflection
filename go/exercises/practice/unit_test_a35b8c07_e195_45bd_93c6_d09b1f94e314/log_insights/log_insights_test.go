package log_insights

import (
	"sort"
	"sync"
	"testing"
	"time"
)

// Helper function to get current time in nanoseconds.
func now() int64 {
	return time.Now().UnixNano()
}

// TestAddAndQueryLogs validates basic log ingestion and querying by time, node, and level.
func TestAddAndQueryLogs(t *testing.T) {
	agg := NewAggregator()

	// Create several log entries.
	logs := []LogEntry{
		{Timestamp: now(), NodeID: "node-1", Level: "INFO", Message: "Service started"},
		{Timestamp: now() + 1000, NodeID: "node-1", Level: "ERROR", Message: "Failed to connect to DB"},
		{Timestamp: now() + 2000, NodeID: "node-2", Level: "WARN", Message: "High memory usage"},
		{Timestamp: now() + 3000, NodeID: "node-1", Level: "INFO", Message: "Service running"},
		{Timestamp: now() + 4000, NodeID: "node-2", Level: "ERROR", Message: "Disk error occurred"},
	}
	for _, entry := range logs {
		if err := agg.AddLog(entry); err != nil {
			t.Fatalf("AddLog error: %v", err)
		}
	}

	// Query logs for node-1 in a defined time range with levels INFO and ERROR.
	criteria := QueryCriteria{
		StartTime: logs[0].Timestamp,
		EndTime:   logs[3].Timestamp + 1000,
		NodeIDs:   []string{"node-1"},
		Levels:    []string{"INFO", "ERROR"},
		Keyword:   "",
	}
	result, err := agg.QueryLogs(criteria)
	if err != nil {
		t.Fatalf("QueryLogs error: %v", err)
	}

	// Build the expected result using the same filtering.
	var expected []LogEntry
	for _, entry := range logs {
		if entry.NodeID == "node-1" && entry.Timestamp >= criteria.StartTime && entry.Timestamp <= criteria.EndTime {
			if entry.Level == "INFO" || entry.Level == "ERROR" {
				expected = append(expected, entry)
			}
		}
	}

	if len(result) != len(expected) {
		t.Fatalf("Expected %d logs, got %d", len(expected), len(result))
	}

	// Ensure logs are returned in ascending order of timestamp.
	for i := 1; i < len(result); i++ {
		if result[i].Timestamp < result[i-1].Timestamp {
			t.Fatalf("Logs not sorted by timestamp")
		}
	}
}

// TestQueryKeywordFilter validates querying logs with a keyword filter.
func TestQueryKeywordFilter(t *testing.T) {
	agg := NewAggregator()

	logs := []LogEntry{
		{Timestamp: now(), NodeID: "node-3", Level: "INFO", Message: "Initialization complete"},
		{Timestamp: now() + 500, NodeID: "node-3", Level: "ERROR", Message: "Connection timeout"},
		{Timestamp: now() + 1000, NodeID: "node-3", Level: "WARN", Message: "Connection slow"},
		{Timestamp: now() + 1500, NodeID: "node-3", Level: "INFO", Message: "Connection restored"},
	}
	for _, entry := range logs {
		if err := agg.AddLog(entry); err != nil {
			t.Fatalf("AddLog error: %v", err)
		}
	}

	criteria := QueryCriteria{
		StartTime: logs[0].Timestamp,
		EndTime:   logs[3].Timestamp + 1000,
		NodeIDs:   []string{"node-3"},
		Levels:    []string{"INFO", "ERROR", "WARN"},
		Keyword:   "Connection",
	}
	result, err := agg.QueryLogs(criteria)
	if err != nil {
		t.Fatalf("QueryLogs error: %v", err)
	}

	// Verify that each returned log contains the keyword "Connection".
	for _, entry := range result {
		if !containsKeyword(entry.Message, "Connection") {
			t.Fatalf("Log message %q does not contain keyword 'Connection'", entry.Message)
		}
	}
}

// TestAnomalyDetection verifies that the anomaly detection correctly flags a node when error count exceeds a threshold.
func TestAnomalyDetection(t *testing.T) {
	agg := NewAggregator()

	threshold := 3
	windowSize := int64(2e9) // 2 seconds in nanoseconds
	baseTime := now()

	// Insert multiple error logs for "node-4" at intervals to simulate rapid errors.
	var entries []LogEntry
	for i := 0; i < 5; i++ {
		entries = append(entries, LogEntry{
			Timestamp: baseTime + int64(i)*300*1e6, // every 300ms
			NodeID:    "node-4",
			Level:     "ERROR",
			Message:   "Error event",
		})
	}
	for _, entry := range entries {
		if err := agg.AddLog(entry); err != nil {
			t.Fatalf("AddLog error: %v", err)
		}
	}

	anomalous, err := agg.CheckAnomaly("node-4", threshold, windowSize)
	if err != nil {
		t.Fatalf("CheckAnomaly error: %v", err)
	}
	if !anomalous {
		t.Fatalf("Anomaly not detected when expected")
	}

	// Ensure that a node with few errors does not trigger an anomaly.
	entries = []LogEntry{
		{Timestamp: baseTime, NodeID: "node-5", Level: "INFO", Message: "All good"},
		{Timestamp: baseTime + 500*1e6, NodeID: "node-5", Level: "ERROR", Message: "Minor error"},
	}
	for _, entry := range entries {
		if err := agg.AddLog(entry); err != nil {
			t.Fatalf("AddLog error: %v", err)
		}
	}

	anomalous, err = agg.CheckAnomaly("node-5", threshold, windowSize)
	if err != nil {
		t.Fatalf("CheckAnomaly error: %v", err)
	}
	if anomalous {
		t.Fatalf("Anomaly detected unexpectedly for node-5")
	}
}

// TestConcurrentLogIngestion ensures that the aggregator can handle concurrent log insertions.
func TestConcurrentLogIngestion(t *testing.T) {
	agg := NewAggregator()
	var wg sync.WaitGroup
	nodeIDs := []string{"node-1", "node-2", "node-3", "node-4", "node-5"}
	numLogsPerNode := 100
	startTime := now()

	for _, node := range nodeIDs {
		wg.Add(1)
		go func(n string) {
			defer wg.Done()
			for i := 0; i < numLogsPerNode; i++ {
				entry := LogEntry{
					Timestamp: startTime + int64(i),
					NodeID:    n,
					Level:     "INFO",
					Message:   "Concurrent log message",
				}
				if err := agg.AddLog(entry); err != nil {
					t.Errorf("AddLog error for node %s: %v", n, err)
				}
			}
		}(node)
	}
	wg.Wait()

	criteria := QueryCriteria{
		StartTime: startTime,
		EndTime:   startTime + int64(numLogsPerNode),
		NodeIDs:   nodeIDs,
		Levels:    []string{"INFO"},
		Keyword:   "",
	}
	results, err := agg.QueryLogs(criteria)
	if err != nil {
		t.Fatalf("QueryLogs error: %v", err)
	}
	expectedCount := len(nodeIDs) * numLogsPerNode
	if len(results) != expectedCount {
		t.Fatalf("Expected %d logs, got %d", expectedCount, len(results))
	}
}

// TestQuerySortOrder verifies that the logs returned from a query are sorted by timestamp.
func TestQuerySortOrder(t *testing.T) {
	agg := NewAggregator()
	logs := []LogEntry{
		{Timestamp: now() + 3000, NodeID: "node-A", Level: "INFO", Message: "Third log"},
		{Timestamp: now() + 1000, NodeID: "node-A", Level: "INFO", Message: "First log"},
		{Timestamp: now() + 2000, NodeID: "node-A", Level: "INFO", Message: "Second log"},
	}
	for _, entry := range logs {
		if err := agg.AddLog(entry); err != nil {
			t.Fatalf("AddLog error: %v", err)
		}
	}

	criteria := QueryCriteria{
		StartTime: logs[1].Timestamp,
		EndTime:   logs[0].Timestamp + 1000,
		NodeIDs:   []string{"node-A"},
		Levels:    []string{"INFO"},
		Keyword:   "",
	}
	result, err := agg.QueryLogs(criteria)
	if err != nil {
		t.Fatalf("QueryLogs error: %v", err)
	}

	// Copy and sort result to validate order.
	expected := make([]LogEntry, len(result))
	copy(expected, result)
	sort.Slice(expected, func(i, j int) bool {
		return expected[i].Timestamp < expected[j].Timestamp
	})

	for i := range result {
		if result[i].Timestamp != expected[i].Timestamp {
			t.Fatalf("Logs not returned in sorted order")
		}
	}
}

// containsKeyword checks if the given keyword exists in the message.
func containsKeyword(message, keyword string) bool {
	return indexOf(message, keyword) >= 0
}

// indexOf returns the index of substr in str, or -1 if not found.
func indexOf(str, substr string) int {
	for i := 0; i <= len(str)-len(substr); i++ {
		if str[i:i+len(substr)] == substr {
			return i
		}
	}
	return -1
}