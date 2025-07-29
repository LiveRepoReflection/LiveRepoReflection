package microservice_router

import (
	"errors"
	"sync"
	"testing"
	"time"
)

// fakeRegistry implements the ServiceRegistry interface.
type fakeRegistry struct {
	mu        sync.Mutex
	endpoints map[string][]string
}

func (r *fakeRegistry) GetServiceEndpoints(serviceID string) []string {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.endpoints[serviceID]
}

// fakeSendRequestFunc defines the function signature for our fake sendRequest.
type fakeSendRequestFunc func(endpoint string, payload []byte) ([]byte, error)

// TestRouterSuccess tests a successful routing scenario.
func TestRouterSuccess(t *testing.T) {
	// Set up a fake registry with one endpoint.
	reg := &fakeRegistry{
		endpoints: map[string][]string{
			"test_service": {"endpoint1"},
		},
	}
	// Create a router instance with a reasonable timeout.
	router := NewRouter(reg, 100*time.Millisecond)
	// Override sendRequest with a fake function that always succeeds.
	router.sendRequest = func(endpoint string, payload []byte) ([]byte, error) {
		if endpoint != "endpoint1" {
			return nil, errors.New("unexpected endpoint")
		}
		return []byte("success"), nil
	}

	resp, err := router.RouteRequest("test_service", []byte("request"))
	if err != nil {
		t.Fatalf("expected success, got error: %v", err)
	}
	expected := "success"
	if string(resp) != expected {
		t.Fatalf("expected %q, got %q", expected, string(resp))
	}
}

// TestRouterNoEndpoints tests the scenario when no endpoints are available for a service.
func TestRouterNoEndpoints(t *testing.T) {
	reg := &fakeRegistry{
		endpoints: map[string][]string{
			"other_service": {"endpoint1"},
		},
	}
	router := NewRouter(reg, 100*time.Millisecond)
	// Override sendRequest even though it should never be called.
	router.sendRequest = func(endpoint string, payload []byte) ([]byte, error) {
		return []byte("should not be called"), nil
	}

	_, err := router.RouteRequest("test_service", []byte("request"))
	if err == nil {
		t.Fatalf("expected error due to no available endpoints, got success")
	}
}

// TestRouterRoundRobin tests the round-robin load balancing mechanism.
func TestRouterRoundRobin(t *testing.T) {
	// Set up a fake registry with two endpoints.
	reg := &fakeRegistry{
		endpoints: map[string][]string{
			"test_service": {"endpoint1", "endpoint2"},
		},
	}
	router := NewRouter(reg, 100*time.Millisecond)

	// Create a counter to record the number of times each endpoint is used.
	var mu sync.Mutex
	callCount := make(map[string]int)

	router.sendRequest = func(endpoint string, payload []byte) ([]byte, error) {
		mu.Lock()
		callCount[endpoint]++
		mu.Unlock()
		return []byte("ok"), nil
	}

	// Make several requests and verify round-robin distribution.
	totalCalls := 10
	for i := 0; i < totalCalls; i++ {
		_, err := router.RouteRequest("test_service", []byte("request"))
		if err != nil {
			t.Fatalf("unexpected error on call %d: %v", i, err)
		}
	}

	// Expect near-even distribution.
	mu.Lock()
	defer mu.Unlock()
	c1 := callCount["endpoint1"]
	c2 := callCount["endpoint2"]
	if c1+c2 != totalCalls {
		t.Fatalf("total calls mismatch: got %d, expected %d", c1+c2, totalCalls)
	}
	// The difference should not be more than 1.
	if diff := c1 - c2; diff > 1 || diff < -1 {
		t.Fatalf("round robin distribution failed: endpoint1=%d, endpoint2=%d", c1, c2)
	}
}

// TestRouterRetry tests that the router retries on failure.
func TestRouterRetry(t *testing.T) {
	// Set up a registry with two endpoints.
	reg := &fakeRegistry{
		endpoints: map[string][]string{
			"test_service": {"fail_endpoint", "success_endpoint"},
		},
	}
	router := NewRouter(reg, 100*time.Millisecond)

	// Use a counter to simulate that the first endpoint fails, and the second succeeds.
	var mu sync.Mutex
	callCount := make(map[string]int)

	router.sendRequest = func(endpoint string, payload []byte) ([]byte, error) {
		mu.Lock()
		callCount[endpoint]++
		mu.Unlock()
		if endpoint == "fail_endpoint" {
			return nil, errors.New("endpoint failure")
		}
		return []byte("retry_success"), nil
	}

	resp, err := router.RouteRequest("test_service", []byte("request"))
	if err != nil {
		t.Fatalf("expected retry to succeed, got error: %v", err)
	}
	if string(resp) != "retry_success" {
		t.Fatalf("expected response %q, got %q", "retry_success", string(resp))
	}

	mu.Lock()
	defer mu.Unlock()
	if callCount["fail_endpoint"] < 1 {
		t.Fatalf("expected at least one call to fail_endpoint")
	}
	if callCount["success_endpoint"] < 1 {
		t.Fatalf("expected at least one call to success_endpoint")
	}
}

// TestRouterTimeout tests that the router respects the timeout setting.
func TestRouterTimeout(t *testing.T) {
	reg := &fakeRegistry{
		endpoints: map[string][]string{
			"test_service": {"slow_endpoint"},
		},
	}
	// Use a timeout that is shorter than the delay in fakeSendRequest.
	router := NewRouter(reg, 50*time.Millisecond)
	router.sendRequest = func(endpoint string, payload []byte) ([]byte, error) {
		time.Sleep(100 * time.Millisecond)
		return []byte("late_response"), nil
	}

	_, err := router.RouteRequest("test_service", []byte("request"))
	if err == nil {
		t.Fatalf("expected timeout error, got success")
	}
}

// TestRouterConcurrency tests handling a large number of concurrent requests.
func TestRouterConcurrency(t *testing.T) {
	reg := &fakeRegistry{
		endpoints: map[string][]string{
			"test_service": {"endpoint1", "endpoint2", "endpoint3"},
		},
	}
	router := NewRouter(reg, 200*time.Millisecond)
	// For this test, fake sendRequest always returns success.
	router.sendRequest = func(endpoint string, payload []byte) ([]byte, error) {
		return []byte("concurrent_response"), nil
	}

	var wg sync.WaitGroup
	numRequests := 100
	errChan := make(chan error, numRequests)

	for i := 0; i < numRequests; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_, err := router.RouteRequest("test_service", []byte("request"))
			if err != nil {
				errChan <- err
			}
		}()
	}
	wg.Wait()
	close(errChan)

	for err := range errChan {
		t.Errorf("concurrent request error: %v", err)
	}
}