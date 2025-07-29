package event_aggregate

import (
	"sort"
)

type Event struct {
	Timestamp  int64  // Unix timestamp in nanoseconds
	Category   string // Event category (e.g., "payment", "login", "error")
	Value      int    // Numerical value associated with the event
	ProducerID string // Unique identifier for the producer
}

type Aggregator struct {
	events []Event
}

func NewAggregator() *Aggregator {
	return &Aggregator{
		events: make([]Event, 0),
	}
}

func (agg *Aggregator) Ingest(e Event) {
	agg.events = append(agg.events, e)
}

func (agg *Aggregator) CountEvents(category string, startTime, endTime int64) int {
	count := 0
	for _, e := range agg.events {
		if e.Category == category && e.Timestamp >= startTime && e.Timestamp <= endTime {
			count++
		}
	}
	return count
}

func (agg *Aggregator) SumValues(category string, startTime, endTime int64) int {
	sum := 0
	for _, e := range agg.events {
		if e.Category == category && e.Timestamp >= startTime && e.Timestamp <= endTime {
			sum += e.Value
		}
	}
	return sum
}

func (agg *Aggregator) TopKProducers(category string, startTime, endTime int64, k ...int) []string {
	countByProducer := make(map[string]int)
	for _, e := range agg.events {
		if e.Category == category && e.Timestamp >= startTime && e.Timestamp <= endTime {
			countByProducer[e.ProducerID]++
		}
	}

	type pair struct {
		Producer string
		Count    int
	}

	pairs := make([]pair, 0, len(countByProducer))
	for p, count := range countByProducer {
		pairs = append(pairs, pair{Producer: p, Count: count})
	}

	sort.Slice(pairs, func(i, j int) bool {
		return pairs[i].Count > pairs[j].Count
	})

	limit := len(pairs)
	if len(k) > 0 && k[0] < limit {
		limit = k[0]
	}

	result := make([]string, 0, limit)
	for i := 0; i < limit; i++ {
		result = append(result, pairs[i].Producer)
	}
	return result
}