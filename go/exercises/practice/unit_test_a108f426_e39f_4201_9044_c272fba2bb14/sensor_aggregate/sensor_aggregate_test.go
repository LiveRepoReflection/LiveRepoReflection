package sensor_aggregate

import (
	"reflect"
	"testing"
)

func TestCoordinatorWorkerIntegration(t *testing.T) {
	// Define a time window using Unix timestamps.
	windowStart := int64(100)
	windowEnd := int64(200)

	// Initialize the coordinator and two worker nodes.
	coordinator := NewCoordinator(windowStart, windowEnd)
	worker1 := NewWorker("worker1", windowStart, windowEnd)
	worker2 := NewWorker("worker2", windowStart, windowEnd)

	// Worker1 processes sensor1 data within the window.
	if err := worker1.ProcessSensorData("sensor1", 110, map[string]int{"temp": 10, "pressure": 5}); err != nil {
		t.Fatalf("worker1 unexpected error: %v", err)
	}
	if err := worker1.ProcessSensorData("sensor1", 115, map[string]int{"temp": 5}); err != nil {
		t.Fatalf("worker1 unexpected error: %v", err)
	}

	// Worker2 processes out-of-order sensor2 data.
	if err := worker2.ProcessSensorData("sensor2", 105, map[string]int{"temp": 8, "humidity": 3}); err != nil {
		t.Fatalf("worker2 unexpected error: %v", err)
	}
	// Data outside the window should be ignored.
	if err := worker2.ProcessSensorData("sensor2", 205, map[string]int{"temp": 20}); err != nil {
		t.Fatalf("worker2 unexpected error: %v", err)
	}

	// Workers send their partial aggregations.
	agg1 := worker1.SendAggregation()
	agg2 := worker2.SendAggregation()

	// Coordinator receives partial results.
	coordinator.ReceivePartialAggregation(agg1)
	coordinator.ReceivePartialAggregation(agg2)

	// Expected global aggregation:
	// temp: 10 + 5 (worker1) + 8 (worker2) = 23
	// pressure: 5 (worker1)
	// humidity: 3 (worker2)
	expected := map[string]int{
		"temp":     23,
		"pressure": 5,
		"humidity": 3,
	}

	result := coordinator.GetAggregation()
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("TestCoordinatorWorkerIntegration: expected aggregation %v, got %v", expected, result)
	}
}

func TestLateDataWithinWindow(t *testing.T) {
	windowStart := int64(100)
	windowEnd := int64(200)

	coordinator := NewCoordinator(windowStart, windowEnd)
	worker := NewWorker("worker", windowStart, windowEnd)

	// Process normal data.
	if err := worker.ProcessSensorData("sensor1", 120, map[string]int{"metricA": 10}); err != nil {
		t.Fatalf("unexpected error on normal data: %v", err)
	}

	// Process late-arriving data (but still within the window).
	if err := worker.ProcessSensorData("sensor1", 105, map[string]int{"metricA": 5}); err != nil {
		t.Fatalf("unexpected error on late data: %v", err)
	}

	agg := worker.SendAggregation()
	coordinator.ReceivePartialAggregation(agg)

	expected := map[string]int{
		"metricA": 15,
	}

	result := coordinator.GetAggregation()
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("TestLateDataWithinWindow: expected %v, got %v", expected, result)
	}
}

func TestDataOutsideWindow(t *testing.T) {
	windowStart := int64(100)
	windowEnd := int64(200)

	coordinator := NewCoordinator(windowStart, windowEnd)
	worker := NewWorker("worker", windowStart, windowEnd)

	// Data before the window.
	if err := worker.ProcessSensorData("sensor1", 90, map[string]int{"metricB": 10}); err != nil {
		t.Fatalf("unexpected error for pre-window data: %v", err)
	}

	// Data after the window.
	if err := worker.ProcessSensorData("sensor1", 210, map[string]int{"metricB": 20}); err != nil {
		t.Fatalf("unexpected error for post-window data: %v", err)
	}

	// Process valid data within the window.
	if err := worker.ProcessSensorData("sensor1", 150, map[string]int{"metricB": 5}); err != nil {
		t.Fatalf("unexpected error for valid data: %v", err)
	}

	agg := worker.SendAggregation()
	coordinator.ReceivePartialAggregation(agg)

	expected := map[string]int{
		"metricB": 5,
	}

	result := coordinator.GetAggregation()
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("TestDataOutsideWindow: expected aggregation %v, got %v", expected, result)
	}
}

func TestMultipleMetrics(t *testing.T) {
	windowStart := int64(100)
	windowEnd := int64(200)

	coordinator := NewCoordinator(windowStart, windowEnd)
	worker := NewWorker("worker", windowStart, windowEnd)

	// Process data containing multiple metrics.
	if err := worker.ProcessSensorData("sensor1", 130, map[string]int{"m1": 3, "m2": 7}); err != nil {
		t.Fatalf("unexpected error on sensor1 data: %v", err)
	}
	if err := worker.ProcessSensorData("sensor2", 140, map[string]int{"m1": 2, "m3": 10}); err != nil {
		t.Fatalf("unexpected error on sensor2 data: %v", err)
	}
	if err := worker.ProcessSensorData("sensor1", 145, map[string]int{"m2": 3, "m3": 5}); err != nil {
		t.Fatalf("unexpected error on additional sensor1 data: %v", err)
	}

	agg := worker.SendAggregation()
	coordinator.ReceivePartialAggregation(agg)

	expected := map[string]int{
		"m1": 5,
		"m2": 10,
		"m3": 15,
	}

	result := coordinator.GetAggregation()
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("TestMultipleMetrics: expected %v, got %v", expected, result)
	}
}

func TestEmptyAggregation(t *testing.T) {
	windowStart := int64(100)
	windowEnd := int64(200)

	coordinator := NewCoordinator(windowStart, windowEnd)
	worker := NewWorker("worker", windowStart, windowEnd)

	// No sensor data is processed.
	agg := worker.SendAggregation()
	coordinator.ReceivePartialAggregation(agg)

	expected := map[string]int{}
	result := coordinator.GetAggregation()
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("TestEmptyAggregation: expected empty aggregation %v, got %v", expected, result)
	}
}