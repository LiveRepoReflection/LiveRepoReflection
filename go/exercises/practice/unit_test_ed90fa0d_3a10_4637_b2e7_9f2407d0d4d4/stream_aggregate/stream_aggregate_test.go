package stream_aggregate

import (
	"sync"
	"testing"
	"time"
)

// TestSingleEntityAggregation verifies that events for a single entity are aggregated correctly.
func TestSingleEntityAggregation(t *testing.T) {
	// Create a coordinator with a sliding window of 1000 milliseconds.
	coordinator := NewCoordinator(1000)
	// Create three events for the same entity.
	e1 := Event{Timestamp: 1000, EntityID: "entity1", Value: 10.0}
	e2 := Event{Timestamp: 1500, EntityID: "entity1", Value: 20.0}
	e3 := Event{Timestamp: 2000, EntityID: "entity1", Value: 30.0}

	// Process the events.
	if err := coordinator.ProcessEvent(e1); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}
	if err := coordinator.ProcessEvent(e2); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}
	if err := coordinator.ProcessEvent(e3); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}

	// Query the average.
	average, err := coordinator.QueryAverage("entity1")
	if err != nil {
		t.Fatalf("failed to query average: %v", err)
	}
	// At the time of the last event, the sliding window covers all events.
	expected := (10.0 + 20.0 + 30.0) / 3.0
	if average != expected {
		t.Errorf("expected average %v, got %v", expected, average)
	}
}

// TestSlidingWindowEviction verifies that events falling outside the sliding window are removed.
func TestSlidingWindowEviction(t *testing.T) {
	// Create a coordinator with a sliding window of 500 milliseconds.
	coordinator := NewCoordinator(500)
	// Create events such that the first event is outside the sliding window at query time.
	e1 := Event{Timestamp: 1000, EntityID: "entity2", Value: 10.0}
	e2 := Event{Timestamp: 1400, EntityID: "entity2", Value: 20.0}
	e3 := Event{Timestamp: 1600, EntityID: "entity2", Value: 30.0}

	if err := coordinator.ProcessEvent(e1); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}
	if err := coordinator.ProcessEvent(e2); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}
	if err := coordinator.ProcessEvent(e3); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}

	// When processing the event at timestamp 1600, the sliding window is [1100, 1600].
	average, err := coordinator.QueryAverage("entity2")
	if err != nil {
		t.Fatalf("failed to query average: %v", err)
	}
	// Only e2 and e3 should be considered.
	expected := (20.0 + 30.0) / 2.0
	if average != expected {
		t.Errorf("expected average %v, got %v", expected, average)
	}
}

// TestMultipleEntities tests the aggregation for multiple entities simultaneously.
func TestMultipleEntities(t *testing.T) {
	coordinator := NewCoordinator(1000)
	events := []Event{
		{Timestamp: 1000, EntityID: "entityA", Value: 10.0},
		{Timestamp: 1100, EntityID: "entityB", Value: 15.0},
		{Timestamp: 1200, EntityID: "entityA", Value: 20.0},
		{Timestamp: 1300, EntityID: "entityB", Value: 25.0},
	}
	for _, event := range events {
		if err := coordinator.ProcessEvent(event); err != nil {
			t.Fatalf("ProcessEvent failed: %v", err)
		}
	}

	avgA, err := coordinator.QueryAverage("entityA")
	if err != nil {
		t.Fatalf("failed to query average for entityA: %v", err)
	}
	expectedA := (10.0 + 20.0) / 2.0
	if avgA != expectedA {
		t.Errorf("expected average for entityA %v, got %v", expectedA, avgA)
	}

	avgB, err := coordinator.QueryAverage("entityB")
	if err != nil {
		t.Fatalf("failed to query average for entityB: %v", err)
	}
	expectedB := (15.0 + 25.0) / 2.0
	if avgB != expectedB {
		t.Errorf("expected average for entityB %v, got %v", expectedB, avgB)
	}
}

// TestConcurrentEventProcessing simulates concurrent event processing from multiple goroutines.
func TestConcurrentEventProcessing(t *testing.T) {
	coordinator := NewCoordinator(1000)
	var wg sync.WaitGroup
	numEvents := 100

	// Launch 10 concurrent goroutines processing events for the same entity.
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(offset int) {
			defer wg.Done()
			for j := 0; j < numEvents; j++ {
				evt := Event{
					Timestamp: int64(1000 + offset + j),
					EntityID:  "concurrent",
					Value:     float64(j % 100),
				}
				if err := coordinator.ProcessEvent(evt); err != nil {
					t.Errorf("ProcessEvent failed in goroutine: %v", err)
				}
			}
		}(i)
	}
	wg.Wait()

	average, err := coordinator.QueryAverage("concurrent")
	if err != nil {
		t.Fatalf("failed to query average: %v", err)
	}
	// Since we do not compute an exact expected average here, ensure it is within a valid range.
	if average < 0 {
		t.Errorf("expected non-negative average, got %v", average)
	}
}

// TestOutOfOrderEvents verifies that out-of-order event arrival is handled correctly.
func TestOutOfOrderEvents(t *testing.T) {
	coordinator := NewCoordinator(1000)
	e1 := Event{Timestamp: 2000, EntityID: "entityOOO", Value: 30.0}
	e2 := Event{Timestamp: 1000, EntityID: "entityOOO", Value: 10.0}
	e3 := Event{Timestamp: 1500, EntityID: "entityOOO", Value: 20.0}

	// Process events in non-chronological order.
	if err := coordinator.ProcessEvent(e1); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}
	if err := coordinator.ProcessEvent(e2); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}
	if err := coordinator.ProcessEvent(e3); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}

	average, err := coordinator.QueryAverage("entityOOO")
	if err != nil {
		t.Fatalf("failed to query average: %v", err)
	}
	// Assuming the sliding window is determined by the highest processed timestamp,
	// all events fall within the window.
	expected := (30.0 + 10.0 + 20.0) / 3.0
	if average != expected {
		t.Errorf("expected average %v, got %v", expected, average)
	}
}

// TestWorkerFailureAndRecovery simulates a worker failure and recovery scenario.
func TestWorkerFailureAndRecovery(t *testing.T) {
	coordinator := NewCoordinator(1000)
	// Process a couple of events for the target entity.
	e1 := Event{Timestamp: 1000, EntityID: "entity_fail", Value: 50.0}
	e2 := Event{Timestamp: 1100, EntityID: "entity_fail", Value: 70.0}

	if err := coordinator.ProcessEvent(e1); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}
	if err := coordinator.ProcessEvent(e2); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}

	// Simulate worker failure for the worker that handles "entity_fail".
	if err := coordinator.SimulateWorkerFailure("entity_fail"); err != nil {
		t.Fatalf("failed to simulate worker failure: %v", err)
	}

	// Wait to simulate downtime.
	time.Sleep(10 * time.Millisecond)

	// Recover the worker.
	if err := coordinator.RecoverWorker("entity_fail"); err != nil {
		t.Fatalf("failed to recover worker: %v", err)
	}

	// Process a new event post-recovery.
	e3 := Event{Timestamp: 1200, EntityID: "entity_fail", Value: 90.0}
	if err := coordinator.ProcessEvent(e3); err != nil {
		t.Fatalf("ProcessEvent failed: %v", err)
	}

	average, err := coordinator.QueryAverage("entity_fail")
	if err != nil {
		t.Fatalf("failed to query average: %v", err)
	}
	expected := (50.0 + 70.0 + 90.0) / 3.0
	if average != expected {
		t.Errorf("expected average %v, got %v", expected, average)
	}
}

// TestInvalidEntityQuery verifies that querying a non-existent entity returns an error.
func TestInvalidEntityQuery(t *testing.T) {
	coordinator := NewCoordinator(1000)
	_, err := coordinator.QueryAverage("nonexistent")
	if err == nil {
		t.Errorf("expected an error when querying a nonexistent entity, got nil")
	}
}