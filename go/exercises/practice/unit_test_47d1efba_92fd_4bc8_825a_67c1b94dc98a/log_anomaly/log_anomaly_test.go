package log_anomaly

import (
	"testing"
	"time"
)

func TestLogIngestion(t *testing.T) {
	storage := NewDistributedStorage()
	ingestor := NewLogIngestor(storage)

	testCases := []struct {
		name      string
		logEntry  LogEntry
		wantError bool
	}{
		{
			name: "valid log entry",
			logEntry: LogEntry{
				Timestamp:   time.Now().UnixNano(),
				ServiceName: "payment-service",
				LogLevel:    "ERROR",
				Message:     "Failed to process payment",
			},
			wantError: false,
		},
		{
			name: "invalid timestamp",
			logEntry: LogEntry{
				Timestamp:   -1,
				ServiceName: "order-service",
				LogLevel:    "INFO",
				Message:     "Invalid timestamp",
			},
			wantError: true,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			err := ingestor.Ingest(tc.logEntry)
			if (err != nil) != tc.wantError {
				t.Errorf("Ingest() error = %v, wantError %v", err, tc.wantError)
			}
		})
	}
}

func TestStorageRetrieval(t *testing.T) {
	storage := NewDistributedStorage()
	now := time.Now()

	// Populate with test data
	logs := []LogEntry{
		{
			Timestamp:   now.Add(-5 * time.Minute).UnixNano(),
			ServiceName: "inventory-service",
			LogLevel:    "ERROR",
			Message:     "Stock update failed",
		},
		{
			Timestamp:   now.Add(-2 * time.Minute).UnixNano(),
			ServiceName: "inventory-service",
			LogLevel:    "WARN",
			Message:     "Low stock warning",
		},
	}

	for _, log := range logs {
		storage.Store(log)
	}

	t.Run("retrieve by service name", func(t *testing.T) {
		results, err := storage.Retrieve("inventory-service", now.Add(-10*time.Minute), now)
		if err != nil {
			t.Fatalf("Retrieve() error = %v", err)
		}
		if len(results) != 2 {
			t.Errorf("Expected 2 logs, got %d", len(results))
		}
	})

	t.Run("retrieve with time range", func(t *testing.T) {
		results, err := storage.Retrieve("inventory-service", now.Add(-3*time.Minute), now)
		if err != nil {
			t.Fatalf("Retrieve() error = %v", err)
		}
		if len(results) != 1 {
			t.Errorf("Expected 1 log, got %d", len(results))
		}
	})
}

func TestAnomalyDetection(t *testing.T) {
	detector := NewAnomalyDetector(5, 2) // window=5, threshold=2

	testCases := []struct {
		name     string
		logs     []LogEntry
		expected bool
	}{
		{
			name: "normal operation",
			logs: []LogEntry{
				{ServiceName: "auth-service", LogLevel: "INFO"},
				{ServiceName: "auth-service", LogLevel: "INFO"},
				{ServiceName: "auth-service", LogLevel: "WARN"},
			},
			expected: false,
		},
		{
			name: "anomaly detected",
			logs: []LogEntry{
				{ServiceName: "auth-service", LogLevel: "ERROR"},
				{ServiceName: "auth-service", LogLevel: "INFO"},
				{ServiceName: "auth-service", LogLevel: "ERROR"},
				{ServiceName: "auth-service", LogLevel: "ERROR"},
			},
			expected: true,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			for _, log := range tc.logs {
				detector.AddLog(log)
			}
			result := detector.CheckAnomaly("auth-service")
			if result != tc.expected {
				t.Errorf("CheckAnomaly() = %v, want %v", result, tc.expected)
			}
			detector.Reset() // Clear state between test cases
		})
	}
}

func TestConcurrentIngestion(t *testing.T) {
	storage := NewDistributedStorage()
	ingestor := NewLogIngestor(storage)

	concurrency := 1000
	done := make(chan bool)
	errChan := make(chan error)

	for i := 0; i < concurrency; i++ {
		go func(id int) {
			log := LogEntry{
				Timestamp:   time.Now().UnixNano(),
				ServiceName: "test-service",
				LogLevel:    "INFO",
				Message:     "Concurrent test",
			}
			err := ingestor.Ingest(log)
			if err != nil {
				errChan <- err
				return
			}
			done <- true
		}(i)
	}

	for i := 0; i < concurrency; i++ {
		select {
		case <-done:
		case err := <-errChan:
			t.Fatalf("Concurrent ingestion failed: %v", err)
		}
	}

	// Verify all logs were stored
	logs, err := storage.Retrieve("test-service", time.Now().Add(-1*time.Minute), time.Now())
	if err != nil {
		t.Fatalf("Retrieve failed: %v", err)
	}
	if len(logs) != concurrency {
		t.Errorf("Expected %d logs, got %d", concurrency, len(logs))
	}
}