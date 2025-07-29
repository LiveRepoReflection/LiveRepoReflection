package dynamic_rmq

import (
	"math"
	"math/rand"
	"sync"
	"testing"
	"time"
)

// TestBasicQuery checks that Query returns the correct minimum value for various ranges.
func TestBasicQuery(t *testing.T) {
	arr := []int{5, 2, 8, 3, 9, 1, 7}
	rmq, err := NewDynamicRMQ(arr)
	if err != nil {
		t.Fatalf("Failed to initialize RMQ: %v", err)
	}

	// Query the entire array.
	res, err := rmq.Query(0, len(arr)-1)
	if err != nil {
		t.Fatalf("Query returned error: %v", err)
	}
	if res != 1 {
		t.Fatalf("Expected minimum 1, got %d", res)
	}

	// Query a subarray from index 1 to 3.
	res, err = rmq.Query(1, 3)
	if err != nil {
		t.Fatalf("Query returned error: %v", err)
	}
	if res != 2 {
		t.Fatalf("Expected minimum 2, got %d", res)
	}

	// Query a subarray from index 3 to 5.
	res, err = rmq.Query(3, 5)
	if err != nil {
		t.Fatalf("Query returned error: %v", err)
	}
	if res != 1 {
		t.Fatalf("Expected minimum 1, got %d", res)
	}
}

// TestUpdate verifies that updating elements correctly modifies the result of subsequent queries.
func TestUpdate(t *testing.T) {
	arr := []int{5, 2, 8, 3, 9, 1, 7}
	rmq, err := NewDynamicRMQ(arr)
	if err != nil {
		t.Fatalf("Failed to initialize RMQ: %v", err)
	}

	// Update index 5 from 1 to 10.
	err = rmq.Update(5, 10)
	if err != nil {
		t.Fatalf("Update returned error: %v", err)
	}
	res, err := rmq.Query(0, len(arr)-1)
	if err != nil {
		t.Fatalf("Query returned error: %v", err)
	}
	// The new array is [5,2,8,3,9,10,7], so the minimum should be 2.
	if res != 2 {
		t.Fatalf("Expected minimum 2 after update, got %d", res)
	}

	// Update index 1 from 2 to 0.
	err = rmq.Update(1, 0)
	if err != nil {
		t.Fatalf("Update returned error: %v", err)
	}
	res, err = rmq.Query(0, len(arr)-1)
	if err != nil {
		t.Fatalf("Query returned error: %v", err)
	}
	// The new array is [5,0,8,3,9,10,7], so the minimum should be 0.
	if res != 0 {
		t.Fatalf("Expected minimum 0 after update, got %d", res)
	}
}

// TestInvalidOperations ensures that queries and updates with invalid indices return errors appropriately.
func TestInvalidOperations(t *testing.T) {
	arr := []int{5, 2, 8}
	rmq, err := NewDynamicRMQ(arr)
	if err != nil {
		t.Fatalf("Failed to initialize RMQ: %v", err)
	}

	// Query with L > R.
	_, err = rmq.Query(2, 1)
	if err == nil {
		t.Fatalf("Expected error for Query with L greater than R")
	}

	// Query with a negative index.
	_, err = rmq.Query(-1, 2)
	if err == nil {
		t.Fatalf("Expected error for Query with negative index")
	}

	// Query with an out-of-bound index.
	_, err = rmq.Query(0, 3)
	if err == nil {
		t.Fatalf("Expected error for Query with index out-of-bound")
	}

	// Update with a negative index.
	err = rmq.Update(-1, 10)
	if err == nil {
		t.Fatalf("Expected error for Update with negative index")
	}

	// Update with an out-of-bound index.
	err = rmq.Update(3, 10)
	if err == nil {
		t.Fatalf("Expected error for Update with index out-of-bound")
	}
}

// TestConcurrentQueriesAndUpdates tests the RMQ under high concurrency conditions.
func TestConcurrentQueriesAndUpdates(t *testing.T) {
	// Seed the random number generator.
	rand.Seed(time.Now().UnixNano())

	// Create a large array for concurrent testing.
	size := 1000
	arr := make([]int, size)
	for i := 0; i < size; i++ {
		arr[i] = rand.Intn(1000)
	}

	rmq, err := NewDynamicRMQ(arr)
	if err != nil {
		t.Fatalf("Failed to initialize RMQ: %v", err)
	}

	var wg sync.WaitGroup

	// Launch concurrent query goroutines.
	queryGoroutines := 100
	for i := 0; i < queryGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 1000; j++ {
				l := rand.Intn(size)
				r := rand.Intn(size)
				if l > r {
					l, r = r, l
				}
				// Ignore the result and error for this stress test.
				_, _ = rmq.Query(l, r)
			}
		}()
	}

	// Launch concurrent update goroutines.
	updateGoroutines := 100
	for i := 0; i < updateGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 1000; j++ {
				idx := rand.Intn(size)
				newVal := rand.Intn(1000)
				_ = rmq.Update(idx, newVal)
			}
		}()
	}

	wg.Wait()

	// Perform a final query over the full range to ensure the RMQ is still functional.
	res, err := rmq.Query(0, size-1)
	if err != nil {
		t.Fatalf("Final Query returned error: %v", err)
	}
	// The result should be within a plausible range.
	if res < 0 || res > math.MaxInt32 {
		t.Fatalf("Final Query returned an implausible value: %d", res)
	}
}