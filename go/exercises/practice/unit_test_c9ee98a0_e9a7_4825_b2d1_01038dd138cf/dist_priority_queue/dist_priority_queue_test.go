package distpriorityqueue_test

import (
	"errors"
	"math/rand"
	"strconv"
	"sync"
	"testing"
	"time"

	"dist_priority_queue/distpriorityqueue"
)

func newTestQueue() *distpriorityqueue.Queue {
	config := distpriorityqueue.Config{
		ReplicationFactor: 2,
		RetrieveTimeout:   500 * time.Millisecond,
		PersistencePath:   "./tmp", // temporary persistence directory for tests
	}
	// NewQueue creates and initializes a new distributed priority queue instance.
	return distpriorityqueue.NewQueue(config)
}

func TestBasicSubmitAndRetrieve(t *testing.T) {
	q := newTestQueue()
	defer q.Shutdown()

	task := distpriorityqueue.Task{
		ID:       "task1",
		Priority: 10,
		Payload:  "Test Payload",
	}

	err := q.SubmitTask(task)
	if err != nil {
		t.Fatalf("SubmitTask failed: %v", err)
	}

	retrievedTask, err := q.RetrieveTask(1 * time.Second)
	if err != nil {
		t.Fatalf("RetrieveTask failed: %v", err)
	}

	if retrievedTask.ID != task.ID {
		t.Errorf("Expected task ID %s but got %s", task.ID, retrievedTask.ID)
	}
}

func TestPriorityOrdering(t *testing.T) {
	q := newTestQueue()
	defer q.Shutdown()

	tasks := []distpriorityqueue.Task{
		{ID: "task1", Priority: 5, Payload: "Payload 1"},
		{ID: "task2", Priority: 2, Payload: "Payload 2"},
		{ID: "task3", Priority: 8, Payload: "Payload 3"},
		{ID: "task4", Priority: 1, Payload: "Payload 4"},
		{ID: "task5", Priority: 3, Payload: "Payload 5"},
	}

	for _, task := range tasks {
		if err := q.SubmitTask(task); err != nil {
			t.Fatalf("SubmitTask error: %v", err)
		}
	}

	// Expected order: task4, task2, task5, task1, task3 based on lowest priority number first.
	expectedOrder := []string{"task4", "task2", "task5", "task1", "task3"}
	for i, expID := range expectedOrder {
		tsk, err := q.RetrieveTask(1 * time.Second)
		if err != nil {
			t.Fatalf("RetrieveTask error: %v", err)
		}
		if tsk.ID != expID {
			t.Fatalf("At index %d expected task %s but got %s", i, expID, tsk.ID)
		}
	}
}

func TestRetrieveTimeout(t *testing.T) {
	q := newTestQueue()
	defer q.Shutdown()

	start := time.Now()
	_, err := q.RetrieveTask(200 * time.Millisecond)
	elapsed := time.Since(start)
	if err == nil {
		t.Fatalf("Expected timeout error but got none")
	}
	if elapsed < 200*time.Millisecond {
		t.Errorf("RetrieveTask returned before timeout elapsed, elapsed: %v", elapsed)
	}
	if !errors.Is(err, distpriorityqueue.ErrTimeout) {
		t.Errorf("Expected timeout error, got: %v", err)
	}
}

func TestConcurrentSubmitAndRetrieve(t *testing.T) {
	q := newTestQueue()
	defer q.Shutdown()

	totalTasks := 100
	var wg sync.WaitGroup
	retrievedIDs := make([]string, 0, totalTasks)
	var mtx sync.Mutex

	// Producer goroutine submits tasks concurrently.
	wg.Add(1)
	go func() {
		defer wg.Done()
		for i := 0; i < totalTasks; i++ {
			task := distpriorityqueue.Task{
				ID:       "ctask_" + strconv.Itoa(i),
				Priority: rand.Intn(100),
				Payload:  "Concurrent Payload " + strconv.Itoa(i),
			}
			if err := q.SubmitTask(task); err != nil {
				t.Errorf("SubmitTask error: %v", err)
			}
			time.Sleep(5 * time.Millisecond)
		}
	}()

	// Multiple worker goroutines retrieve tasks concurrently.
	workerCount := 5
	var workerWG sync.WaitGroup
	for i := 0; i < workerCount; i++ {
		workerWG.Add(1)
		go func(workerID int) {
			defer workerWG.Done()
			for {
				task, err := q.RetrieveTask(500 * time.Millisecond)
				if err != nil {
					if errors.Is(err, distpriorityqueue.ErrTimeout) {
						return
					}
					t.Errorf("Worker %d RetrieveTask error: %v", workerID, err)
					return
				}
				mtx.Lock()
				retrievedIDs = append(retrievedIDs, task.ID)
				mtx.Unlock()
				time.Sleep(10 * time.Millisecond)
			}
		}(i)
	}

	wg.Wait()
	workerWG.Wait()

	if len(retrievedIDs) != totalTasks {
		t.Errorf("Expected %d tasks retrieved, got %d", totalTasks, len(retrievedIDs))
	}
}

func TestDeadLetterQueue(t *testing.T) {
	q := newTestQueue()
	defer q.Shutdown()

	task := distpriorityqueue.Task{
		ID:       "dlq_task",
		Priority: 10,
		Payload:  "DLQ Test Payload",
	}

	if err := q.SubmitTask(task); err != nil {
		t.Fatalf("SubmitTask error: %v", err)
	}

	retrievedTask, err := q.RetrieveTask(1 * time.Second)
	if err != nil {
		t.Fatalf("RetrieveTask error: %v", err)
	}
	if retrievedTask.ID != task.ID {
		t.Fatalf("Expected task ID %s but got %s", task.ID, retrievedTask.ID)
	}

	// Simulate processing failure.
	if err := q.ReportTaskFailure(retrievedTask.ID); err != nil {
		t.Fatalf("ReportTaskFailure error: %v", err)
	}

	// Verify that task is moved to the Dead Letter Queue.
	dlqTasks := q.GetDLQ()
	found := false
	for _, tsk := range dlqTasks {
		if tsk.ID == task.ID {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("Task %s was not found in DLQ after failure", task.ID)
	}
}