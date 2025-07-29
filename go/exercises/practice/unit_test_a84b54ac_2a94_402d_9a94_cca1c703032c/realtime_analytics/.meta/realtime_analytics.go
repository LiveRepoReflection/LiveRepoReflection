package realtime_analytics

import (
	"encoding/json"
	"errors"
	"sync"
	"time"
)

type Analytics struct {
	mu          sync.Mutex
	currentTime int64
	buckets     map[int64]*Bucket
}

type Bucket struct {
	Total        int
	EventsByUser map[string]int
	EventsByType map[string]int
	SumValue     map[string]map[string]float64
}

// NewAnalytics creates a new Analytics instance with the current Unix timestamp.
func NewAnalytics() *Analytics {
	return &Analytics{
		currentTime: time.Now().Unix(),
		buckets:     make(map[int64]*Bucket),
	}
}

// ProcessEvent parses the JSON event and updates the corresponding bucket.
// Expects JSON event with fields: "user_id" (string), "event_type" (string),
// "timestamp" (int), and an optional "attributes" object with a "value" (number).
func (a *Analytics) ProcessEvent(eventJSON string) error {
	var event map[string]interface{}
	if err := json.Unmarshal([]byte(eventJSON), &event); err != nil {
		return err
	}

	// Validate required fields: user_id, event_type, timestamp.
	userInter, ok := event["user_id"]
	if !ok {
		return errors.New("missing field user_id")
	}
	userID, ok := userInter.(string)
	if !ok {
		return errors.New("user_id is not a string")
	}

	eventTypeInter, ok := event["event_type"]
	if !ok {
		return errors.New("missing field event_type")
	}
	eventType, ok := eventTypeInter.(string)
	if !ok {
		return errors.New("event_type is not a string")
	}

	timestampInter, ok := event["timestamp"]
	if !ok {
		return errors.New("missing field timestamp")
	}
	var timestamp int64
	switch t := timestampInter.(type) {
	case float64:
		timestamp = int64(t)
	default:
		return errors.New("timestamp is not a valid number")
	}

	var value float64
	hasValue := false
	if attributes, ok := event["attributes"]; ok {
		if attrMap, ok := attributes.(map[string]interface{}); ok {
			if v, ok := attrMap["value"]; ok {
				if num, ok := v.(float64); ok {
					value = num
					hasValue = true
				}
			}
		}
	}

	a.mu.Lock()
	defer a.mu.Unlock()

	// Create a bucket for the given timestamp if it doesn't exist.
	bucket, exists := a.buckets[timestamp]
	if !exists {
		bucket = &Bucket{
			Total:        0,
			EventsByUser: make(map[string]int),
			EventsByType: make(map[string]int),
			SumValue:     make(map[string]map[string]float64),
		}
		a.buckets[timestamp] = bucket
	}

	// Update aggregates in the bucket.
	bucket.Total++
	bucket.EventsByUser[userID]++
	bucket.EventsByType[eventType]++
	if hasValue {
		if bucket.SumValue[userID] == nil {
			bucket.SumValue[userID] = make(map[string]float64)
		}
		bucket.SumValue[userID][eventType] += value
	}

	return nil
}

// AdvanceTime sets the current time for the analytics system and
// cleans up any buckets that fall outside the 60-second window.
func (a *Analytics) AdvanceTime(newTime int64) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.currentTime = newTime
	a.cleanupBuckets()
}

// cleanupBuckets removes buckets with timestamps older than currentTime - 60 seconds.
func (a *Analytics) cleanupBuckets() {
	threshold := a.currentTime - 60
	for ts := range a.buckets {
		if ts <= threshold {
			delete(a.buckets, ts)
		}
	}
}

// TotalEvents returns the total count of events within the current 60-second window.
func (a *Analytics) TotalEvents() int {
	a.mu.Lock()
	defer a.mu.Unlock()

	total := 0
	for ts, bucket := range a.buckets {
		if ts > a.currentTime-60 {
			total += bucket.Total
		}
	}
	return total
}

// EventsByUser returns the number of events for a given user within the current 60-second window.
func (a *Analytics) EventsByUser(userID string) int {
	a.mu.Lock()
	defer a.mu.Unlock()

	total := 0
	for ts, bucket := range a.buckets {
		if ts > a.currentTime-60 {
			total += bucket.EventsByUser[userID]
		}
	}
	return total
}

// EventsByType returns the number of events for a given event type within the current 60-second window.
func (a *Analytics) EventsByType(eventType string) int {
	a.mu.Lock()
	defer a.mu.Unlock()

	total := 0
	for ts, bucket := range a.buckets {
		if ts > a.currentTime-60 {
			total += bucket.EventsByType[eventType]
		}
	}
	return total
}

// SumValue returns the sum of the 'value' attributes for a given user and event type within the current 60-second window.
func (a *Analytics) SumValue(userID, eventType string) float64 {
	a.mu.Lock()
	defer a.mu.Unlock()

	sum := 0.0
	for ts, bucket := range a.buckets {
		if ts > a.currentTime-60 {
			if userMap, ok := bucket.SumValue[userID]; ok {
				sum += userMap[eventType]
			}
		}
	}
	return sum
}