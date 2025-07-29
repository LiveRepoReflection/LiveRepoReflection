package lockfree_queue

import (
	"errors"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestNewQueue(t *testing.T) {
	t.Run("valid capacity", func(t *testing.T) {
		q := NewQueue[int](10)
		if q == nil {
			t.Fatal("expected non-nil queue")
		}
		if q.Cap() != 10 {
			t.Errorf("expected capacity 10, got %d", q.Cap())
		}
	})

	t.Run("invalid capacity", func(t *testing.T) {
		q := NewQueue[int](0)
		if q != nil {
			t.Error("expected nil queue for zero capacity")
		}
	})
}

func TestEnqueueDequeue(t *testing.T) {
	q := NewQueue[int](3)

	t.Run("empty queue", func(t *testing.T) {
		_, err := q.Dequeue()
		if !errors.Is(err, ErrQueueEmpty) {
			t.Errorf("expected ErrQueueEmpty, got %v", err)
		}
	})

	t.Run("single item", func(t *testing.T) {
		if err := q.Enqueue(42); err != nil {
			t.Fatalf("enqueue failed: %v", err)
		}
		if q.Len() != 1 {
			t.Errorf("expected length 1, got %d", q.Len())
		}

		val, err := q.Dequeue()
		if err != nil {
			t.Fatalf("dequeue failed: %v", err)
		}
		if val != 42 {
			t.Errorf("expected 42, got %d", val)
		}
		if q.Len() != 0 {
			t.Errorf("expected length 0, got %d", q.Len())
		}
	})

	t.Run("full queue", func(t *testing.T) {
		for i := 0; i < 3; i++ {
			if err := q.Enqueue(i); err != nil {
				t.Fatalf("enqueue failed: %v", err)
			}
		}
		if q.Len() != 3 {
			t.Errorf("expected length 3, got %d", q.Len())
		}

		err := q.Enqueue(99)
		if !errors.Is(err, ErrQueueFull) {
			t.Errorf("expected ErrQueueFull, got %v", err)
		}
	})
}

func TestConcurrentEnqueue(t *testing.T) {
	const numProducers = 10
	const itemsPerProducer = 1000
	q := NewQueue[int](numProducers * itemsPerProducer)

	var wg sync.WaitGroup
	wg.Add(numProducers)

	var enqueueErrors atomic.Int32

	for i := 0; i < numProducers; i++ {
		go func(producerID int) {
			defer wg.Done()
			for j := 0; j < itemsPerProducer; j++ {
				item := producerID*itemsPerProducer + j
				if err := q.Enqueue(item); err != nil {
					enqueueErrors.Add(1)
				}
			}
		}(i)
	}

	wg.Wait()

	if enqueueErrors.Load() > 0 {
		t.Errorf("got %d enqueue errors", enqueueErrors.Load())
	}
	if q.Len() != numProducers*itemsPerProducer {
		t.Errorf("expected %d items, got %d", numProducers*itemsPerProducer, q.Len())
	}
}

func TestConcurrentSingleConsumer(t *testing.T) {
	const numProducers = 10
	const itemsPerProducer = 1000
	q := NewQueue[int](numProducers * itemsPerProducer)

	var wg sync.WaitGroup
	wg.Add(numProducers)

	// Fill the queue
	for i := 0; i < numProducers; i++ {
		go func(producerID int) {
			defer wg.Done()
			for j := 0; j < itemsPerProducer; j++ {
				item := producerID*itemsPerProducer + j
				for {
					if err := q.Enqueue(item); err == nil {
						break
					}
					time.Sleep(time.Microsecond)
				}
			}
		}(i)
	}
	wg.Wait()

	// Single consumer
	var receivedItems []int
	var dequeueErrors atomic.Int32

	for len(receivedItems) < numProducers*itemsPerProducer {
		item, err := q.Dequeue()
		if err != nil {
			if !errors.Is(err, ErrQueueEmpty) {
				dequeueErrors.Add(1)
			}
			time.Sleep(time.Microsecond)
			continue
		}
		receivedItems = append(receivedItems, item)
	}

	if dequeueErrors.Load() > 0 {
		t.Errorf("got %d dequeue errors", dequeueErrors.Load())
	}
	if len(receivedItems) != numProducers*itemsPerProducer {
		t.Errorf("expected %d items, got %d", numProducers*itemsPerProducer, len(receivedItems))
	}
}

func TestFIFOOrder(t *testing.T) {
	const numItems = 1000
	q := NewQueue[int](numItems)

	for i := 0; i < numItems; i++ {
		if err := q.Enqueue(i); err != nil {
			t.Fatalf("enqueue failed: %v", err)
		}
	}

	for i := 0; i < numItems; i++ {
		val, err := q.Dequeue()
		if err != nil {
			t.Fatalf("dequeue failed: %v", err)
		}
		if val != i {
			t.Fatalf("expected %d, got %d", i, val)
		}
	}
}

func TestConcurrentMixed(t *testing.T) {
	const numOperations = 10000
	q := NewQueue[int](numOperations)

	var wg sync.WaitGroup
	wg.Add(2)

	// Producer
	go func() {
		defer wg.Done()
		for i := 0; i < numOperations; i++ {
			for {
				if err := q.Enqueue(i); err == nil {
					break
				}
				time.Sleep(time.Microsecond)
			}
		}
	}()

	// Consumer
	var receivedCount atomic.Int32
	go func() {
		defer wg.Done()
		for receivedCount.Load() < numOperations {
			_, err := q.Dequeue()
			if err == nil {
				receivedCount.Add(1)
			}
		}
	}()

	wg.Wait()

	if receivedCount.Load() != numOperations {
		t.Errorf("expected %d items, got %d", numOperations, receivedCount.Load())
	}
}