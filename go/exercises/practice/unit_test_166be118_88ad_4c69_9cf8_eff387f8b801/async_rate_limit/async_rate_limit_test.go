package async_rate_limit

import (
	"sync"
	"testing"
	"time"
)

func TestPriorityExecutionOrder(t *testing.T) {
	// Create a rate limiter with a high rate so that delays do not interfere with ordering.
	rl := NewRateLimiter(1000)
	defer rl.Shutdown(5 * time.Second)

	var mu sync.Mutex
	executed := []int{}
	wg := sync.WaitGroup{}

	// Submit tasks with various priorities.
	// Tasks: index 0 has priority 5, index 1 has priority 3, index 2 has priority 4, index 3 has priority 1, index 4 has priority 2.
	priorities := []int{5, 3, 4, 1, 2}
	for i, p := range priorities {
		wg.Add(1)
		index := i
		priority := p
		err := rl.Submit(func() {
			mu.Lock()
			executed = append(executed, index)
			mu.Unlock()
			wg.Done()
		}, priority)
		if err != nil {
			t.Fatalf("Submit failed: %v", err)
		}
	}

	wg.Wait()

	// Expected order based on priority: index 3 (priority 1), index 4 (priority 2), index 1 (priority 3), index 2 (priority 4), index 0 (priority 5)
	expectedOrder := []int{3, 4, 1, 2, 0}
	if len(executed) != len(expectedOrder) {
		t.Fatalf("Expected %d executed tasks, got %d", len(expectedOrder), len(executed))
	}
	for i, v := range expectedOrder {
		if executed[i] != v {
			t.Errorf("At position %d, expected task with index %d, got %d", i, v, executed[i])
		}
	}
}

func TestRateEnforcement(t *testing.T) {
	// Set up a rate limiter with a specific rate, e.g., 5 tasks per second.
	rate := 5
	rl := NewRateLimiter(rate)
	defer rl.Shutdown(5 * time.Second)

	var mu sync.Mutex
	executedTimes := []time.Time{}
	wg := sync.WaitGroup{}
	numTasks := 10

	for i := 0; i < numTasks; i++ {
		wg.Add(1)
		err := rl.Submit(func() {
			mu.Lock()
			executedTimes = append(executedTimes, time.Now())
			mu.Unlock()
			wg.Done()
		}, 1)
		if err != nil {
			t.Fatalf("Submit failed: %v", err)
		}
	}

	wg.Wait()

	if len(executedTimes) < 2 {
		t.Fatalf("Not enough tasks to measure rate")
	}

	// Compute average interval between task executions.
	var totalInterval time.Duration
	for i := 1; i < len(executedTimes); i++ {
		interval := executedTimes[i].Sub(executedTimes[i-1])
		totalInterval += interval
	}
	avgInterval := totalInterval / time.Duration(len(executedTimes)-1)
	expectedInterval := time.Second / time.Duration(rate)

	// Allow a 10% tolerance.
	tolerance := expectedInterval / 10
	if avgInterval < expectedInterval-tolerance || avgInterval > expectedInterval+tolerance {
		t.Errorf("Expected average interval around %v, got %v", expectedInterval, avgInterval)
	}
}

func TestConcurrentSubmissions(t *testing.T) {
	// Test high concurrency and non-blocking submission.
	rate := 1000
	rl := NewRateLimiter(rate)
	defer rl.Shutdown(5 * time.Second)

	var mu sync.Mutex
	counter := 0
	totalTasks := 1000
	wg := sync.WaitGroup{}

	for i := 0; i < totalTasks; i++ {
		wg.Add(1)
		go func() {
			err := rl.Submit(func() {
				mu.Lock()
				counter++
				mu.Unlock()
				wg.Done()
			}, 1)
			if err != nil {
				t.Errorf("Submit failed: %v", err)
				wg.Done()
			}
		}()
	}

	wg.Wait()

	if counter != totalTasks {
		t.Errorf("Expected %d tasks to be executed, got %d", totalTasks, counter)
	}
}

func TestShutdownPreventsSubmission(t *testing.T) {
	rl := NewRateLimiter(1000)
	// Initiate shutdown in a separate goroutine.
	go func() {
		err := rl.Shutdown(5 * time.Second)
		if err != nil {
			t.Errorf("Shutdown failed: %v", err)
		}
	}()

	// Give some time for shutdown to start.
	time.Sleep(100 * time.Millisecond)

	// Attempt to submit a new task after shutdown has been initiated.
	err := rl.Submit(func() {}, 1)
	if err == nil {
		t.Errorf("Expected error when submitting task after shutdown, got nil")
	}
}