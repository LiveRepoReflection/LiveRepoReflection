package event_aggregator

import (
	"sort"
	"sync"
)

// Event represents a single event in the system.
type Event struct {
	Timestamp int64
	EventType string
	EntityID  string
	Value     float64
}

// Aggregator manages event ingestion and query operations.
type Aggregator struct {
	mu   sync.RWMutex
	data map[string]map[string][]Event // eventType -> entityID -> sorted slice of Events by Timestamp.
}

// NewAggregator creates and returns a new Aggregator.
func NewAggregator() *Aggregator {
	return &Aggregator{
		data: make(map[string]map[string][]Event),
	}
}

// Ingest adds a new event into the aggregator in sorted order by Timestamp.
func (a *Aggregator) Ingest(event Event) error {
	a.mu.Lock()
	defer a.mu.Unlock()

	entities, exists := a.data[event.EventType]
	if !exists {
		entities = make(map[string][]Event)
		a.data[event.EventType] = entities
	}
	eventsSlice := entities[event.EntityID]
	// Find the correct index to insert the event so that the slice remains sorted by Timestamp.
	index := sort.Search(len(eventsSlice), func(i int) bool {
		return eventsSlice[i].Timestamp > event.Timestamp
	})
	// Insert the event into the slice at the found index.
	if index == len(eventsSlice) {
		eventsSlice = append(eventsSlice, event)
	} else {
		eventsSlice = append(eventsSlice, Event{})
		copy(eventsSlice[index+1:], eventsSlice[index:])
		eventsSlice[index] = event
	}
	entities[event.EntityID] = eventsSlice
	return nil
}

// Query returns the aggregated sum of event values for a given event type and entity ID
// within the specified time window [startTimestamp, endTimestamp].
func (a *Aggregator) Query(eventType, entityID string, startTimestamp, endTimestamp int64) (float64, error) {
	a.mu.RLock()
	defer a.mu.RUnlock()

	entities, exists := a.data[eventType]
	if !exists {
		return 0, nil
	}
	eventsSlice, exists := entities[entityID]
	if !exists {
		return 0, nil
	}
	// Find the index of the first event with Timestamp >= startTimestamp.
	lower := sort.Search(len(eventsSlice), func(i int) bool {
		return eventsSlice[i].Timestamp >= startTimestamp
	})
	// Find the index of the first event with Timestamp > endTimestamp.
	upper := sort.Search(len(eventsSlice), func(i int) bool {
		return eventsSlice[i].Timestamp > endTimestamp
	})
	var sum float64
	for i := lower; i < upper; i++ {
		sum += eventsSlice[i].Value
	}
	return sum, nil
}