package event_aggregate

import (
	"reflect"
	"sort"
	"testing"
)

func generateTestEvents() []Event {
	base := int64(1000000000)
	return []Event{
		{Timestamp: base + 10, Category: "payment", Value: 100, ProducerID: "p1"},
		{Timestamp: base + 20, Category: "payment", Value: 200, ProducerID: "p2"},
		{Timestamp: base + 30, Category: "login", Value: 0, ProducerID: "p1"},
		{Timestamp: base + 40, Category: "payment", Value: 50, ProducerID: "p1"},
		{Timestamp: base + 50, Category: "payment", Value: 150, ProducerID: "p2"},
		{Timestamp: base + 60, Category: "payment", Value: 300, ProducerID: "p3"},
		{Timestamp: base + 70, Category: "login", Value: 0, ProducerID: "p2"},
		{Timestamp: base + 80, Category: "error", Value: 1, ProducerID: "p4"},
		{Timestamp: base + 90, Category: "payment", Value: 120, ProducerID: "p1"},
	}
}

func TestCountEvents(t *testing.T) {
	agg := NewAggregator()
	events := generateTestEvents()
	for _, e := range events {
		agg.Ingest(e)
	}
	base := int64(1000000000)

	// Test count for "payment" over full range
	count := agg.CountEvents("payment", base, base+100)
	if count != 6 {
		t.Errorf("Expected 6 payment events, got %d", count)
	}

	// Test count for "login" within a specific time interval
	count = agg.CountEvents("login", base+30, base+80)
	if count != 2 {
		t.Errorf("Expected 2 login events, got %d", count)
	}

	// Test count for a non-existent category
	count = agg.CountEvents("nonexistent", base, base+100)
	if count != 0 {
		t.Errorf("Expected 0 events for nonexistent category, got %d", count)
	}
}

func TestSumValues(t *testing.T) {
	agg := NewAggregator()
	events := generateTestEvents()
	for _, e := range events {
		agg.Ingest(e)
	}
	base := int64(1000000000)

	// For payment events: 100 + 200 + 50 + 150 + 300 + 120 = 920
	sum := agg.SumValues("payment", base, base+100)
	if sum != 920 {
		t.Errorf("Expected sum of 920 for payment events, got %d", sum)
	}

	// For login events: 0 + 0 = 0
	sum = agg.SumValues("login", base, base+100)
	if sum != 0 {
		t.Errorf("Expected sum of 0 for login events, got %d", sum)
	}

	// For error events: 1
	sum = agg.SumValues("error", base, base+100)
	if sum != 1 {
		t.Errorf("Expected sum of 1 for error events, got %d", sum)
	}
}

func TestTopKProducers(t *testing.T) {
	agg := NewAggregator()
	events := generateTestEvents()

	// Additional events to adjust frequency counts.
	extraEvents := []Event{
		{Timestamp: 1000000010, Category: "payment", Value: 80, ProducerID: "p1"},
		{Timestamp: 1000000020, Category: "payment", Value: 60, ProducerID: "p2"},
		{Timestamp: 1000000030, Category: "payment", Value: 40, ProducerID: "p3"},
		{Timestamp: 1000000040, Category: "payment", Value: 20, ProducerID: "p1"},
	}

	for _, e := range events {
		agg.Ingest(e)
	}
	for _, e := range extraEvents {
		agg.Ingest(e)
	}

	base := int64(1000000000)
	// Expected frequencies for "payment":
	// p1: 4 events, p2: 3 events, p3: 2 events.
	topProducers := agg.TopKProducers("payment", base, base+100)
	expectedTop := []string{"p1", "p2", "p3"}
	if !reflect.DeepEqual(topProducers, expectedTop) {
		t.Errorf("Expected top producers %v, got %v", expectedTop, topProducers)
	}

	// Test with k smaller than the total number of producers.
	topTwo := agg.TopKProducers("payment", base, base+100, 2)
	expectedTopTwo := []string{"p1", "p2"}
	if !reflect.DeepEqual(topTwo, expectedTopTwo) {
		t.Errorf("Expected top 2 producers %v, got %v", expectedTopTwo, topTwo)
	}

	// Additionally, ensure the result is sorted in descending order of event count.
	countMap := make(map[string]int)
	allEvents := append(events, extraEvents...)
	for _, e := range allEvents {
		if e.Category == "payment" && e.Timestamp >= base && e.Timestamp <= base+100 {
			countMap[e.ProducerID]++
		}
	}
	sortedPairs := make([]struct {
		Producer string
		Count    int
	}, 0, len(countMap))
	for p, c := range countMap {
		sortedPairs = append(sortedPairs, struct {
			Producer string
			Count    int
		}{Producer: p, Count: c})
	}
	sort.Slice(sortedPairs, func(i, j int) bool {
		return sortedPairs[i].Count > sortedPairs[j].Count
	})
	actualOrder := make([]string, len(sortedPairs))
	for i, pair := range sortedPairs {
		actualOrder[i] = pair.Producer
	}
	if !reflect.DeepEqual(topProducers, actualOrder) {
		t.Errorf("Expected sorted producers %v, got %v", actualOrder, topProducers)
	}
}

func TestEdgeTimeBoundaries(t *testing.T) {
	agg := NewAggregator()
	base := int64(1000000000)
	events := []Event{
		{Timestamp: base, Category: "login", Value: 0, ProducerID: "p1"},
		{Timestamp: base + 50, Category: "login", Value: 0, ProducerID: "p2"},
		{Timestamp: base + 100, Category: "login", Value: 0, ProducerID: "p1"},
	}
	for _, e := range events {
		agg.Ingest(e)
	}

	// Test that events exactly on boundaries are considered.
	count := agg.CountEvents("login", base, base+100)
	if count != 3 {
		t.Errorf("Expected 3 login events on boundaries, got %d", count)
	}
}