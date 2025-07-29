package log_scale_test

import (
	"encoding/json"
	"sync"
	"testing"
	"time"

	"log_scale"
)

// ResetStorage is a helper that clears any persisted logs.
// It assumes that the log_scale package provides a ResetStorage function.
func clearStorage() {
	log_scale.ResetStorage()
}

// createLogEntry creates a JSON string for a log entry from the given parameters.
func createLogEntry(timestamp, serviceName, logLevel, message, traceID string) string {
	entry := map[string]string{
		"timestamp":    timestamp,
		"service_name": serviceName,
		"log_level":    logLevel,
		"message":      message,
		"trace_id":     traceID,
	}
	data, _ := json.Marshal(entry)
	return string(data)
}

func TestIngestValidLog(t *testing.T) {
	clearStorage()
	logEntry := createLogEntry("2024-01-01T12:00:00Z", "serviceA", "INFO", "Request processed successfully", "a1b2c3d4e5f6")
	err := log_scale.IngestLog(logEntry)
	if err != nil {
		t.Fatalf("expected nil error, got %v", err)
	}
	filter := log_scale.QueryFilter{}
	results, err := log_scale.QueryLogs(filter)
	if err != nil {
		t.Fatalf("query error: %v", err)
	}
	if len(results) != 1 {
		t.Fatalf("expected 1 log, got %d", len(results))
	}
}

func TestIngestInvalidLog(t *testing.T) {
	clearStorage()
	// Malformed JSON
	invalidLog := `{"timestamp": "2024-01-01T12:00:00Z", "service_name": "serviceA",`
	err := log_scale.IngestLog(invalidLog)
	if err == nil {
		t.Fatalf("expected error for malformed log entry, got nil")
	}
}

func TestQueryByTimestamp(t *testing.T) {
	clearStorage()
	entries := []struct {
		timestamp   string
		serviceName string
		logLevel    string
		message     string
		traceID     string
	}{
		{"2024-01-01T10:00:00Z", "serviceA", "INFO", "Log 1", "trace1"},
		{"2024-01-01T11:00:00Z", "serviceB", "ERROR", "Log 2", "trace2"},
		{"2024-01-01T12:00:00Z", "serviceA", "DEBUG", "Log 3", "trace3"},
	}
	for _, e := range entries {
		logEntry := createLogEntry(e.timestamp, e.serviceName, e.logLevel, e.message, e.traceID)
		err := log_scale.IngestLog(logEntry)
		if err != nil {
			t.Fatalf("failed to ingest log: %v", err)
		}
	}
	startTime, err := time.Parse(time.RFC3339, "2024-01-01T10:30:00Z")
	if err != nil {
		t.Fatalf("failed to parse time: %v", err)
	}
	endTime, err := time.Parse(time.RFC3339, "2024-01-01T12:00:00Z")
	if err != nil {
		t.Fatalf("failed to parse time: %v", err)
	}
	filter := log_scale.QueryFilter{
		StartTime: startTime,
		EndTime:   endTime,
	}
	results, err := log_scale.QueryLogs(filter)
	if err != nil {
		t.Fatalf("query error: %v", err)
	}
	if len(results) != 2 {
		t.Fatalf("expected 2 logs in the time range, got %d", len(results))
	}
}

func TestQueryByServiceName(t *testing.T) {
	clearStorage()
	entries := []struct {
		timestamp   string
		serviceName string
		logLevel    string
		message     string
		traceID     string
	}{
		{"2024-01-02T09:00:00Z", "serviceA", "INFO", "Start service", "traceA1"},
		{"2024-01-02T09:05:00Z", "serviceB", "WARN", "Service warning", "traceB1"},
		{"2024-01-02T09:10:00Z", "serviceA", "DEBUG", "Service debug", "traceA2"},
	}
	for _, e := range entries {
		logEntry := createLogEntry(e.timestamp, e.serviceName, e.logLevel, e.message, e.traceID)
		err := log_scale.IngestLog(logEntry)
		if err != nil {
			t.Fatalf("failed to ingest log: %v", err)
		}
	}
	filter := log_scale.QueryFilter{
		ServiceName: "serviceA",
	}
	results, err := log_scale.QueryLogs(filter)
	if err != nil {
		t.Fatalf("query error: %v", err)
	}
	if len(results) != 2 {
		t.Fatalf("expected 2 logs for serviceA, got %d", len(results))
	}
}

func TestQueryByLogLevel(t *testing.T) {
	clearStorage()
	entries := []struct {
		timestamp   string
		serviceName string
		logLevel    string
		message     string
		traceID     string
	}{
		{"2024-01-03T08:00:00Z", "serviceC", "ERROR", "Error occurred", "traceC1"},
		{"2024-01-03T08:05:00Z", "serviceC", "INFO", "Informational", "traceC2"},
		{"2024-01-03T08:10:00Z", "serviceC", "ERROR", "Another error", "traceC3"},
	}
	for _, e := range entries {
		logEntry := createLogEntry(e.timestamp, e.serviceName, e.logLevel, e.message, e.traceID)
		err := log_scale.IngestLog(logEntry)
		if err != nil {
			t.Fatalf("failed to ingest log: %v", err)
		}
	}
	filter := log_scale.QueryFilter{
		LogLevel: "ERROR",
	}
	results, err := log_scale.QueryLogs(filter)
	if err != nil {
		t.Fatalf("query error: %v", err)
	}
	if len(results) != 2 {
		t.Fatalf("expected 2 ERROR logs, got %d", len(results))
	}
}

func TestQueryByMessageSubstring(t *testing.T) {
	clearStorage()
	entries := []struct {
		timestamp   string
		serviceName string
		logLevel    string
		message     string
		traceID     string
	}{
		{"2024-01-04T07:00:00Z", "serviceD", "INFO", "User login succeeded", "traceD1"},
		{"2024-01-04T07:05:00Z", "serviceD", "INFO", "User logout completed", "traceD2"},
		{"2024-01-04T07:10:00Z", "serviceD", "INFO", "Password change succeeded", "traceD3"},
	}
	for _, e := range entries {
		logEntry := createLogEntry(e.timestamp, e.serviceName, e.logLevel, e.message, e.traceID)
		err := log_scale.IngestLog(logEntry)
		if err != nil {
			t.Fatalf("failed to ingest log: %v", err)
		}
	}
	filter := log_scale.QueryFilter{
		MessageSubstring: "succeeded",
	}
	results, err := log_scale.QueryLogs(filter)
	if err != nil {
		t.Fatalf("query error: %v", err)
	}
	if len(results) != 2 {
		t.Fatalf("expected 2 logs containing 'succeeded', got %d", len(results))
	}
}

func TestQueryByTraceID(t *testing.T) {
	clearStorage()
	entries := []struct {
		timestamp   string
		serviceName string
		logLevel    string
		message     string
		traceID     string
	}{
		{"2024-01-05T06:00:00Z", "serviceE", "DEBUG", "Initialization complete", "uniqueTrace1"},
		{"2024-01-05T06:05:00Z", "serviceE", "DEBUG", "Initialization failed", "uniqueTrace2"},
	}
	for _, e := range entries {
		logEntry := createLogEntry(e.timestamp, e.serviceName, e.logLevel, e.message, e.traceID)
		err := log_scale.IngestLog(logEntry)
		if err != nil {
			t.Fatalf("failed to ingest log: %v", err)
		}
	}
	filter := log_scale.QueryFilter{
		TraceID: "uniqueTrace2",
	}
	results, err := log_scale.QueryLogs(filter)
	if err != nil {
		t.Fatalf("query error: %v", err)
	}
	if len(results) != 1 {
		t.Fatalf("expected 1 log with trace ID 'uniqueTrace2', got %d", len(results))
	}
}

func TestOrderedQuery(t *testing.T) {
	clearStorage()
	entries := []struct {
		timestamp   string
		serviceName string
		logLevel    string
		message     string
		traceID     string
	}{
		{"2024-01-06T05:00:00Z", "serviceF", "INFO", "First log", "traceF1"},
		{"2024-01-06T05:01:00Z", "serviceF", "INFO", "Second log", "traceF2"},
		{"2024-01-06T05:02:00Z", "serviceF", "INFO", "Third log", "traceF3"},
	}
	for _, e := range entries {
		logEntry := createLogEntry(e.timestamp, e.serviceName, e.logLevel, e.message, e.traceID)
		err := log_scale.IngestLog(logEntry)
		if err != nil {
			t.Fatalf("failed to ingest log: %v", err)
		}
	}
	filter := log_scale.QueryFilter{
		ServiceName: "serviceF",
	}
	results, err := log_scale.QueryLogs(filter)
	if err != nil {
		t.Fatalf("query error: %v", err)
	}
	if len(results) != 3 {
		t.Fatalf("expected 3 logs for serviceF, got %d", len(results))
	}
	previousTime := results[0].Timestamp
	for i := 1; i < len(results); i++ {
		if results[i].Timestamp.Before(previousTime) {
			t.Fatalf("logs are not ordered by timestamp")
		}
		previousTime = results[i].Timestamp
	}
}

func TestConcurrentIngestion(t *testing.T) {
	clearStorage()
	var wg sync.WaitGroup
	totalEntries := 100
	for i := 0; i < totalEntries; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			timestamp := time.Date(2024, 1, 7, 8, i, 0, 0, time.UTC).Format(time.RFC3339)
			logEntry := createLogEntry(timestamp, "serviceConcurrent", "INFO", "Concurrent log", "trace-concurrent")
			err := log_scale.IngestLog(logEntry)
			if err != nil {
				t.Errorf("failed to ingest log concurrently: %v", err)
			}
		}(i)
	}
	wg.Wait()
	filter := log_scale.QueryFilter{
		ServiceName: "serviceConcurrent",
	}
	results, err := log_scale.QueryLogs(filter)
	if err != nil {
		t.Fatalf("query error: %v", err)
	}
	if len(results) != totalEntries {
		t.Fatalf("expected %d concurrent logs, got %d", totalEntries, len(results))
	}
}