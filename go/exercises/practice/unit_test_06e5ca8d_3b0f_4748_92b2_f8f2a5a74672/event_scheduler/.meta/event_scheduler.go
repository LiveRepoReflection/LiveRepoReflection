package event_scheduler

import (
	"container/heap"
	"errors"
	"fmt"
	"sync"
	"time"
)

// Event represents a scheduled event with metadata
type Event struct {
	ID            string
	ExecutionTime int64
	Payload       string
	Executed      bool
	Cancelled     bool
}

// EventScheduler is the main scheduler struct
type EventScheduler struct {
	events      map[string]*Event
	timeIndex   *TimeHeap
	mutex       sync.RWMutex
}

// NewEventScheduler creates a new instance of EventScheduler
func NewEventScheduler() *EventScheduler {
	scheduler := &EventScheduler{
		events:    make(map[string]*Event),
		timeIndex: &TimeHeap{},
	}
	heap.Init(scheduler.timeIndex)
	return scheduler
}

// ScheduleEvent schedules a new event or updates an existing one
func (es *EventScheduler) ScheduleEvent(eventID string, executionTime int64, payload string) error {
	if eventID == "" {
		return errors.New("event ID cannot be empty")
	}

	// Check if execution time is in the past
	if executionTime <= time.Now().Unix() {
		return errors.New("execution time must be in the future")
	}

	es.mutex.Lock()
	defer es.mutex.Unlock()

	// Check if event already exists (idempotence)
	existingEvent, exists := es.events[eventID]
	if exists {
		// Update the existing event
		if !existingEvent.Executed && !existingEvent.Cancelled {
			existingEvent.ExecutionTime = executionTime
			existingEvent.Payload = payload
			
			// Re-heapify to account for the updated execution time
			heap.Init(es.timeIndex)
		}
		return nil
	}

	// Create a new event
	newEvent := &Event{
		ID:            eventID,
		ExecutionTime: executionTime,
		Payload:       payload,
		Executed:      false,
		Cancelled:     false,
	}

	// Add to map and priority queue
	es.events[eventID] = newEvent
	heap.Push(es.timeIndex, eventIDTime{
		ID:   eventID,
		Time: executionTime,
	})

	return nil
}

// CancelEvent cancels a previously scheduled event
func (es *EventScheduler) CancelEvent(eventID string) error {
	if eventID == "" {
		return errors.New("event ID cannot be empty")
	}

	es.mutex.Lock()
	defer es.mutex.Unlock()

	event, exists := es.events[eventID]
	if !exists {
		return fmt.Errorf("event with ID %s does not exist", eventID)
	}

	if event.Executed {
		return fmt.Errorf("event with ID %s has already been executed", eventID)
	}

	event.Cancelled = true
	return nil
}

// GetNextEvents retrieves events scheduled at or before the given time
func (es *EventScheduler) GetNextEvents(currentTime int64, limit int) ([]string, error) {
	if limit < 0 {
		return nil, errors.New("limit must be non-negative")
	}

	if limit == 0 {
		return []string{}, nil
	}

	es.mutex.RLock()
	defer es.mutex.RUnlock()

	// Create a temporary copy of the time index for querying
	tempHeap := &TimeHeap{}
	*tempHeap = append(*tempHeap, (*es.timeIndex)...)
	heap.Init(tempHeap)

	result := make([]string, 0, limit)
	for tempHeap.Len() > 0 && len(result) < limit {
		item := heap.Pop(tempHeap).(eventIDTime)
		
		// Check if event is scheduled at or before currentTime
		if item.Time > currentTime {
			break
		}

		// Retrieve event details
		event, exists := es.events[item.ID]
		if exists && !event.Executed && !event.Cancelled {
			result = append(result, item.ID)
		}
	}

	return result, nil
}

// MarkEventAsExecuted marks an event as executed
func (es *EventScheduler) MarkEventAsExecuted(eventID string) error {
	if eventID == "" {
		return errors.New("event ID cannot be empty")
	}

	es.mutex.Lock()
	defer es.mutex.Unlock()

	event, exists := es.events[eventID]
	if !exists {
		return fmt.Errorf("event with ID %s does not exist", eventID)
	}

	// Idempotence: if already executed, just return success
	if event.Executed {
		return nil
	}

	if event.Cancelled {
		return fmt.Errorf("event with ID %s has been cancelled", eventID)
	}

	event.Executed = true
	return nil
}

// TimeHeap is a min-heap of event IDs ordered by execution time
type TimeHeap []eventIDTime

type eventIDTime struct {
	ID   string
	Time int64
}

// Implementation of heap.Interface for TimeHeap
func (h TimeHeap) Len() int { return len(h) }

func (h TimeHeap) Less(i, j int) bool {
	return h[i].Time < h[j].Time
}

func (h TimeHeap) Swap(i, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *TimeHeap) Push(x interface{}) {
	*h = append(*h, x.(eventIDTime))
}

func (h *TimeHeap) Pop() interface{} {
	old := *h
	n := len(old)
	item := old[n-1]
	*h = old[0 : n-1]
	return item
}