package data_percentiles

import (
	"math"
	"math/rand"
	"sync"
	"testing"
	"time"
)

// newTestAnalyticsPlatform creates a new instance of AnalyticsPlatform.
// It is assumed that NewAnalyticsPlatform is implemented in the solution.
func newTestAnalyticsPlatform(t *testing.T) AnalyticsPlatform {
	ap, err := NewAnalyticsPlatform()
	if err != nil {
		t.Fatalf("Failed to initialize AnalyticsPlatform: %v", err)
	}
	return ap
}

func TestSetCompressionFactor(t *testing.T) {
	ap := newTestAnalyticsPlatform(t)

	// Test setting an invalid compression factor
	err := ap.SetCompressionFactor(-1.0)
	if err == nil {
		t.Errorf("SetCompressionFactor accepted a negative value, expected an error")
	}

	// Test setting a valid compression factor
	err = ap.SetCompressionFactor(100.0)
	if err != nil {
		t.Errorf("SetCompressionFactor returned error for valid input: %v", err)
	}
}

func TestSetDecayFactor(t *testing.T) {
	ap := newTestAnalyticsPlatform(t)

	// Test setting an out of range decay factor (assumed invalid if not between 0 and 1)
	err := ap.SetDecayFactor(1.5)
	if err == nil {
		t.Errorf("SetDecayFactor accepted an out of range value, expected an error")
	}

	// Test setting a valid decay factor
	err = ap.SetDecayFactor(0.5)
	if err != nil {
		t.Errorf("SetDecayFactor returned error for valid input: %v", err)
	}
}

func TestAddDataPointAndQuery(t *testing.T) {
	ap := newTestAnalyticsPlatform(t)
	userID := "user1"

	// Query percentile for a user with no data should return an error
	_, err := ap.GetPercentile(userID, 50)
	if err == nil {
		t.Errorf("Expected error when querying percentile for a user with no data")
	}

	// Ingest a known set of data points
	dataPoints := []float64{1.0, 3.0, 5.0, 7.0, 9.0}
	for i, val := range dataPoints {
		timestamp := time.Now().Add(time.Duration(i) * time.Second).Unix()
		if err := ap.AddDataPoint(userID, timestamp, val); err != nil {
			t.Fatalf("AddDataPoint failed for value %v: %v", val, err)
		}
	}

	// Query median (50th percentile)
	median, err := ap.GetPercentile(userID, 50)
	if err != nil {
		t.Fatalf("GetPercentile failed: %v", err)
	}

	// For the provided data set, the expected median should be approximately 5.0.
	if math.Abs(median-5.0) > 1.0 {
		t.Errorf("Median value out of expected range, got %v, expected approximately 5.0", median)
	}

	// Query with invalid percentile values: negative and over 100
	_, err = ap.GetPercentile(userID, -10)
	if err == nil {
		t.Errorf("Expected error when querying with a negative percentile")
	}

	_, err = ap.GetPercentile(userID, 150)
	if err == nil {
		t.Errorf("Expected error when querying with a percentile greater than 100")
	}
}

func TestConcurrentAccess(t *testing.T) {
	ap := newTestAnalyticsPlatform(t)
	userID := "concurrent_user"
	var wg sync.WaitGroup

	// Launch multiple goroutines to add data concurrently.
	numGoroutines := 50
	dataPerGoroutine := 100
	startTime := time.Now().Unix()
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			rnd := rand.New(rand.NewSource(time.Now().UnixNano() + int64(id)))
			for j := 0; j < dataPerGoroutine; j++ {
				timestamp := startTime + int64(j)
				value := rnd.Float64() * 100
				if err := ap.AddDataPoint(userID, timestamp, value); err != nil {
					t.Errorf("Goroutine %d: AddDataPoint failed: %v", id, err)
				}
			}
		}(i)
	}
	wg.Wait()

	// Launch concurrent queries to fetch the 50th percentile.
	queryGoroutines := 20
	for i := 0; i < queryGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			p := 50.0
			value, err := ap.GetPercentile(userID, p)
			if err != nil {
				t.Errorf("GetPercentile failed for percentile %v: %v", p, err)
			} else {
				// Check if the returned value is within the expected boundaries.
				if value < 0 || value > 100 {
					t.Errorf("Percentile result %v out of expected range", value)
				}
			}
		}()
	}
	wg.Wait()
}

func TestMultipleUsers(t *testing.T) {
	ap := newTestAnalyticsPlatform(t)
	users := []string{"userA", "userB", "userC"}
	now := time.Now().Unix()

	// Ingest different data streams for multiple users.
	for _, userID := range users {
		for i := 1; i <= 100; i++ {
			timestamp := now + int64(i)
			if err := ap.AddDataPoint(userID, timestamp, float64(i)); err != nil {
				t.Fatalf("AddDataPoint failed for user %s with value %d: %v", userID, i, err)
			}
		}
	}

	// Query for the 90th percentile for each user.
	for _, userID := range users {
		perc, err := ap.GetPercentile(userID, 90)
		if err != nil {
			t.Errorf("GetPercentile failed for user %s: %v", userID, err)
		} else {
			// For a sequential list from 1 to 100, expect roughly 90 as the 90th percentile.
			if math.Abs(perc-90) > 10 {
				t.Errorf("User %s: 90th percentile value %v out of acceptable range", userID, perc)
			}
		}
	}
}