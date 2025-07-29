package dist_prioq

import (
	"math/rand"
	"strconv"
	"sync"
	"testing"
	"time"
)

// Assume the following interface is provided by the dist_prioq package:
//
// type Item struct {
//     Value     string
//     Priority  int
//     Timestamp int64
// }
//
// // DistributedPrioQueue represents the distributed priority queue system.
// type DistributedPrioQueue interface {
//     Enqueue(item Item) error
//     Dequeue() (Item, error)
//     Stop()
//     // FailNode simulates a failure of a node identified by its index.
//     FailNode(nodeID int) error
// }
//
// // InitializeSystem initializes the distributed priority queue with numNodes.
// // It returns a DistributedPrioQueue instance and an error if initialization fails.
// func InitializeSystem(numNodes int) (DistributedPrioQueue, error)

func createTestItem(value string, priority int) Item {
	return Item{
		Value:     value,
		Priority:  priority,
		Timestamp: time.Now().UnixNano(),
	}
}

func TestSingleEnqueueDequeue(t *testing.T) {
	dpq, err := InitializeSystem(1)
	if err != nil {
		t.Fatalf("Failed to initialize system: %v", err)
	}
	defer dpq.Stop()

	item := createTestItem("test_item", 10)
	err = dpq.Enqueue(item)
	if err != nil {
		t.Fatalf("Failed to enqueue item: %v", err)
	}

	dequeued, err := dpq.Dequeue()
	if err != nil {
		t.Fatalf("Failed to dequeue item: %v", err)
	}

	if dequeued.Value != item.Value || dequeued.Priority != item.Priority {
		t.Fatalf("Expected item %+v, got %+v", item, dequeued)
	}
}

func TestPriorityOrdering(t *testing.T) {
	dpq, err := InitializeSystem(3)
	if err != nil {
		t.Fatalf("Failed to initialize system: %v", err)
	}
	defer dpq.Stop()

	items := []Item{
		createTestItem("low", 1),
		createTestItem("medium", 5),
		createTestItem("high", 10),
		createTestItem("medium2", 5),
	}

	for _, item := range items {
		if err := dpq.Enqueue(item); err != nil {
			t.Fatalf("Failed to enqueue item %+v: %v", item, err)
		}
	}

	// Expected order: highest priority first; for equal priorities, FIFO order applies.
	expectedOrder := []string{"high", "medium", "medium2", "low"}
	for _, expected := range expectedOrder {
		dequeued, err := dpq.Dequeue()
		if err != nil {
			t.Fatalf("Failed to dequeue item: %v", err)
		}
		if dequeued.Value != expected {
			t.Fatalf("Expected item %s but got %s", expected, dequeued.Value)
		}
	}
}

func TestConcurrentEnqueueDequeue(t *testing.T) {
	dpq, err := InitializeSystem(5)
	if err != nil {
		t.Fatalf("Failed to initialize system: %v", err)
	}
	defer dpq.Stop()

	const numItems = 100
	var wg sync.WaitGroup

	// Concurrent Enqueue
	for i := 0; i < numItems; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			item := createTestItem("item"+strconv.Itoa(i), rand.Intn(100))
			if err := dpq.Enqueue(item); err != nil {
				t.Errorf("Enqueue failed for item %d: %v", i, err)
			}
		}(i)
	}
	wg.Wait()

	// Concurrent Dequeue
	var dqWg sync.WaitGroup
	results := make(chan Item, numItems)
	for i := 0; i < 10; i++ {
		dqWg.Add(1)
		go func() {
			defer dqWg.Done()
			for {
				item, err := dpq.Dequeue()
				if err != nil {
					// Assume an error indicates that the queue might be empty
					return
				}
				results <- item
			}
		}()
	}

	// Allow time for dequeue operations to process the queue.
	time.Sleep(2 * time.Second)
	dpq.Stop()
	dqWg.Wait()
	close(results)

	dequeuedCount := 0
	for range results {
		dequeuedCount++
	}

	if dequeuedCount != numItems {
		t.Fatalf("Expected %d items to be dequeued, but got %d", numItems, dequeuedCount)
	}
}

func TestReplicationFaultTolerance(t *testing.T) {
	dpq, err := InitializeSystem(4)
	if err != nil {
		t.Fatalf("Failed to initialize system: %v", err)
	}

	items := []Item{
		createTestItem("first", 7),
		createTestItem("second", 3),
		createTestItem("third", 9),
	}

	for _, item := range items {
		if err := dpq.Enqueue(item); err != nil {
			t.Fatalf("Failed to enqueue item %+v: %v", item, err)
		}
	}

	// Simulate a node failure (for example, node with id 2)
	if err := dpq.FailNode(2); err != nil {
		t.Fatalf("Failed to simulate node failure: %v", err)
	}

	// After node failure, ensure that replicated items are still dequeued in correct order.
	expectedOrder := []string{"third", "first", "second"}
	for _, expected := range expectedOrder {
		item, err := dpq.Dequeue()
		if err != nil {
			t.Fatalf("Failed to dequeue after node failure: %v", err)
		}
		if item.Value != expected {
			t.Fatalf("Expected item %s, but got %s", expected, item.Value)
		}
	}

	dpq.Stop()
}