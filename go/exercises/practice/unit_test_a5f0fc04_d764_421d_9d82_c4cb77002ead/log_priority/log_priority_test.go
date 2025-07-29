package logpriority

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

// Test basic functionality with single-threaded operations
func TestBasicFunctionality(t *testing.T) {
	aggregator := NewLogAggregator()

	// Ingest some events
	aggregator.Ingest(LogEvent{
		Timestamp: 1000,
		Severity:  "ERROR",
		Message:   "Database connection failed",
		Origin:    "db-server-1",
	})

	aggregator.Ingest(LogEvent{
		Timestamp: 1001,
		Severity:  "INFO",
		Message:   "User logged in",
		Origin:    "web-server-1",
	})

	aggregator.Ingest(LogEvent{
		Timestamp: 1002,
		Severity:  "CRITICAL",
		Message:   "System crash",
		Origin:    "app-server-1",
	})

	// Get top 2 events
	topEvents := aggregator.GetTopN(2)

	// Should have 2 events
	if len(topEvents) != 2 {
		t.Errorf("Expected 2 events, got %d", len(topEvents))
	}

	// First event should be CRITICAL
	if topEvents[0].Severity != "CRITICAL" {
		t.Errorf("Expected CRITICAL severity for top event, got %s", topEvents[0].Severity)
	}

	// Second event should be ERROR
	if topEvents[1].Severity != "ERROR" {
		t.Errorf("Expected ERROR severity for second event, got %s", topEvents[1].Severity)
	}
}

// Test ordering by severity
func TestOrderBySeverity(t *testing.T) {
	aggregator := NewLogAggregator()

	// Add events in reverse order of severity
	severities := []string{"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
	for i, severity := range severities {
		aggregator.Ingest(LogEvent{
			Timestamp: int64(1000 + i),
			Severity:  severity,
			Message:   fmt.Sprintf("Message with %s severity", severity),
			Origin:    "server-1",
		})
	}

	// Get all events
	topEvents := aggregator.GetTopN(5)

	// Check order is by severity (reversed)
	for i, severity := range []string{"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"} {
		if i >= len(topEvents) {
			t.Fatalf("Expected 5 events, got %d", len(topEvents))
		}
		if topEvents[i].Severity != severity {
			t.Errorf("Expected severity %s at position %d, got %s", severity, i, topEvents[i].Severity)
		}
	}
}

// Test ordering by timestamp within same severity
func TestOrderByTimestamp(t *testing.T) {
	aggregator := NewLogAggregator()

	// Add events with same severity but different timestamps
	for i := 0; i < 5; i++ {
		aggregator.Ingest(LogEvent{
			Timestamp: int64(1000 - i), // Decreasing timestamps
			Severity:  "ERROR",
			Message:   fmt.Sprintf("Error message %d", i),
			Origin:    "server-1",
		})
	}

	// Get all events
	topEvents := aggregator.GetTopN(5)

	// Check order is by timestamp (newest first)
	var lastTimestamp int64 = 1001 // Higher than any we added
	for i, event := range topEvents {
		if event.Timestamp > lastTimestamp {
			t.Errorf("Event at position %d has timestamp %d, which is greater than previous timestamp %d",
				i, event.Timestamp, lastTimestamp)
		}
		lastTimestamp = event.Timestamp
	}
}

// Test ordering by origin event count for same severity and timestamp
func TestOrderByOriginCount(t *testing.T) {
	aggregator := NewLogAggregator()

	// Add many events from origin1
	for i := 0; i < 5; i++ {
		aggregator.Ingest(LogEvent{
			Timestamp: 1000,
			Severity:  "INFO",
			Message:   fmt.Sprintf("Info from origin1 %d", i),
			Origin:    "origin1",
		})
	}

	// Add fewer events from origin2
	for i := 0; i < 3; i++ {
		aggregator.Ingest(LogEvent{
			Timestamp: 1000,
			Severity:  "INFO",
			Message:   fmt.Sprintf("Info from origin2 %d", i),
			Origin:    "origin2",
		})
	}

	// Add events with same severity and timestamp for testing
	aggregator.Ingest(LogEvent{
		Timestamp: 1001,
		Severity:  "ERROR",
		Message:   "Test message from origin1",
		Origin:    "origin1",
	})

	aggregator.Ingest(LogEvent{
		Timestamp: 1001,
		Severity:  "ERROR",
		Message:   "Test message from origin2",
		Origin:    "origin2",
	})

	// Get top events
	topEvents := aggregator.GetTopN(2)

	// Find the ERROR severity events
	var errorEvents []LogEvent
	for _, event := range topEvents {
		if event.Severity == "ERROR" && event.Timestamp == 1001 {
			errorEvents = append(errorEvents, event)
		}
	}

	// We should have found ERROR events
	if len(errorEvents) < 2 {
		t.Fatalf("Expected to find at least 2 ERROR events, found %d", len(errorEvents))
	}

	// The origin1 event should come before origin2 because it has more total events
	if errorEvents[0].Origin != "origin1" || errorEvents[1].Origin != "origin2" {
		t.Errorf("Expected origin1 (5 events) to be prioritized over origin2 (3 events)")
	}
}

// Test concurrent ingestion
func TestConcurrentIngestion(t *testing.T) {
	aggregator := NewLogAggregator()
	const numGoroutines = 10
	const eventsPerGoroutine = 100

	var wg sync.WaitGroup
	wg.Add(numGoroutines)

	for g := 0; g < numGoroutines; g++ {
		go func(goroutineID int) {
			defer wg.Done()
			for i := 0; i < eventsPerGoroutine; i++ {
				// Mix of severities
				severity := "INFO"
				if i%5 == 0 {
					severity = "ERROR"
				} else if i%7 == 0 {
					severity = "CRITICAL"
				}

				aggregator.Ingest(LogEvent{
					Timestamp: time.Now().Unix(),
					Severity:  severity,
					Message:   fmt.Sprintf("Message %d from goroutine %d", i, goroutineID),
					Origin:    fmt.Sprintf("origin-%d", goroutineID),
				})
			}
		}(g)
	}

	// Wait for all goroutines to finish
	wg.Wait()

	// Verify we can get events after concurrent ingestion
	topEvents := aggregator.GetTopN(10)
	if len(topEvents) == 0 {
		t.Error("Expected to get some events after concurrent ingestion, got none")
	}

	// We should have received at least the right number of events
	allEvents := aggregator.GetTopN(numGoroutines * eventsPerGoroutine)
	if len(allEvents) != numGoroutines*eventsPerGoroutine {
		t.Errorf("Expected %d total events, got %d", numGoroutines*eventsPerGoroutine, len(allEvents))
	}
}

// Test edge cases
func TestEdgeCases(t *testing.T) {
	aggregator := NewLogAggregator()

	// Test GetTopN with no events
	emptyResult := aggregator.GetTopN(10)
	if len(emptyResult) != 0 {
		t.Errorf("Expected empty result for GetTopN on empty aggregator, got %d events", len(emptyResult))
	}

	// Test GetTopN with n=0
	zeroResult := aggregator.GetTopN(0)
	if len(zeroResult) != 0 {
		t.Errorf("Expected empty result for GetTopN(0), got %d events", len(zeroResult))
	}

	// Add one event
	aggregator.Ingest(LogEvent{
		Timestamp: 1000,
		Severity:  "INFO",
		Message:   "Single event",
		Origin:    "origin1",
	})

	// Test GetTopN with n larger than available events
	largeNResult := aggregator.GetTopN(100)
	if len(largeNResult) != 1 {
		t.Errorf("Expected 1 event when requesting more than available, got %d", len(largeNResult))
	}

	// Test with invalid severity (implementation-dependent behavior)
	// This test assumes that your implementation will handle invalid severities gracefully
	aggregator.Ingest(LogEvent{
		Timestamp: 1001,
		Severity:  "INVALID_SEVERITY",
		Message:   "Event with invalid severity",
		Origin:    "origin1",
	})

	// We should still be able to get events after an invalid severity
	events := aggregator.GetTopN(10)
	if len(events) == 0 {
		t.Error("Expected to get events after ingesting invalid severity, got none")
	}
}

// Test performance with large dataset
func TestPerformance(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance test in short mode")
	}

	aggregator := NewLogAggregator()
	const numEvents = 100000
	const numOrigins = 1000

	// Insert a large number of events
	for i := 0; i < numEvents; i++ {
		// Distribute severities
		severity := "INFO"
		if i%10 == 0 {
			severity = "WARNING"
		} else if i%100 == 0 {
			severity = "ERROR"
		} else if i%1000 == 0 {
			severity = "CRITICAL"
		}

		aggregator.Ingest(LogEvent{
			Timestamp: int64(i),
			Severity:  severity,
			Message:   fmt.Sprintf("Message %d", i),
			Origin:    fmt.Sprintf("origin-%d", i%numOrigins),
		})
	}

	// Measure time to get top events
	start := time.Now()
	topEvents := aggregator.GetTopN(100)
	duration := time.Since(start)

	// Log performance info
	t.Logf("GetTopN(100) for %d events took %v", numEvents, duration)
	t.Logf("Got %d events", len(topEvents))

	// Basic validation that we got something reasonable
	if len(topEvents) != 100 {
		t.Errorf("Expected 100 events, got %d", len(topEvents))
	}
}

// Test for consistency with repeated calls to GetTopN
func TestConsistency(t *testing.T) {
	aggregator := NewLogAggregator()

	// Insert some events
	for i := 0; i < 100; i++ {
		severity := "INFO"
		if i%10 == 0 {
			severity = "ERROR"
		}

		aggregator.Ingest(LogEvent{
			Timestamp: int64(i),
			Severity:  severity,
			Message:   fmt.Sprintf("Message %d", i),
			Origin:    fmt.Sprintf("origin-%d", i%10),
		})
	}

	// Get top events multiple times
	results1 := aggregator.GetTopN(50)
	results2 := aggregator.GetTopN(50)

	// Results should be consistent
	if len(results1) != len(results2) {
		t.Errorf("Inconsistent result lengths: %d vs %d", len(results1), len(results2))
	}

	for i := 0; i < len(results1); i++ {
		if results1[i].Timestamp != results2[i].Timestamp ||
			results1[i].Severity != results2[i].Severity ||
			results1[i].Origin != results2[i].Origin {
			t.Errorf("Inconsistent results at position %d", i)
			break
		}
	}
}