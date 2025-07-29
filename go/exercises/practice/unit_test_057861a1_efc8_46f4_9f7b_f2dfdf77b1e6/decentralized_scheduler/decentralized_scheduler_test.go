package scheduler

import (
	"sync"
	"testing"
	"time"
)

func TestScheduleNoConflict(t *testing.T) {
	network := NewNetwork([]string{"emp1", "emp2"})

	now := time.Now().Unix()
	event := Event{
		Start:        now + 60,
		End:          now + 120,
		Description:  "Team Meeting",
		Participants: []string{"emp1", "emp2"},
		ID:           "event1",
	}

	err := network.ProposeEvent(event)
	if err != nil {
		t.Fatalf("Expected event to be scheduled successfully, got error: %v", err)
	}

	cal1 := network.GetCalendar("emp1")
	cal2 := network.GetCalendar("emp2")

	if !containsEvent(cal1.Events, event) {
		t.Errorf("Employee emp1 calendar missing scheduled event")
	}
	if !containsEvent(cal2.Events, event) {
		t.Errorf("Employee emp2 calendar missing scheduled event")
	}
}

func TestScheduleWithConflict(t *testing.T) {
	network := NewNetwork([]string{"emp1", "emp2"})

	now := time.Now().Unix()
	// Schedule the initial event.
	event1 := Event{
		Start:        now + 60,
		End:          now + 120,
		Description:  "Morning Sync",
		Participants: []string{"emp1", "emp2"},
		ID:           "event1",
	}

	err := network.ProposeEvent(event1)
	if err != nil {
		t.Fatalf("Expected event1 to be scheduled successfully, got error: %v", err)
	}

	// Propose a conflicting event.
	event2 := Event{
		Start:        now + 90,
		End:          now + 150,
		Description:  "Overlapping Meeting",
		Participants: []string{"emp1"},
		ID:           "event2",
	}

	err = network.ProposeEvent(event2)
	if err == nil {
		t.Fatalf("Expected conflict error for event2, but scheduling succeeded")
	}
}

func TestConcurrentScheduling(t *testing.T) {
	employees := []string{"emp1", "emp2", "emp3", "emp4", "emp5"}
	network := NewNetwork(employees)

	now := time.Now().Unix()
	events := []Event{
		{
			Start:        now + 60,
			End:          now + 120,
			Description:  "Meeting A",
			Participants: []string{"emp1", "emp2"},
			ID:           "eventA",
		},
		{
			Start:        now + 90,
			End:          now + 150,
			Description:  "Meeting B",
			Participants: []string{"emp2", "emp3"},
			ID:           "eventB",
		},
		{
			Start:        now + 100,
			End:          now + 160,
			Description:  "Meeting C",
			Participants: []string{"emp3", "emp4"},
			ID:           "eventC",
		},
		{
			Start:        now + 170,
			End:          now + 230,
			Description:  "Meeting D",
			Participants: []string{"emp4", "emp5"},
			ID:           "eventD",
		},
	}

	var wg sync.WaitGroup
	errorsChan := make(chan error, len(events))
	for _, ev := range events {
		wg.Add(1)
		go func(e Event) {
			defer wg.Done()
			err := network.ProposeEvent(e)
			errorsChan <- err
		}(ev)
	}
	wg.Wait()
	close(errorsChan)

	// Verify consistency among calendars.
	for _, emp := range employees {
		cal := network.GetCalendar(emp)
		for _, event := range cal.Events {
			for _, participant := range event.Participants {
				pCal := network.GetCalendar(participant)
				if !containsEvent(pCal.Events, event) {
					t.Errorf("Inconsistency detected: Event %s missing from calendar of participant %s", event.ID, participant)
				}
			}
		}
	}
}

func TestFaultTolerance(t *testing.T) {
	employees := []string{"emp1", "emp2", "emp3"}
	network := NewNetwork(employees)

	// Set emp2 as unavailable.
	network.SetAvailability("emp2", false)

	now := time.Now().Unix()
	event := Event{
		Start:        now + 60,
		End:          now + 120,
		Description:  "Critical Meeting",
		Participants: []string{"emp1", "emp2"},
		ID:           "eventFault",
	}

	err := network.ProposeEvent(event)
	if err == nil {
		t.Errorf("Expected scheduling failure due to unavailable participant, but event was scheduled")
	}

	// Bring emp2 back online.
	network.SetAvailability("emp2", true)
	err = network.ProposeEvent(event)
	if err != nil {
		t.Errorf("Expected event to be scheduled after participant is available, got error: %v", err)
	}
}

func containsEvent(events []Event, target Event) bool {
	for _, e := range events {
		if e.ID == target.ID {
			return true
		}
	}
	return false
}