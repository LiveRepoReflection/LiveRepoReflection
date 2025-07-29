package event_stream

import (
	"sync"
	"testing"
	"time"
)

// Assumed interface for the event stream system:
//
// func NewEventStream() *EventStream
//
// (es *EventStream) RegisterSensor(sensorID string) error
// (es *EventStream) DeregisterSensor(sensorID string) error
// (es *EventStream) SendEvent(sensorID string, timestamp int64, value float64) error
// (es *EventStream) QueryAggregation(sensorID string, windowSize int64, aggType string) (float64, error)

func TestSingleSensorOrderedProcessing(t *testing.T) {
	es := NewEventStream()
	sensorID := "sensor1"
	if err := es.RegisterSensor(sensorID); err != nil {
		t.Fatalf("failed to register sensor: %v", err)
	}

	// Send events in order: timestamp from 1 to 5 and value equal to timestamp.
	for i := int64(1); i <= 5; i++ {
		if err := es.SendEvent(sensorID, i, float64(i)); err != nil {
			t.Fatalf("failed to send event at timestamp %d: %v", i, err)
		}
	}

	// Query sum aggregation with window size sufficiently large to cover all events.
	result, err := es.QueryAggregation(sensorID, 5, "sum")
	if err != nil {
		t.Fatalf("failed to query sum aggregation: %v", err)
	}
	if result != 15 {
		t.Errorf("expected sum 15, got %f", result)
	}
}

func TestSlidingWindowAverage(t *testing.T) {
	es := NewEventStream()
	sensorID := "sensor_avg"
	if err := es.RegisterSensor(sensorID); err != nil {
		t.Fatalf("failed to register sensor: %v", err)
	}
	// Send events with distinct timestamps and corresponding values.
	events := []struct {
		ts  int64
		val float64
	}{
		{10, 10.0},
		{20, 20.0},
		{30, 30.0},
		{40, 40.0},
		{50, 50.0},
	}
	for _, e := range events {
		if err := es.SendEvent(sensorID, e.ts, e.val); err != nil {
			t.Fatalf("failed to send event: %v", err)
		}
	}
	// Query average aggregation with window size 25 seconds.
	// Latest event timestamp is 50, so the window covers events with timestamp >= 26.
	// Only events at 30, 40, and 50 should be considered.
	expectedAvg := (30.0 + 40.0 + 50.0) / 3.0
	result, err := es.QueryAggregation(sensorID, 25, "average")
	if err != nil {
		t.Fatalf("failed to query average aggregation: %v", err)
	}
	if result != expectedAvg {
		t.Errorf("expected average %f, got %f", expectedAvg, result)
	}
}

func TestSlidingWindowMaximum(t *testing.T) {
	es := NewEventStream()
	sensorID := "sensor_max"
	if err := es.RegisterSensor(sensorID); err != nil {
		t.Fatalf("failed to register sensor: %v", err)
	}
	// Send events with varying values.
	events := []struct {
		ts  int64
		val float64
	}{
		{5, 8.0},
		{10, 15.0},
		{15, 7.0},
		{20, 22.0},
		{25, 16.0},
	}
	for _, e := range events {
		if err := es.SendEvent(sensorID, e.ts, e.val); err != nil {
			t.Fatalf("failed to send event: %v", err)
		}
	}
	// Query maximum aggregation with window size 15 seconds.
	// Latest event timestamp is 25; window covers events with timestamp >= 10.
	// Maximum among events at timestamps 10, 15, 20, 25 is 22.0.
	result, err := es.QueryAggregation(sensorID, 15, "maximum")
	if err != nil {
		t.Fatalf("failed to query maximum aggregation: %v", err)
	}
	if result != 22.0 {
		t.Errorf("expected maximum 22.0, got %f", result)
	}
}

func TestDynamicSensorRegistration(t *testing.T) {
	es := NewEventStream()
	sensorID := "sensor_dynamic"
	// Attempting to send an event to an unregistered sensor should produce an error.
	if err := es.SendEvent(sensorID, 1, 10.0); err == nil {
		t.Fatalf("expected error when sending event to an unregistered sensor")
	}
	// Register the sensor dynamically.
	if err := es.RegisterSensor(sensorID); err != nil {
		t.Fatalf("failed to register sensor dynamically: %v", err)
	}
	if err := es.SendEvent(sensorID, 2, 20.0); err != nil {
		t.Fatalf("failed to send event after registration: %v", err)
	}
	// Deregister the sensor.
	if err := es.DeregisterSensor(sensorID); err != nil {
		t.Fatalf("failed to deregister sensor: %v", err)
	}
	// Sending events after deregistration should fail.
	if err := es.SendEvent(sensorID, 3, 30.0); err == nil {
		t.Fatalf("expected error when sending event to deregistered sensor")
	}
}

func TestConcurrentEventProcessing(t *testing.T) {
	es := NewEventStream()
	sensorID := "sensor_concurrent"
	if err := es.RegisterSensor(sensorID); err != nil {
		t.Fatalf("failed to register sensor: %v", err)
	}
	var wg sync.WaitGroup
	numGoroutines := 10
	eventsPerGoroutine := 50
	startTime := time.Now().Unix()

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(offset int) {
			defer wg.Done()
			for j := 0; j < eventsPerGoroutine; j++ {
				ts := startTime + int64(offset*eventsPerGoroutine+j)
				value := float64(j % 100)
				if err := es.SendEvent(sensorID, ts, value); err != nil {
					t.Errorf("error in concurrent send: %v", err)
				}
			}
		}(i)
	}
	wg.Wait()

	// Compute the expected sum.
	var expectedSum float64 = 0
	for i := 0; i < eventsPerGoroutine; i++ {
		expectedSum += float64(i)
	}
	expectedSum *= float64(numGoroutines)

	// Query sum aggregation over a window that covers all events.
	result, err := es.QueryAggregation(sensorID, int64(numGoroutines*eventsPerGoroutine), "sum")
	if err != nil {
		t.Fatalf("failed to query sum aggregation: %v", err)
	}
	if result != expectedSum {
		t.Errorf("expected sum %f, got %f", expectedSum, result)
	}
}

func TestOutOfOrderEvents(t *testing.T) {
	es := NewEventStream()
	sensorID := "sensor_out_of_order"
	if err := es.RegisterSensor(sensorID); err != nil {
		t.Fatalf("failed to register sensor: %v", err)
	}
	// Send events out-of-order.
	events := []struct {
		ts  int64
		val float64
	}{
		{10, 10.0},
		{5, 5.0},
		{15, 15.0},
	}
	for _, e := range events {
		if err := es.SendEvent(sensorID, e.ts, e.val); err != nil {
			t.Fatalf("failed to send event: %v", err)
		}
	}
	// Query sum aggregation with window size 20 seconds.
	// Latest timestamp is 15; window covers events with timestamp >= -5, effectively processing all events.
	result, err := es.QueryAggregation(sensorID, 20, "sum")
	if err != nil {
		t.Fatalf("failed to query sum aggregation: %v", err)
	}
	if result != 30.0 {
		t.Errorf("expected sum 30.0, got %f", result)
	}
}