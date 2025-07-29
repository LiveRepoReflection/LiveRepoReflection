package distributed_logs_test

import (
	"reflect"
	"sort"
	"testing"
	"time"

	"distributed_logs"
)

func TestAddAndQueryLogs(t *testing.T) {
	agg := distributed_logs.NewAggregator()

	now := time.Now().UnixNano()
	logs := []distributed_logs.LogEntry{
		{Timestamp: now + 300, Severity: distributed_logs.INFO, Message: "Log 300"},
		{Timestamp: now + 100, Severity: distributed_logs.DEBUG, Message: "Log 100"},
		{Timestamp: now + 200, Severity: distributed_logs.WARN, Message: "Log 200"},
		{Timestamp: now + 400, Severity: distributed_logs.ERROR, Message: "Log 400"},
	}

	for _, log := range logs {
		err := agg.AddLog(log)
		if err != nil {
			t.Fatalf("failed to add log: %v", err)
		}
	}

	queriedLogs, err := agg.QueryLogs(now, now+500, "")
	if err != nil {
		t.Fatalf("QueryLogs failed: %v", err)
	}

	if len(queriedLogs) != 4 {
		t.Fatalf("expected 4 logs, got %d", len(queriedLogs))
	}

	expectedTimestamps := []int64{now + 100, now + 200, now + 300, now + 400}
	for i, log := range queriedLogs {
		if log.Timestamp != expectedTimestamps[i] {
			t.Errorf("expected timestamp %d at index %d, got %d", expectedTimestamps[i], i, log.Timestamp)
		}
	}
}

func TestQueryBySeverity(t *testing.T) {
	agg := distributed_logs.NewAggregator()

	now := time.Now().UnixNano()
	logs := []distributed_logs.LogEntry{
		{Timestamp: now + 100, Severity: distributed_logs.DEBUG, Message: "Debug log"},
		{Timestamp: now + 200, Severity: distributed_logs.INFO, Message: "Info log"},
		{Timestamp: now + 300, Severity: distributed_logs.WARN, Message: "Warn log"},
		{Timestamp: now + 400, Severity: distributed_logs.ERROR, Message: "Error log"},
	}

	for _, log := range logs {
		err := agg.AddLog(log)
		if err != nil {
			t.Fatalf("failed to add log: %v", err)
		}
	}

	queriedLogs, err := agg.QueryLogs(now, now+500, distributed_logs.INFO)
	if err != nil {
		t.Fatalf("QueryLogs failed: %v", err)
	}

	expected := []distributed_logs.LogEntry{
		logs[1], logs[2], logs[3],
	}

	if !reflect.DeepEqual(queriedLogs, expected) {
		t.Errorf("expected logs %v, got %v", expected, queriedLogs)
	}
}

func TestTimeRangeFiltering(t *testing.T) {
	agg := distributed_logs.NewAggregator()

	now := time.Now().UnixNano()
	logs := []distributed_logs.LogEntry{
		{Timestamp: now + 50, Severity: distributed_logs.INFO, Message: "Before range"},
		{Timestamp: now + 150, Severity: distributed_logs.INFO, Message: "Within range 1"},
		{Timestamp: now + 250, Severity: distributed_logs.INFO, Message: "Within range 2"},
		{Timestamp: now + 350, Severity: distributed_logs.INFO, Message: "After range"},
	}

	for _, log := range logs {
		err := agg.AddLog(log)
		if err != nil {
			t.Fatalf("failed to add log: %v", err)
		}
	}

	queriedLogs, err := agg.QueryLogs(now+100, now+300, distributed_logs.INFO)
	if err != nil {
		t.Fatalf("QueryLogs failed: %v", err)
	}

	expected := []distributed_logs.LogEntry{
		logs[1], logs[2],
	}

	if !reflect.DeepEqual(queriedLogs, expected) {
		t.Errorf("expected logs %v, got %v", expected, queriedLogs)
	}
}

func TestDuplicateLogsHandling(t *testing.T) {
	agg := distributed_logs.NewAggregator()

	now := time.Now().UnixNano()
	logEntry := distributed_logs.LogEntry{
		Timestamp: now + 100,
		Severity:  distributed_logs.INFO,
		Message:   "Duplicate log",
	}

	err := agg.AddLog(logEntry)
	if err != nil {
		t.Fatalf("failed to add log first time: %v", err)
	}
	err = agg.AddLog(logEntry)
	if err != nil {
		t.Fatalf("failed to add duplicate log: %v", err)
	}

	queriedLogs, err := agg.QueryLogs(now, now+200, "")
	if err != nil {
		t.Fatalf("QueryLogs failed: %v", err)
	}

	if len(queriedLogs) != 1 {
		t.Errorf("expected 1 unique log, got %d", len(queriedLogs))
	}
}

func TestConcurrentLogAddition(t *testing.T) {
	agg := distributed_logs.NewAggregator()

	now := time.Now().UnixNano()
	const numLogs = 1000
	done := make(chan struct{})
	for i := 0; i < numLogs; i++ {
		go func(i int) {
			logEntry := distributed_logs.LogEntry{
				Timestamp: now + int64(i),
				Severity:  distributed_logs.INFO,
				Message:   "Concurrent log",
			}
			err := agg.AddLog(logEntry)
			if err != nil {
				t.Errorf("failed to add log concurrently: %v", err)
			}
			done <- struct{}{}
		}(i)
	}

	for i := 0; i < numLogs; i++ {
		<-done
	}

	queriedLogs, err := agg.QueryLogs(now, now+int64(numLogs), distributed_logs.INFO)
	if err != nil {
		t.Fatalf("QueryLogs failed: %v", err)
	}

	if len(queriedLogs) != numLogs {
		t.Errorf("expected %d logs, got %d", numLogs, len(queriedLogs))
	}

	sortedLogs := make([]int64, len(queriedLogs))
	for i, log := range queriedLogs {
		sortedLogs[i] = log.Timestamp
	}

	if !sort.SliceIsSorted(sortedLogs, func(i, j int) bool { return sortedLogs[i] < sortedLogs[j] }) {
		t.Errorf("logs are not in sorted order by timestamp")
	}
}

func TestExponentialBackoffRetry(t *testing.T) {
	agg := distributed_logs.NewAggregator()

	agg.SetTransientFailure(true)

	now := time.Now().UnixNano()
	logEntry := distributed_logs.LogEntry{
		Timestamp: now + 100,
		Severity:  distributed_logs.INFO,
		Message:   "Retry log",
	}

	err := agg.AddLog(logEntry)
	if err != nil {
		t.Fatalf("failed to add log with transient failure: %v", err)
	}

	queriedLogs, err := agg.QueryLogs(now, now+200, "")
	if err != nil {
		t.Fatalf("QueryLogs failed: %v", err)
	}

	found := false
	for _, l := range queriedLogs {
		if l.Message == "Retry log" {
			found = true
			break
		}
	}

	if !found {
		t.Errorf("log entry not found despite retries")
	}

	agg.SetTransientFailure(false)
}

func TestSystemConfiguration(t *testing.T) {
	agg := distributed_logs.NewAggregator()

	config := distributed_logs.Config{
		ProducerCount:   5,
		CollectorCount:  2,
		AggregatorCount: 1,
		LogRate:         100,
	}
	err := agg.UpdateConfig(config)
	if err != nil {
		t.Fatalf("failed to update configuration: %v", err)
	}

	newConfig := agg.GetConfig()
	if !reflect.DeepEqual(config, newConfig) {
		t.Errorf("expected config %v, got %v", config, newConfig)
	}
}