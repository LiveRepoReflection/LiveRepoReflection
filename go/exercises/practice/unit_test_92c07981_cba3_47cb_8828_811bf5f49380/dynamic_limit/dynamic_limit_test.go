package dynamic_limit_test

import (
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"strconv"
	"sync"
	"testing"
	"time"

	"dynamic_limit"
)

// helper function to send a GET request and return status code
func sendRequest(client *http.Client, url string) (int, error) {
	resp, err := client.Get(url)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()
	// read entire body to simulate full request processing
	_, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		return 0, err
	}
	return resp.StatusCode, nil
}

// Test single allowed request and then a rate limited request.
func TestSingleRequest(t *testing.T) {
	// Set capacity to 1: only one request should be allowed.
	dynamic_limit.UpdateCapacity(1)

	// Create test server using the dynamic_limit HTTP handler.
	ts := httptest.NewServer(dynamic_limit.Handler())
	defer ts.Close()

	client := ts.Client()

	// First request should be allowed.
	status, err := sendRequest(client, ts.URL)
	if err != nil {
		t.Fatalf("unexpected error sending first request: %v", err)
	}
	if status != http.StatusOK {
		t.Fatalf("expected status %d for first request, got %d", http.StatusOK, status)
	}

	// Second request should be rate limited (429).
	status, err = sendRequest(client, ts.URL)
	if err != nil {
		t.Fatalf("unexpected error sending second request: %v", err)
	}
	if status != http.StatusTooManyRequests {
		t.Fatalf("expected status %d for second request, got %d", http.StatusTooManyRequests, status)
	}
}

// Test concurrent requests, ensuring that number of allowed requests does not exceed capacity.
func TestConcurrentRequests(t *testing.T) {
	// Set capacity to 50.
	capacity := 50
	dynamic_limit.UpdateCapacity(capacity)

	// Create test server.
	ts := httptest.NewServer(dynamic_limit.Handler())
	defer ts.Close()

	client := ts.Client()
	
	// fire 100 concurrent requests
	numRequests := 100
	var wg sync.WaitGroup
	var mu sync.Mutex
	allowed := 0
	rateLimited := 0

	for i := 0; i < numRequests; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			status, err := sendRequest(client, ts.URL)
			if err != nil {
				t.Errorf("error sending request: %v", err)
				return
			}
			mu.Lock()
			if status == http.StatusOK {
				allowed++
			} else if status == http.StatusTooManyRequests {
				rateLimited++
			} else {
				t.Errorf("unexpected status code: %d", status)
			}
			mu.Unlock()
		}()
	}
	wg.Wait()

	if allowed != capacity {
		t.Errorf("expected allowed requests count to be %d, got %d", capacity, allowed)
	}
	if allowed+rateLimited != numRequests {
		t.Errorf("total requests mismatch: expected %d got %d", numRequests, allowed+rateLimited)
	}
}

// Test dynamic capacity update during operation.
func TestCapacityDynamicUpdate(t *testing.T) {
	// Start with capacity = 10.
	initialCapacity := 10
	dynamic_limit.UpdateCapacity(initialCapacity)

	// Create test server.
	ts := httptest.NewServer(dynamic_limit.Handler())
	defer ts.Close()

	client := ts.Client()

	// Send 'initialCapacity' requests, all should be allowed.
	for i := 0; i < initialCapacity; i++ {
		status, err := sendRequest(client, ts.URL)
		if err != nil {
			t.Fatalf("unexpected error sending request: %v", err)
		}
		if status != http.StatusOK {
			t.Fatalf("expected status %d, got %d on iteration %d", http.StatusOK, status, i)
		}
	}
	// Next request should be rate limited.
	status, err := sendRequest(client, ts.URL)
	if err != nil {
		t.Fatalf("unexpected error sending request after capacity exhausted: %v", err)
	}
	if status != http.StatusTooManyRequests {
		t.Fatalf("expected status %d after capacity exhausted, got %d", http.StatusTooManyRequests, status)
	}

	// Simulate a capacity update by the Capacity Manager.
	updatedCapacity := 15
	dynamic_limit.UpdateCapacity(updatedCapacity)

	// Wait briefly to allow the update to propagate in the system.
	time.Sleep(100 * time.Millisecond)

	// Now, send updatedCapacity requests which should be allowed.
	for i := 0; i < updatedCapacity; i++ {
		status, err := sendRequest(client, ts.URL)
		if err != nil {
			t.Fatalf("unexpected error sending request after capacity update: %v", err)
		}
		if status != http.StatusOK {
			t.Fatalf("expected status %d after capacity update, got %d on iteration %d", http.StatusOK, status, i)
		}
	}

	// Next request should be rate limited.
	status, err = sendRequest(client, ts.URL)
	if err != nil {
		t.Fatalf("unexpected error sending request after updated capacity exhausted: %v", err)
	}
	if status != http.StatusTooManyRequests {
		t.Fatalf("expected status %d after updated capacity exhausted, got %d", http.StatusTooManyRequests, status)
	}
}

// Test that capacity update via multiple updates is atomic and consistent.
func TestMultipleCapacityUpdates(t *testing.T) {
	// Create test server.
	ts := httptest.NewServer(dynamic_limit.Handler())
	defer ts.Close()

	client := ts.Client()

	// Define a sequence of capacity updates.
	capacities := []int{20, 5, 15, 0, 10}
	for idx, capVal := range capacities {
		dynamic_limit.UpdateCapacity(capVal)
		// Wait for update propagation.
		time.Sleep(50 * time.Millisecond)

		// Count how many allowed requests we get.
		allowedCount := 0
		// Execute capVal + 3 requests to ensure we exceed current capacity.
		requestCount := capVal + 3

		for i := 0; i < requestCount; i++ {
			status, err := sendRequest(client, ts.URL)
			if err != nil {
				t.Fatalf("error sending request during capacity update test at iteration %d: %v", idx, err)
			}
			if status == http.StatusOK {
				allowedCount++
			}
		}

		if allowedCount != capVal {
			t.Errorf("for capacity %d, expected %d allowed requests, got %d", capVal, capVal, allowedCount)
		}
	}
}

// Test that repeated requests without capacity reset remain rate limited.
func TestPersistentRateLimiting(t *testing.T) {
	// Set capacity to 3.
	dynamic_limit.UpdateCapacity(3)

	// Create test server.
	ts := httptest.NewServer(dynamic_limit.Handler())
	defer ts.Close()

	client := ts.Client()

	// Send three requests to use up capacity.
	for i := 0; i < 3; i++ {
		status, err := sendRequest(client, ts.URL)
		if err != nil {
			t.Fatalf("unexpected error sending request: %v", err)
		}
		if status != http.StatusOK {
			t.Fatalf("expected status %d, got %d", http.StatusOK, status)
		}
	}

	// Additional requests should be rate limited.
	for i := 0; i < 5; i++ {
		status, err := sendRequest(client, ts.URL)
		if err != nil {
			t.Fatalf("unexpected error sending request after capacity exhausted: %v", err)
		}
		if status != http.StatusTooManyRequests {
			t.Fatalf("expected status %d after capacity exhausted, got %d", http.StatusTooManyRequests, status)
		}
	}
}

// Test rapid capacity changes and concurrent access.
func TestRapidCapacityChanges(t *testing.T) {
	// Create test server.
	ts := httptest.NewServer(dynamic_limit.Handler())
	defer ts.Close()

	client := ts.Client()
	var wg sync.WaitGroup

	// Function to rapidly update capacity.
	updateFunc := func() {
		defer wg.Done()
		for i := 0; i < 20; i++ {
			// Cycle capacity between 0 and 25.
			dynamic_limit.UpdateCapacity(i % 26)
			time.Sleep(10 * time.Millisecond)
		}
	}

	// Function to send requests continuously.
	requestFunc := func() {
		defer wg.Done()
		for i := 0; i < 50; i++ {
			_, err := sendRequest(client, ts.URL)
			if err != nil {
				t.Errorf("error during rapid capacity changes: %v", err)
			}
			time.Sleep(5 * time.Millisecond)
		}
	}

	// Start concurrent capacity updates and request sending.
	numUpdaters := 3
	numRequesters := 5
	totalUpdaters := numUpdaters
	totalRequesters := numRequesters

	for i := 0; i < totalUpdaters; i++ {
		wg.Add(1)
		go updateFunc()
	}
	for i := 0; i < totalRequesters; i++ {
		wg.Add(1)
		go requestFunc()
	}

	wg.Wait()
}

// Test that the handler uses the capacity state correctly by simulating sequential requests
// and checking the allowed count matches the capacity set for that cycle.
func TestSequentialRequests(t *testing.T) {
	client := &http.Client{}
	// Simulate sequential capacity cycles.
	for capVal := 1; capVal <= 10; capVal++ {
		dynamic_limit.UpdateCapacity(capVal)
		// Create a new httptest server for each cycle to ensure a fresh state if needed.
		ts := httptest.NewServer(dynamic_limit.Handler())
		allowedCount := 0
		totalRequests := capVal + 2 // slightly over capacity
		for i := 0; i < totalRequests; i++ {
			status, err := sendRequest(client, ts.URL)
			if err != nil {
				ts.Close()
				t.Fatalf("error during sequential requests for capacity %d: %v", capVal, err)
			}
			if status == http.StatusOK {
				allowedCount++
			} else if status != http.StatusTooManyRequests {
				ts.Close()
				t.Fatalf("unexpected status code %d for capacity %d", status, capVal)
			}
		}
		ts.Close()
		if allowedCount != capVal {
			t.Errorf("For capacity %d, expected %d allowed requests but got %d", capVal, capVal, allowedCount)
		}
	}
}

// Test that when capacity is set to a negative value, the system treats it as 0 capacity.
func TestNegativeCapacity(t *testing.T) {
	dynamic_limit.UpdateCapacity(-5)

	ts := httptest.NewServer(dynamic_limit.Handler())
	defer ts.Close()
	client := ts.Client()

	status, err := sendRequest(client, ts.URL)
	if err != nil {
		t.Fatalf("error sending request with negative capacity: %v", err)
	}
	if status != http.StatusTooManyRequests {
		t.Fatalf("expected status %d for negative capacity, got %d", http.StatusTooManyRequests, status)
	}
}

// Test handling of capacity updates using string based input parsing (if applicable).
// This test simulates the scenario where a capacity might be provided in string format.
func TestCapacityStringParsing(t *testing.T) {
	// Assume that the dynamic_limit package provides a function for updating capacity from string.
	// For this test, we simulate that using an integer conversion.
	capStr := "12"
	capVal, err := strconv.Atoi(capStr)
	if err != nil {
		t.Fatalf("error converting capacity string: %v", err)
	}
	dynamic_limit.UpdateCapacity(capVal)

	ts := httptest.NewServer(dynamic_limit.Handler())
	defer ts.Close()
	client := ts.Client()

	allowedCount := 0
	for i := 0; i < capVal+2; i++ {
		status, err := sendRequest(client, ts.URL)
		if err != nil {
			t.Fatalf("error sending request in capacity string parsing test: %v", err)
		}
		if status == http.StatusOK {
			allowedCount++
		}
	}
	if allowedCount != capVal {
		t.Errorf("expected allowed requests to be %d, got %d", capVal, allowedCount)
	}
}