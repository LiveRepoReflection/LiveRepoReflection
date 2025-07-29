package event_horizon

import (
	"errors"
	"sort"
	"sync"
)

// Event represents an event in the system.
type Event struct {
	Timestamp int64
	ID        string
	Priority  int
	Payload   string
}

// Store defines the interface for event storage.
type Store interface {
	Ingest(e Event) error
	QueryByTimestampRange(start, end int64) ([]Event, error)
	QueryByEventID(id string) (Event, error)
	DeleteByTimestampRange(start, end int64) error
}

// store implements the Store interface.
type store struct {
	mu           sync.RWMutex
	eventsByID   map[string]Event
	eventsSorted []Event // sorted by Timestamp ascending
}

// NewStore creates and returns a new event store.
func NewStore() Store {
	return &store{
		eventsByID:   make(map[string]Event),
		eventsSorted: make([]Event, 0),
	}
}

// Ingest adds a new event or overwrites an existing event with the same ID.
func (s *store) Ingest(e Event) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	// If an event with the same ID exists, remove it from eventsSorted.
	if oldEvent, exists := s.eventsByID[e.ID]; exists {
		index := s.findEventIndex(oldEvent)
		if index != -1 {
			s.eventsSorted = append(s.eventsSorted[:index], s.eventsSorted[index+1:]...)
		}
	}

	// Insert or update event in map.
	s.eventsByID[e.ID] = e

	// Insert event into eventsSorted maintain order by Timestamp ascending.
	newIndex := sort.Search(len(s.eventsSorted), func(i int) bool {
		return s.eventsSorted[i].Timestamp >= e.Timestamp
	})
	if newIndex == len(s.eventsSorted) {
		s.eventsSorted = append(s.eventsSorted, e)
	} else {
		s.eventsSorted = append(s.eventsSorted, Event{})
		copy(s.eventsSorted[newIndex+1:], s.eventsSorted[newIndex:])
		s.eventsSorted[newIndex] = e
	}
	return nil
}

// QueryByTimestampRange returns events within [start, end] sorted by Priority descending and Timestamp ascending.
func (s *store) QueryByTimestampRange(start, end int64) ([]Event, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// Find the starting index using binary search.
	startIndex := sort.Search(len(s.eventsSorted), func(i int) bool {
		return s.eventsSorted[i].Timestamp >= start
	})
	var results []Event
	for i := startIndex; i < len(s.eventsSorted); i++ {
		if s.eventsSorted[i].Timestamp > end {
			break
		}
		results = append(results, s.eventsSorted[i])
	}
	// Sort by Priority descending and for equal Priority, Timestamp ascending.
	sort.Slice(results, func(i, j int) bool {
		if results[i].Priority > results[j].Priority {
			return true
		} else if results[i].Priority < results[j].Priority {
			return false
		}
		return results[i].Timestamp < results[j].Timestamp
	})
	return results, nil
}

// QueryByEventID returns the event corresponding to the given ID.
func (s *store) QueryByEventID(id string) (Event, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	e, exists := s.eventsByID[id]
	if !exists {
		return Event{}, errors.New("event not found")
	}
	return e, nil
}

// DeleteByTimestampRange deletes events with Timestamp in [start, end].
func (s *store) DeleteByTimestampRange(start, end int64) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Find the starting index using binary search.
	startIndex := sort.Search(len(s.eventsSorted), func(i int) bool {
		return s.eventsSorted[i].Timestamp >= start
	})
	// Find the ending index.
	endIndex := startIndex
	for endIndex < len(s.eventsSorted) && s.eventsSorted[endIndex].Timestamp <= end {
		endIndex++
	}
	// Remove events from the map.
	for i := startIndex; i < endIndex; i++ {
		delete(s.eventsByID, s.eventsSorted[i].ID)
	}
	// Delete events from the sorted slice.
	s.eventsSorted = append(s.eventsSorted[:startIndex], s.eventsSorted[endIndex:]...)
	return nil
}

// findEventIndex returns the index of the event in eventsSorted slice or -1 if not found.
func (s *store) findEventIndex(e Event) int {
	// Since eventsSorted is sorted by Timestamp, iterate over a small range.
	// There may be multiple events with the same timestamp.
	for i, event := range s.eventsSorted {
		if event.ID == e.ID {
			return i
		}
	}
	return -1
}