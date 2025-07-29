package distributed_scheduler_test

import (
	"sync"
	"testing"
	"time"

	"distributed_scheduler"
)

func TestWorkerRegistration(t *testing.T) {
	sched := distributed_scheduler.NewScheduler()
	err := sched.RegisterWorker("worker1")
	if err != nil {
		t.Fatalf("expected no error on registering worker, got: %v", err)
	}

	workers := sched.ActiveWorkers()
	if len(workers) != 1 || workers[0] != "worker1" {
		t.Fatalf("expected active worker 'worker1', got: %v", workers)
	}
}

func TestTaskSubmissionAndCompletion(t *testing.T) {
	sched := distributed_scheduler.NewScheduler()
	err := sched.RegisterWorker("worker1")
	if err != nil {
		t.Fatalf("failed to register worker: %v", err)
	}

	taskID, err := sched.SubmitTask("dummy task")
	if err != nil {
		t.Fatalf("failed to submit task: %v", err)
	}

	// Wait briefly for the task to be picked and processed by the worker.
	time.Sleep(100 * time.Millisecond)

	status, err := sched.GetTaskStatus(taskID)
	if err != nil {
		t.Fatalf("failed to get task status: %v", err)
	}
	if status != "completed" {
		t.Fatalf("expected task status 'completed', got: %s", status)
	}

	result, err := sched.GetTaskResult(taskID)
	if err != nil {
		t.Fatalf("failed to get task result: %v", err)
	}
	if result == "" {
		t.Fatalf("expected non-empty task result")
	}
}

func TestFaultTolerance(t *testing.T) {
	sched := distributed_scheduler.NewScheduler()
	err := sched.RegisterWorker("worker1")
	if err != nil {
		t.Fatalf("failed to register worker1: %v", err)
	}
	err = sched.RegisterWorker("worker2")
	if err != nil {
		t.Fatalf("failed to register worker2: %v", err)
	}

	taskID, err := sched.SubmitTask("fault tolerant task")
	if err != nil {
		t.Fatalf("failed to submit task: %v", err)
	}

	// Wait briefly for the task to be assigned.
	time.Sleep(50 * time.Millisecond)

	assignedWorker, err := sched.GetTaskWorker(taskID)
	if err != nil {
		t.Fatalf("failed to get assigned worker for task: %v", err)
	}

	// Simulate worker failure.
	sched.MarkWorkerFailed(assignedWorker)

	// Allow time for fault tolerance mechanism to reassign and complete the task.
	time.Sleep(150 * time.Millisecond)

	status, err := sched.GetTaskStatus(taskID)
	if err != nil {
		t.Fatalf("failed to get task status after failure: %v", err)
	}
	if status != "completed" {
		t.Fatalf("expected task status 'completed' after failure recovery, got: %s", status)
	}
}

func TestConcurrentTaskProcessing(t *testing.T) {
	sched := distributed_scheduler.NewScheduler()
	workerIDs := []string{"worker1", "worker2", "worker3", "worker4", "worker5"}
	for _, id := range workerIDs {
		if err := sched.RegisterWorker(id); err != nil {
			t.Fatalf("failed to register worker %s: %v", id, err)
		}
	}

	var wg sync.WaitGroup
	numTasks := 20
	taskIDs := make([]string, numTasks)

	// Submit tasks concurrently.
	for i := 0; i < numTasks; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			taskID, err := sched.SubmitTask("concurrent task")
			if err != nil {
				t.Errorf("failed to submit task %d: %v", i, err)
				return
			}
			taskIDs[i] = taskID
		}(i)
	}
	wg.Wait()

	// Allow time for all tasks to be processed.
	time.Sleep(300 * time.Millisecond)

	// Verify that all tasks have been completed.
	for i, id := range taskIDs {
		status, err := sched.GetTaskStatus(id)
		if err != nil {
			t.Errorf("failed to get status for task %d: %v", i, err)
			continue
		}
		if status != "completed" {
			t.Errorf("expected task %d to be 'completed', got: %s", i, status)
		}
	}
}