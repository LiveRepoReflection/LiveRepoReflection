package event_aggregator

import (
	"sync"
	"testing"
	"time"
)

func TestAggregatorSingleEntitySingleEventType(t *testing.T) {
	agg := NewAggregator()

	now := time.Now().Unix()
	event1 := Event{
		Timestamp: now,
		EventType: "click",
		EntityID:  "entity1",
		Value:     5.0,
	}

	if err := agg.Ingest(event1); err != nil {
		t.Fatalf("Ingest failed: %v", err)
	}

	sum, err := agg.Query("click", "entity1", now, now)
	if err != nil {
		t.Fatalf("Query failed: %v", err)
	}
	if sum != 5.0 {
		t.Fatalf("Expected sum 5.0, got %v", sum)
	}
}

func TestAggregatorMultipleEvents(t *testing.T) {
	agg := NewAggregator()
	now := time.Now().Unix()

	events := []Event{
		{Timestamp: now - 10, EventType: "purchase", EntityID: "entity2", Value: 100.0},
		{Timestamp: now - 5, EventType: "purchase", EntityID: "entity2", Value: 150.0},
		{Timestamp: now, EventType: "purchase", EntityID: "entity2", Value: 200.0},
		{Timestamp: now + 5, EventType: "purchase", EntityID: "entity2", Value: 50.0},
	}

	for _, e := range events {
		if err := agg.Ingest(e); err != nil {
			t.Fatalf("Ingest failed: %v", err)
		}
	}

	sum, err := agg.Query("purchase", "entity2", now-10, now+5)
	if err != nil {
		t.Fatalf("Query failed: %v", err)
	}
	expected := 100.0 + 150.0 + 200.0 + 50.0
	if sum != expected {
		t.Fatalf("Expected sum %v, got %v", expected, sum)
	}
}

func TestAggregatorOutOfOrderEvents(t *testing.T) {
	agg := NewAggregator()
	now := time.Now().Unix()

	// Simulate out-of-order ingestion of events
	events := []Event{
		{Timestamp: now + 10, EventType: "view", EntityID: "entity3", Value: 20.0},
		{Timestamp: now, EventType: "view", EntityID: "entity3", Value: 40.0},
		{Timestamp: now + 5, EventType: "view", EntityID: "entity3", Value: 30.0},
	}

	for _, e := range events {
		if err := agg.Ingest(e); err != nil {
			t.Fatalf("Ingest failed: %v", err)
		}
	}

	sum, err := agg.Query("view", "entity3", now, now+10)
	if err != nil {
		t.Fatalf("Query failed: %v", err)
	}
	expected := 20.0 + 40.0 + 30.0
	if sum != expected {
		t.Fatalf("Expected sum %v, got %v", expected, sum)
	}
}

func TestAggregatorMultipleEntityTypes(t *testing.T) {
	agg := NewAggregator()
	now := time.Now().Unix()

	events := []Event{
		{Timestamp: now, EventType: "click", EntityID: "entity4", Value: 10.0},
		{Timestamp: now + 1, EventType: "click", EntityID: "entity4", Value: 15.0},
		{Timestamp: now, EventType: "purchase", EntityID: "entity4", Value: 100.0},
	}

	for _, e := range events {
		if err := agg.Ingest(e); err != nil {
			t.Fatalf("Ingest failed: %v", err)
		}
	}

	// Query for "click" events
	clickSum, err := agg.Query("click", "entity4", now, now+1)
	if err != nil {
		t.Fatalf("Query failed for click events: %v", err)
	}
	expectedClickSum := 10.0 + 15.0
	if clickSum != expectedClickSum {
		t.Fatalf("Expected click sum %v, got %v", expectedClickSum, clickSum)
	}

	// Query for "purchase" events
	purchaseSum, err := agg.Query("purchase", "entity4", now, now)
	if err != nil {
		t.Fatalf("Query failed for purchase events: %v", err)
	}
	if purchaseSum != 100.0 {
		t.Fatalf("Expected purchase sum 100.0, got %v", purchaseSum)
	}
}

func TestAggregatorConcurrency(t *testing.T) {
	agg := NewAggregator()
	now := time.Now().Unix()

	var wg sync.WaitGroup
	numEvents := 1000
	numGoroutines := 10

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(gID int) {
			defer wg.Done()
			for j := 0; j < numEvents; j++ {
				event := Event{
					Timestamp: now + int64(j),
					EventType: "concurrent",
					EntityID:  "entity_concurrent",
					Value:     1.0,
				}
				if err := agg.Ingest(event); err != nil {
					t.Errorf("Goroutine %d: Ingest failed: %v", gID, err)
				}
			}
		}(i)
	}

	wg.Wait()

	sum, err := agg.Query("concurrent", "entity_concurrent", now, now+int64(numEvents))
	if err != nil {
		t.Fatalf("Query failed: %v", err)
	}

	expected := float64(numGoroutines * numEvents)
	if sum != expected {
		t.Fatalf("Expected sum %v, got %v", expected, sum)
	}
}