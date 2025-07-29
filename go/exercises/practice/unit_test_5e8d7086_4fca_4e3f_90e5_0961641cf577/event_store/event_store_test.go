package event_store

import (
	"fmt"
	"reflect"
	"sync"
	"testing"
	"time"
)

// testSubscriber implements the Subscriber interface and captures received events.
type testSubscriber struct {
	mu     sync.Mutex
	events []Event
	ch     chan Event
}

func newTestSubscriber() *testSubscriber {
	return &testSubscriber{
		events: make([]Event, 0),
		ch:     make(chan Event, 10),
	}
}

func (ts *testSubscriber) ProcessEvent(e Event) error {
	ts.mu.Lock()
	ts.events = append(ts.events, e)
	ts.mu.Unlock()
	ts.ch <- e
	return nil
}

// TestAppendAndGetEvents verifies that appended events can be retrieved by GetEvents.
func TestAppendAndGetEvents(t *testing.T) {
	store := NewEventStore()
	now := time.Now()
	event1 := Event{
		ID:        "1",
		Type:      "OrderCreated",
		Data:      []byte(`{"order":1}`),
		Timestamp: now,
	}
	if err := store.Append(event1); err != nil {
		t.Fatalf("Append failed: %v", err)
	}

	events, err := store.GetEvents("OrderCreated", 0)
	if err != nil {
		t.Fatalf("GetEvents failed: %v", err)
	}
	if len(events) != 1 {
		t.Fatalf("Expected 1 event, got %d", len(events))
	}
	if !reflect.DeepEqual(events[0], event1) {
		t.Fatalf("Expected event %v, got %v", event1, events[0])
	}
}

// TestSubscribeAndReceive verifies that a subscribed subscriber receives events upon Append.
func TestSubscribeAndReceive(t *testing.T) {
	store := NewEventStore()
	subscriber := newTestSubscriber()

	if err := store.Subscribe("OrderCreated", subscriber); err != nil {
		t.Fatalf("Subscribe failed: %v", err)
	}

	now := time.Now()
	event1 := Event{
		ID:        "1",
		Type:      "OrderCreated",
		Data:      []byte(`{"order":1}`),
		Timestamp: now,
	}
	if err := store.Append(event1); err != nil {
		t.Fatalf("Append failed: %v", err)
	}

	select {
	case e := <-subscriber.ch:
		if !reflect.DeepEqual(e, event1) {
			t.Fatalf("Expected event %v, got %v", event1, e)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("Timeout waiting for event in TestSubscribeAndReceive.")
	}
}

// TestEventOrder verifies that events are stored and retrieved in the correct order.
func TestEventOrder(t *testing.T) {
	store := NewEventStore()
	now := time.Now()
	eventsToAppend := []Event{
		{
			ID:        "1",
			Type:      "OrderUpdated",
			Data:      []byte(`{"order":1,"status":"processing"}`),
			Timestamp: now.Add(10 * time.Millisecond),
		},
		{
			ID:        "2",
			Type:      "OrderUpdated",
			Data:      []byte(`{"order":1,"status":"shipped"}`),
			Timestamp: now.Add(20 * time.Millisecond),
		},
		{
			ID:        "3",
			Type:      "OrderUpdated",
			Data:      []byte(`{"order":1,"status":"delivered"}`),
			Timestamp: now.Add(30 * time.Millisecond),
		},
	}
	for _, e := range eventsToAppend {
		if err := store.Append(e); err != nil {
			t.Fatalf("Append failed: %v", err)
		}
	}

	returnedEvents, err := store.GetEvents("OrderUpdated", 0)
	if err != nil {
		t.Fatalf("GetEvents failed: %v", err)
	}
	if len(returnedEvents) != len(eventsToAppend) {
		t.Fatalf("Expected %d events, got %d", len(eventsToAppend), len(returnedEvents))
	}
	for i, e := range returnedEvents {
		if !reflect.DeepEqual(e, eventsToAppend[i]) {
			t.Fatalf("At index %d, expected event %v, got %v", i, eventsToAppend[i], e)
		}
	}
}

// TestConcurrentAppends verifies that concurrent Append calls are handled safely.
func TestConcurrentAppends(t *testing.T) {
	store := NewEventStore()
	var wg sync.WaitGroup
	totalEvents := 100
	eventType := "PaymentProcessed"

	for i := 0; i < totalEvents; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			evt := Event{
				ID:        fmt.Sprintf("%d", i),
				Type:      eventType,
				Data:      []byte(fmt.Sprintf(`{"payment_id":%d}`, i)),
				Timestamp: time.Now(),
			}
			if err := store.Append(evt); err != nil {
				t.Errorf("Append failed: %v", err)
			}
		}(i)
	}
	wg.Wait()

	events, err := store.GetEvents(eventType, 0)
	if err != nil {
		t.Fatalf("GetEvents failed: %v", err)
	}
	if len(events) != totalEvents {
		t.Fatalf("Expected %d events, got %d", totalEvents, len(events))
	}
}

// TestConcurrentSubscription verifies that multiple subscribers receive events concurrently.
func TestConcurrentSubscription(t *testing.T) {
	store := NewEventStore()
	subscriber1 := newTestSubscriber()
	subscriber2 := newTestSubscriber()
	eventType := "StockLevelUpdated"

	var wg sync.WaitGroup
	wg.Add(2)
	go func() {
		defer wg.Done()
		if err := store.Subscribe(eventType, subscriber1); err != nil {
			t.Errorf("Subscriber1 Subscribe failed: %v", err)
		}
	}()
	go func() {
		defer wg.Done()
		if err := store.Subscribe(eventType, subscriber2); err != nil {
			t.Errorf("Subscriber2 Subscribe failed: %v", err)
		}
	}()
	wg.Wait()

	now := time.Now()
	event1 := Event{
		ID:        "1",
		Type:      eventType,
		Data:      []byte(`{"product":101,"quantity":5}`),
		Timestamp: now,
	}
	if err := store.Append(event1); err != nil {
		t.Fatalf("Append failed: %v", err)
	}

	receivedCount := 0
	timeout := time.After(2 * time.Second)
	for receivedCount < 2 {
		select {
		case e := <-subscriber1.ch:
			if !reflect.DeepEqual(e, event1) {
				t.Fatalf("Subscriber1 received wrong event: %v", e)
			}
			receivedCount++
		case e := <-subscriber2.ch:
			if !reflect.DeepEqual(e, event1) {
				t.Fatalf("Subscriber2 received wrong event: %v", e)
			}
			receivedCount++
		case <-timeout:
			t.Fatal("Timeout waiting for events in TestConcurrentSubscription")
		}
	}
}