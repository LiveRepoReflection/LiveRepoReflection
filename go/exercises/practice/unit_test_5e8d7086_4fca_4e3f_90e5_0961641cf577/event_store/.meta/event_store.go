package event_store

import (
	"sync"
	"time"
)

// Event defines the structure of an event.
type Event struct {
	ID        string    `json:"id"`
	Type      string    `json:"type"`
	Data      []byte    `json:"data"`
	Timestamp time.Time `json:"timestamp"`
}

// Subscriber is the interface for event subscribers.
type Subscriber interface {
	ProcessEvent(event Event) error
}

// EventStore defines the interface for our event store.
type EventStore interface {
	Append(event Event) error
	Subscribe(eventType string, subscriber Subscriber) error
	GetEvents(eventType string, offset int) ([]Event, error)
}

// inMemoryEventStore is an in-memory implementation of the EventStore.
type inMemoryEventStore struct {
	mu          sync.RWMutex
	events      map[string][]Event
	subscribers map[string][]Subscriber
}

// NewEventStore creates a new in-memory event store.
func NewEventStore() EventStore {
	return &inMemoryEventStore{
		events:      make(map[string][]Event),
		subscribers: make(map[string][]Subscriber),
	}
}

// Append adds an event to the store and notifies subscribers.
func (store *inMemoryEventStore) Append(event Event) error {
	store.mu.Lock()
	store.events[event.Type] = append(store.events[event.Type], event)
	subs := append([]Subscriber(nil), store.subscribers[event.Type]...)
	store.mu.Unlock()

	// Deliver event to all subscribers for this event type.
	for _, subscriber := range subs {
		err := subscriber.ProcessEvent(event)
		if err != nil {
			// In a production system, you would implement retry logic here.
		}
	}
	return nil
}

// Subscribe registers a subscriber for a given event type.
func (store *inMemoryEventStore) Subscribe(eventType string, subscriber Subscriber) error {
	store.mu.Lock()
	store.subscribers[eventType] = append(store.subscribers[eventType], subscriber)
	store.mu.Unlock()
	return nil
}

// GetEvents retrieves events of a specific type starting from the given offset.
func (store *inMemoryEventStore) GetEvents(eventType string, offset int) ([]Event, error) {
	store.mu.RLock()
	events, ok := store.events[eventType]
	store.mu.RUnlock()
	if !ok || offset < 0 || offset > len(events) {
		return []Event{}, nil
	}
	return events[offset:], nil
}