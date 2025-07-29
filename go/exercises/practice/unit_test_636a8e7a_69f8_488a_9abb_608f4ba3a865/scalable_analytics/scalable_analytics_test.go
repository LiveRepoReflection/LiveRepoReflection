package scalable_analytics_test

import (
	"math"
	"reflect"
	"sort"
	"testing"

	"scalable_analytics"
)

const floatEpsilon = 1e-6

func floatsAlmostEqual(a, b float64) bool {
	return math.Abs(a-b) < floatEpsilon
}

func TestAggregateEvents(t *testing.T) {
	// Build events for "cpu_usage" aggregation.
	events := []scalable_analytics.Event{
		{Timestamp: 100, NodeID: "node1", Metric: "cpu_usage", Value: 10},
		{Timestamp: 150, NodeID: "node1", Metric: "cpu_usage", Value: 20},
		{Timestamp: 120, NodeID: "node2", Metric: "cpu_usage", Value: 30},
		{Timestamp: 180, NodeID: "node2", Metric: "cpu_usage", Value: 40},
		// Event outside the time window.
		{Timestamp: 300, NodeID: "node1", Metric: "cpu_usage", Value: 50},
	}
	start, end := int64(50), int64(200)
	results, err := scalable_analytics.AggregateEvents(events, "cpu_usage", start, end)
	if err != nil {
		t.Fatalf("AggregateEvents returned error: %v", err)
	}
	expected := map[string]scalable_analytics.AggregationResult{
		"node1": {
			Count:   2,
			Sum:     30,
			Average: 15,
			Min:     10,
			Max:     20,
			StdDev:  5,
		},
		"node2": {
			Count:   2,
			Sum:     70,
			Average: 35,
			Min:     30,
			Max:     40,
			StdDev:  5,
		},
	}
	if len(results) != len(expected) {
		t.Fatalf("Expected results for %d nodes, got %d", len(expected), len(results))
	}
	for node, expAgg := range expected {
		resAgg, ok := results[node]
		if !ok {
			t.Errorf("Missing aggregation for node %s", node)
			continue
		}
		if resAgg.Count != expAgg.Count {
			t.Errorf("Node %s: expected count %d, got %d", node, expAgg.Count, resAgg.Count)
		}
		if !floatsAlmostEqual(resAgg.Sum, expAgg.Sum) {
			t.Errorf("Node %s: expected sum %f, got %f", node, expAgg.Sum, resAgg.Sum)
		}
		if !floatsAlmostEqual(resAgg.Average, expAgg.Average) {
			t.Errorf("Node %s: expected average %f, got %f", node, expAgg.Average, resAgg.Average)
		}
		if !floatsAlmostEqual(resAgg.Min, expAgg.Min) {
			t.Errorf("Node %s: expected min %f, got %f", node, expAgg.Min, resAgg.Min)
		}
		if !floatsAlmostEqual(resAgg.Max, expAgg.Max) {
			t.Errorf("Node %s: expected max %f, got %f", node, expAgg.Max, resAgg.Max)
		}
		if !floatsAlmostEqual(resAgg.StdDev, expAgg.StdDev) {
			t.Errorf("Node %s: expected stddev %f, got %f", node, expAgg.StdDev, resAgg.StdDev)
		}
	}
}

func TestGetTopKAnomalies(t *testing.T) {
	// Build events for "memory_usage" anomaly detection.
	// In this test, we assume one event per node at two different timestamps.
	events := []scalable_analytics.Event{
		// At timestamp 200.
		{Timestamp: 200, NodeID: "node1", Metric: "memory_usage", Value: 10},
		{Timestamp: 200, NodeID: "node2", Metric: "memory_usage", Value: 20},
		{Timestamp: 200, NodeID: "node3", Metric: "memory_usage", Value: 30},
		// At timestamp 250.
		{Timestamp: 250, NodeID: "node1", Metric: "memory_usage", Value: 15},
		{Timestamp: 250, NodeID: "node2", Metric: "memory_usage", Value: 15},
		{Timestamp: 250, NodeID: "node3", Metric: "memory_usage", Value: 15},
	}
	start, end := int64(100), int64(300)
	// For timestamp 200, the median is 20 resulting in anomaly scores:
	// node1: |10-20| = 10, node2: |20-20| = 0, node3: |30-20| = 10.
	// For timestamp 250, the median is 15 so anomaly scores are 0 for all nodes.
	// The final average anomaly scores over the two timestamps are:
	// node1: 10/2 = 5, node2: 0, node3: 10/2 = 5.
	k := 2
	nodes, err := scalable_analytics.GetTopKAnomalies(events, "memory_usage", start, end, k)
	if err != nil {
		t.Fatalf("GetTopKAnomalies returned error: %v", err)
	}
	expectedNodes := []string{"node1", "node3"}
	sort.Strings(nodes)
	sort.Strings(expectedNodes)
	if !reflect.DeepEqual(nodes, expectedNodes) {
		t.Errorf("Expected top k nodes %v, got %v", expectedNodes, nodes)
	}
}

func TestComputeCorrelation(t *testing.T) {
	// Build events for correlation between "cpu_usage" and "disk_io".
	// For node1, use a perfect positive correlation.
	// For node2, use a perfect negative correlation.
	events := []scalable_analytics.Event{
		// Node1: positive correlation.
		{Timestamp: 300, NodeID: "node1", Metric: "cpu_usage", Value: 10},
		{Timestamp: 300, NodeID: "node1", Metric: "disk_io", Value: 100},
		{Timestamp: 350, NodeID: "node1", Metric: "cpu_usage", Value: 20},
		{Timestamp: 350, NodeID: "node1", Metric: "disk_io", Value: 200},
		{Timestamp: 400, NodeID: "node1", Metric: "cpu_usage", Value: 30},
		{Timestamp: 400, NodeID: "node1", Metric: "disk_io", Value: 300},
		// Node2: negative correlation.
		{Timestamp: 300, NodeID: "node2", Metric: "cpu_usage", Value: 10},
		{Timestamp: 300, NodeID: "node2", Metric: "disk_io", Value: 300},
		{Timestamp: 350, NodeID: "node2", Metric: "cpu_usage", Value: 20},
		{Timestamp: 350, NodeID: "node2", Metric: "disk_io", Value: 200},
		{Timestamp: 400, NodeID: "node2", Metric: "cpu_usage", Value: 30},
		{Timestamp: 400, NodeID: "node2", Metric: "disk_io", Value: 100},
	}
	start, end := int64(250), int64(450)
	correlations, err := scalable_analytics.ComputeCorrelation(events, "cpu_usage", "disk_io", start, end)
	if err != nil {
		t.Fatalf("ComputeCorrelation returned error: %v", err)
	}
	// Expect correlation 1 for node1 and -1 for node2, within epsilon.
	corr1, ok := correlations["node1"]
	if !ok {
		t.Errorf("Missing correlation result for node1")
	} else if !floatsAlmostEqual(corr1, 1) {
		t.Errorf("Expected correlation 1 for node1, got %f", corr1)
	}
	corr2, ok := correlations["node2"]
	if !ok {
		t.Errorf("Missing correlation result for node2")
	} else if !floatsAlmostEqual(corr2, -1) {
		t.Errorf("Expected correlation -1 for node2, got %f", corr2)
	}
}

func TestErrorHandling(t *testing.T) {
	// Test error handling for empty event input.
	_, err := scalable_analytics.AggregateEvents([]scalable_analytics.Event{}, "cpu_usage", 0, 100)
	if err == nil {
		t.Errorf("Expected error for AggregateEvents with empty input, got nil")
	}

	_, err = scalable_analytics.GetTopKAnomalies([]scalable_analytics.Event{}, "memory_usage", 0, 100, 3)
	if err == nil {
		t.Errorf("Expected error for GetTopKAnomalies with empty input, got nil")
	}

	_, err = scalable_analytics.ComputeCorrelation([]scalable_analytics.Event{}, "cpu_usage", "disk_io", 0, 100)
	if err == nil {
		t.Errorf("Expected error for ComputeCorrelation with empty input, got nil")
	}
}