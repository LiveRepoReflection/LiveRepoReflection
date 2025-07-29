package event_horizon

import (
	"sort"
	"strconv"
	"sync"
	"testing"
	"time"
)

// Assuming the following types and functions are defined in the project:
//
// type Event struct {
// 	Timestamp int64
// 	ID        string
// 	Priority  int
// 	Payload   string
// }
//
// type Store interface {
// 	Ingest(e Event) error
// 	QueryByTimestampRange(start, end int64) ([]Event, error)
// 	QueryByEventID(id string) (Event, error)
// 	DeleteByTimestampRange(start, end int64) error
// }
//
// func NewStore() Store

func TestIngestAndQueryByEventID(t *testing.T) {
	store := NewStore()
	now := time.Now().UnixNano()
	event := Event{
		Timestamp: now,
		ID:        "event1",
		Priority:  10,
		Payload:   "test event",
	}
	if err := store.Ingest(event); err != nil {
		t.Fatalf("Ingest failed: %v", err)
	}
	result, err := store.QueryByEventID("event1")
	if err != nil {
		t.Fatalf("QueryByEventID failed: %v", err)
	}
	if result.ID != "event1" || result.Payload != "test event" {
		t.Fatalf("Queried event does not match ingested event")
	}
}

func TestQueryByTimestampRange(t *testing.T) {
	store := NewStore()
	baseTime := time.Now().UnixNano()
	events := []Event{
		{Timestamp: baseTime + 100, ID: "e1", Priority: 5, Payload: "payload1"},
		{Timestamp: baseTime + 200, ID: "e2", Priority: 10, Payload: "payload2"},
		{Timestamp: baseTime + 150, ID: "e3", Priority: 10, Payload: "payload3"},
		{Timestamp: baseTime + 250, ID: "e4", Priority: 7, Payload: "payload4"},
		{Timestamp: baseTime + 300, ID: "e5", Priority: 5, Payload: "payload5"},
	}
	for _, e := range events {
		if err := store.Ingest(e); err != nil {
			t.Fatalf("Failed to ingest event %s: %v", e.ID, err)
		}
	}
	startRange := baseTime + 100
	endRange := baseTime + 250
	results, err := store.QueryByTimestampRange(startRange, endRange)
	if err != nil {
		t.Fatalf("QueryByTimestampRange failed: %v", err)
	}
	// Expected events in the range: e1, e2, e3, e4
	// Sorted by priority descending and then by timestamp ascending:
	// Among events with priority 10: e3 (timestamp baseTime+150) then e2 (timestamp baseTime+200)
	// Then e4 (priority 7) and finally e1 (priority 5)
	expectedOrder := []string{"e3", "e2", "e4", "e1"}
	if len(results) != len(expectedOrder) {
		t.Fatalf("Expected %d events, got %d", len(expectedOrder), len(results))
	}
	// Ensure sorting order: priority descending, then timestamp ascending.
	// If the store implementation uses different ordering internally, the test verifies the final ordering.
	for i, expID := range expectedOrder {
		if results[i].ID != expID {
			t.Fatalf("Order mismatch at index %d: expected %s, got %s", i, expID, results[i].ID)
		}
	}

	// Additionally, verify that the results are correctly sorted according to the required rules.
	if !isSorted(results) {
		t.Fatalf("Returned events are not sorted by priority descending and timestamp ascending for equal priorities")
	}
}

// Helper function to verify the order of events: descending Priority and for same Priority, ascending Timestamp.
func isSorted(events []Event) bool {
	return sort.SliceIsSorted(events, func(i, j int) bool {
		if events[i].Priority > events[j].Priority {
			return true
		} else if events[i].Priority < events[j].Priority {
			return false
		}
		return events[i].Timestamp < events[j].Timestamp
	})
}

func TestDeleteByTimestampRange(t *testing.T) {
	store := NewStore()
	baseTime := time.Now().UnixNano()
	events := []Event{
		{Timestamp: baseTime + 100, ID: "d1", Priority: 3, Payload: "del1"},
		{Timestamp: baseTime + 200, ID: "d2", Priority: 4, Payload: "del2"},
		{Timestamp: baseTime + 300, ID: "d3", Priority: 5, Payload: "del3"},
	}
	for _, e := range events {
		if err := store.Ingest(e); err != nil {
			t.Fatalf("Failed to ingest event %s: %v", e.ID, err)
		}
	}
	// Delete events with timestamp between baseTime+150 and baseTime+350 (inclusive)
	if err := store.DeleteByTimestampRange(baseTime+150, baseTime+350); err != nil {
		t.Fatalf("DeleteByTimestampRange failed: %v", err)
	}
	_, err := store.QueryByEventID("d2")
	if err == nil {
		t.Fatalf("Expected error for deleted event d2, got none")
	}
	_, err = store.QueryByEventID("d3")
	if err == nil {
		t.Fatalf("Expected error for deleted event d3, got none")
	}
	event, err := store.QueryByEventID("d1")
	if err != nil {
		t.Fatalf("QueryByEventID for d1 failed: %v", err)
	}
	if event.ID != "d1" {
		t.Fatalf("Unexpected event returned for d1")
	}
}

func TestDuplicateEventIDOverwrites(t *testing.T) {
	store := NewStore()
	baseTime := time.Now().UnixNano()
	event1 := Event{Timestamp: baseTime + 100, ID: "dup", Priority: 1, Payload: "first"}
	event2 := Event{Timestamp: baseTime + 200, ID: "dup", Priority: 5, Payload: "second"}
	if err := store.Ingest(event1); err != nil {
		t.Fatalf("Ingest failed: %v", err)
	}
	if err := store.Ingest(event2); err != nil {
		t.Fatalf("Ingest (duplicate) failed: %v", err)
	}
	result, err := store.QueryByEventID("dup")
	if err != nil {
		t.Fatalf("QueryByEventID failed: %v", err)
	}
	if result.Payload != "second" || result.Priority != 5 || result.Timestamp != event2.Timestamp {
		t.Fatalf("Event was not overwritten correctly")
	}
}

func TestConcurrentIngestions(t *testing.T) {
	store := NewStore()
	var wg sync.WaitGroup
	baseTime := time.Now().UnixNano()
	numEvents := 1000
	for i := 0; i < numEvents; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			event := Event{
				Timestamp: baseTime + int64(i),
				ID:        "concurrent_" + strconv.Itoa(i),
				Priority:  i % 10,
				Payload:   "payload_" + strconv.Itoa(i),
			}
			if err := store.Ingest(event); err != nil {
				t.Errorf("Concurrent Ingest failed for event %d: %v", i, err)
			}
		}(i)
	}
	wg.Wait()
	results, err := store.QueryByTimestampRange(baseTime, baseTime+int64(numEvents))
	if err != nil {
		t.Fatalf("QueryByTimestampRange after concurrent ingestions failed: %v", err)
	}
	if len(results) != numEvents {
		t.Fatalf("Expected %d events after concurrent ingestion, found %d", numEvents, len(results))
	}
}

func TestEmptyQuery(t *testing.T) {
	store := NewStore()
	baseTime := time.Now().UnixNano()
	results, err := store.QueryByTimestampRange(baseTime, baseTime+1000)
	if err != nil {
		t.Fatalf("QueryByTimestampRange failed: %v", err)
	}
	if len(results) != 0 {
		t.Fatalf("Expected 0 events for empty query, got %d", len(results))
	}
}