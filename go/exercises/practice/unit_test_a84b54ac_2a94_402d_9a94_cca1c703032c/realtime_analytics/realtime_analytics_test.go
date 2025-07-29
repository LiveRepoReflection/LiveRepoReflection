package realtime_analytics_test

import (
	"encoding/json"
	"strconv"
	"sync"
	"testing"
	"time"

	"realtime_analytics"
)

// createEventJSON is a helper to create a JSON string for an event.
func createEventJSON(userID, eventType string, timestamp int64, value interface{}) string {
	event := map[string]interface{}{
		"user_id":    userID,
		"event_type": eventType,
		"timestamp":  timestamp,
	}
	if value != nil {
		event["attributes"] = map[string]interface{}{
			"value": value,
		}
	}
	b, _ := json.Marshal(event)
	return string(b)
}

func TestSingleEventAggregation(t *testing.T) {
	analytics := realtime_analytics.NewAnalytics()
	now := time.Now().Unix()
	eventJSON := createEventJSON("user1", "login", now, 10.0)
	err := analytics.ProcessEvent(eventJSON)
	if err != nil {
		t.Fatalf("ProcessEvent error: %v", err)
	}

	if total := analytics.TotalEvents(); total != 1 {
		t.Errorf("Expected total events 1, got %d", total)
	}
	if userCount := analytics.EventsByUser("user1"); userCount != 1 {
		t.Errorf("Expected 1 event for user1, got %d", userCount)
	}
	if typeCount := analytics.EventsByType("login"); typeCount != 1 {
		t.Errorf("Expected 1 event for login, got %d", typeCount)
	}
	if sum := analytics.SumValue("user1", "login"); sum != 10.0 {
		t.Errorf("Expected sum value for user1 login to be 10.0, got %f", sum)
	}
}

func TestMultipleEventsAggregation(t *testing.T) {
	analytics := realtime_analytics.NewAnalytics()
	now := time.Now().Unix()
	events := []string{
		createEventJSON("user1", "click", now, 2.5),
		createEventJSON("user1", "click", now, 3.5),
		createEventJSON("user2", "click", now, 1.0),
		createEventJSON("user1", "purchase", now, 20.0),
	}
	for _, e := range events {
		err := analytics.ProcessEvent(e)
		if err != nil {
			t.Fatalf("ProcessEvent error: %v", err)
		}
	}

	if total := analytics.TotalEvents(); total != 4 {
		t.Errorf("Expected total events 4, got %d", total)
	}
	if count := analytics.EventsByUser("user1"); count != 3 {
		t.Errorf("Expected 3 events for user1, got %d", count)
	}
	if count := analytics.EventsByType("click"); count != 3 {
		t.Errorf("Expected 3 click events, got %d", count)
	}
	if sum := analytics.SumValue("user1", "click"); sum != 6.0 {
		t.Errorf("Expected sum value for user1 click to be 6.0, got %f", sum)
	}
	if sum := analytics.SumValue("user1", "purchase"); sum != 20.0 {
		t.Errorf("Expected sum value for user1 purchase to be 20.0, got %f", sum)
	}
}

func TestInvalidJSONEvent(t *testing.T) {
	analytics := realtime_analytics.NewAnalytics()
	invalidJSON := "{invalid json"
	err := analytics.ProcessEvent(invalidJSON)
	if err == nil {
		t.Error("Expected error for invalid JSON, got nil")
	}
}

func TestMissingFieldsEvent(t *testing.T) {
	analytics := realtime_analytics.NewAnalytics()
	// Missing user_id and event_type fields.
	event := map[string]interface{}{
		"timestamp": time.Now().Unix(),
	}
	b, _ := json.Marshal(event)
	err := analytics.ProcessEvent(string(b))
	if err == nil {
		t.Error("Expected error for missing required fields, got nil")
	}
}

func TestTimeWindowAggregation(t *testing.T) {
	analytics := realtime_analytics.NewAnalytics()
	baseTime := time.Now().Unix()

	// Create an event that is outside the 60-second window.
	oldEvent := createEventJSON("user1", "click", baseTime-70, 4.0)
	// Create an event that is within the 60-second window.
	recentEvent := createEventJSON("user1", "click", baseTime-30, 6.0)

	// Process both events.
	if err := analytics.ProcessEvent(oldEvent); err != nil {
		t.Fatalf("ProcessEvent error: %v", err)
	}
	if err := analytics.ProcessEvent(recentEvent); err != nil {
		t.Fatalf("ProcessEvent error: %v", err)
	}

	// Advance the analytics system's current time to baseTime.
	analytics.AdvanceTime(baseTime)

	// Only the recentEvent should be included in the current 60-second window.
	if total := analytics.TotalEvents(); total != 1 {
		t.Errorf("Expected total events 1 in current window, got %d", total)
	}
	if count := analytics.EventsByUser("user1"); count != 1 {
		t.Errorf("Expected 1 event for user1 in current window, got %d", count)
	}
	if typeCount := analytics.EventsByType("click"); typeCount != 1 {
		t.Errorf("Expected 1 click event in current window, got %d", typeCount)
	}
	if sum := analytics.SumValue("user1", "click"); sum != 6.0 {
		t.Errorf("Expected sum value for user1 click to be 6.0 in current window, got %f", sum)
	}
}

func TestConcurrentEventProcessing(t *testing.T) {
	analytics := realtime_analytics.NewAnalytics()
	now := time.Now().Unix()
	var wg sync.WaitGroup
	numGoroutines := 100
	eventsPerGoroutine := 50

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for j := 0; j < eventsPerGoroutine; j++ {
				user := "user" + strconv.Itoa(id)
				eventType := "click"
				if j%2 == 0 {
					eventType = "purchase"
				}
				eventJSON := createEventJSON(user, eventType, now, float64(j))
				if err := analytics.ProcessEvent(eventJSON); err != nil {
					t.Errorf("ProcessEvent error: %v", err)
				}
			}
		}(i)
	}
	wg.Wait()

	expectedTotal := numGoroutines * eventsPerGoroutine
	if total := analytics.TotalEvents(); total != expectedTotal {
		t.Errorf("Expected total events %d, got %d", expectedTotal, total)
	}

	// Validate event aggregation for a random user.
	userEvents := analytics.EventsByUser("user50")
	if userEvents != eventsPerGoroutine {
		t.Errorf("Expected %d events for user50, got %d", eventsPerGoroutine, userEvents)
	}
}