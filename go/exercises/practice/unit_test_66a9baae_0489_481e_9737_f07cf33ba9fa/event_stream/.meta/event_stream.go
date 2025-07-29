package event_stream

import (
	"errors"
	"sort"
	"sync"
)

type event struct {
	ts    int64
	value float64
}

type sensor struct {
	id     string
	events []event
	latest int64
	mu     sync.Mutex
}

type EventStream struct {
	sensors map[string]*sensor
	mu      sync.RWMutex
}

// NewEventStream creates a new instance of EventStream.
func NewEventStream() *EventStream {
	return &EventStream{
		sensors: make(map[string]*sensor),
	}
}

// RegisterSensor adds a new sensor to the system.
func (es *EventStream) RegisterSensor(sensorID string) error {
	es.mu.Lock()
	defer es.mu.Unlock()
	if _, exists := es.sensors[sensorID]; exists {
		return errors.New("sensor already registered")
	}
	es.sensors[sensorID] = &sensor{
		id:     sensorID,
		events: make([]event, 0),
		latest: 0,
	}
	return nil
}

// DeregisterSensor removes a sensor from the system.
func (es *EventStream) DeregisterSensor(sensorID string) error {
	es.mu.Lock()
	defer es.mu.Unlock()
	if _, exists := es.sensors[sensorID]; !exists {
		return errors.New("sensor not found")
	}
	delete(es.sensors, sensorID)
	return nil
}

// SendEvent sends an event for a specific sensor.
// It returns an error if the sensor is not registered.
func (es *EventStream) SendEvent(sensorID string, timestamp int64, value float64) error {
	es.mu.RLock()
	s, exists := es.sensors[sensorID]
	es.mu.RUnlock()
	if !exists {
		return errors.New("sensor not registered")
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	// Append the event. Since events can arrive out-of-order, we will sort them when needed.
	s.events = append(s.events, event{ts: timestamp, value: value})
	// Update latest timestamp if this event is newer.
	if timestamp > s.latest {
		s.latest = timestamp
	}
	return nil
}

// QueryAggregation queries the sliding window aggregation for a sensor.
// windowSize is in seconds. The aggregation is computed over all events with timestamp >= threshold.
// The threshold is defined as latestTimestamp - windowSize for "sum", "average", and "maximum" aggregations.
func (es *EventStream) QueryAggregation(sensorID string, windowSize int64, aggType string) (float64, error) {
	es.mu.RLock()
	s, exists := es.sensors[sensorID]
	es.mu.RUnlock()
	if !exists {
		return 0, errors.New("sensor not registered")
	}

	s.mu.Lock()
	// Copy events to avoid holding lock during sort if events slice is large.
	eventsCopy := make([]event, len(s.events))
	copy(eventsCopy, s.events)
	// Determine threshold based on latest event timestamp.
	threshold := s.latest - windowSize

	// Sort events by timestamp.
	sort.Slice(eventsCopy, func(i, j int) bool {
		return eventsCopy[i].ts < eventsCopy[j].ts
	})
	// Find starting index using binary search.
	startIdx := sort.Search(len(eventsCopy), func(i int) bool {
		return eventsCopy[i].ts >= threshold
	})
	// Compute aggregation on events from startIdx to end.
	var result float64
	count := 0
	switch aggType {
	case "sum":
		for i := startIdx; i < len(eventsCopy); i++ {
			result += eventsCopy[i].value
		}
	case "average":
		for i := startIdx; i < len(eventsCopy); i++ {
			result += eventsCopy[i].value
			count++
		}
		if count > 0 {
			result = result / float64(count)
		}
	case "maximum":
		found := false
		for i := startIdx; i < len(eventsCopy); i++ {
			if !found || eventsCopy[i].value > result {
				result = eventsCopy[i].value
				found = true
			}
		}
		if !found {
			return 0, errors.New("no events in the given window")
		}
	default:
		s.mu.Unlock()
		return 0, errors.New("unknown aggregation type")
	}
	s.mu.Unlock()
	return result, nil
}