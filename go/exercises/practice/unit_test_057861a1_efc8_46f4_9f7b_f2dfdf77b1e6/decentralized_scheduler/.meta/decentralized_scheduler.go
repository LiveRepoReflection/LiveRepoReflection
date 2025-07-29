package scheduler

import (
	"errors"
	"sync"
	"time"
)

type Event struct {
	Start        int64
	End          int64
	Description  string
	Participants []string
	ID           string
}

type Calendar struct {
	Events []Event
	mu     sync.Mutex
}

type Node struct {
	id        string
	calendar  *Calendar
	available bool
	mu        sync.Mutex
}

type Network struct {
	nodes map[string]*Node
	mu    sync.Mutex
}

// NewNetwork creates a network with nodes for each provided employee ID.
func NewNetwork(employeeIDs []string) *Network {
	nodes := make(map[string]*Node)
	for _, id := range employeeIDs {
		nodes[id] = &Node{
			id:        id,
			calendar:  &Calendar{Events: []Event{}},
			available: true,
		}
	}
	return &Network{
		nodes: nodes,
	}
}

// SetAvailability sets the availability of a node.
func (n *Network) SetAvailability(id string, avail bool) {
	n.mu.Lock()
	node, exists := n.nodes[id]
	n.mu.Unlock()
	if exists {
		node.mu.Lock()
		node.available = avail
		node.mu.Unlock()
	}
}

// GetCalendar returns a copy of the calendar for the given employee.
func (n *Network) GetCalendar(id string) Calendar {
	n.mu.Lock()
	node, exists := n.nodes[id]
	n.mu.Unlock()
	if !exists {
		return Calendar{Events: []Event{}}
	}
	node.calendar.mu.Lock()
	defer node.calendar.mu.Unlock()
	eventsCopy := make([]Event, len(node.calendar.Events))
	copy(eventsCopy, node.calendar.Events)
	return Calendar{Events: eventsCopy}
}

// ProposeEvent implements a simplified Paxos consensus mechanism to schedule an event.
// It performs a prepare phase (promise) and then an accept phase.
func (n *Network) ProposeEvent(event Event) error {
	// Prepare phase: send proposal to all participants and request promise.
	var mu sync.Mutex
	promiseCount := 0

	for _, participant := range event.Participants {
		n.mu.Lock()
		node, exists := n.nodes[participant]
		n.mu.Unlock()
		if !exists {
			return errors.New("participant " + participant + " does not exist")
		}

		node.mu.Lock()
		available := node.available
		node.mu.Unlock()
		if !available {
			return errors.New("participant " + participant + " is not available")
		}

		// Check for conflicts in the node's calendar.
		node.calendar.mu.Lock()
		for _, scheduled := range node.calendar.Events {
			if eventsConflict(scheduled, event) {
				node.calendar.mu.Unlock()
				return errors.New("conflict detected for participant " + participant)
			}
		}
		node.calendar.mu.Unlock()

		mu.Lock()
		promiseCount++
		mu.Unlock()
	}

	// In our simulation, we require promises from all participants.
	if promiseCount < len(event.Participants) {
		return errors.New("failed to get majority promises")
	}

	// Accept phase: send accept messages to all participants.
	for _, participant := range event.Participants {
		n.mu.Lock()
		node, exists := n.nodes[participant]
		n.mu.Unlock()
		if !exists {
			return errors.New("participant " + participant + " does not exist in accept phase")
		}
		node.calendar.mu.Lock()
		// Double-check for conflicts in case the state changed.
		for _, scheduled := range node.calendar.Events {
			if eventsConflict(scheduled, event) {
				node.calendar.mu.Unlock()
				return errors.New("conflict detected during accept phase for participant " + participant)
			}
		}
		// Append the event.
		node.calendar.Events = append(node.calendar.Events, event)
		node.calendar.mu.Unlock()
	}

	// Simulate a small delay to represent consensus timing.
	time.Sleep(10 * time.Millisecond)
	return nil
}

// eventsConflict checks whether two events conflict based on time overlap and shared participants.
func eventsConflict(a, b Event) bool {
	// No conflict if events do not overlap in time.
	if a.End <= b.Start || b.End <= a.Start {
		return false
	}
	// Check if there is any common participant.
	for _, pA := range a.Participants {
		for _, pB := range b.Participants {
			if pA == pB {
				return true
			}
		}
	}
	return false
}