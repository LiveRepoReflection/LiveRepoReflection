package distributed_scheduler

import (
	"errors"
	"fmt"
	"strconv"
	"sync"
	"time"
)

type Task struct {
	ID      string
	Content string

	Status string // "pending", "assigned", "completed", "failed"
	Worker string // Worker assigned to the task
	Result string
}

type Worker struct {
	ID     string
	Active bool
}

type Scheduler struct {
	tasks       map[string]*Task
	tasksMu     sync.Mutex
	workers     map[string]*Worker
	workersMu   sync.Mutex
	workerQueue []string
	nextWorker  int
	taskCounter int
}

// NewScheduler returns a new instance of Scheduler.
func NewScheduler() *Scheduler {
	return &Scheduler{
		tasks:       make(map[string]*Task),
		workers:     make(map[string]*Worker),
		workerQueue: []string{},
		nextWorker:  0,
		taskCounter: 0,
	}
}

// RegisterWorker registers a new worker with the scheduler.
func (s *Scheduler) RegisterWorker(workerID string) error {
	s.workersMu.Lock()
	defer s.workersMu.Unlock()

	if _, exists := s.workers[workerID]; exists {
		return fmt.Errorf("worker %s already registered", workerID)
	}
	worker := &Worker{
		ID:     workerID,
		Active: true,
	}
	s.workers[workerID] = worker
	s.workerQueue = append(s.workerQueue, workerID)
	return nil
}

// ActiveWorkers returns a list of active worker IDs.
func (s *Scheduler) ActiveWorkers() []string {
	s.workersMu.Lock()
	defer s.workersMu.Unlock()

	active := make([]string, len(s.workerQueue))
	copy(active, s.workerQueue)
	return active
}

// SubmitTask submits a new task to be processed.
func (s *Scheduler) SubmitTask(content string) (string, error) {
	s.tasksMu.Lock()
	s.taskCounter++
	taskID := "task" + strconv.Itoa(s.taskCounter)
	task := &Task{
		ID:      taskID,
		Content: content,
		Status:  "pending",
	}
	s.tasks[taskID] = task
	s.tasksMu.Unlock()

	go s.assignTask(task)
	return taskID, nil
}

// assignTask assigns the given task to an active worker.
func (s *Scheduler) assignTask(task *Task) {
	workerID, err := s.pickWorker()
	if err != nil {
		// No available worker at the moment. Retry after a short delay.
		time.Sleep(50 * time.Millisecond)
		go s.assignTask(task)
		return
	}

	// Update task assignment.
	s.tasksMu.Lock()
	task.Status = "assigned"
	task.Worker = workerID
	s.tasksMu.Unlock()

	go s.processTask(task, workerID)
}

// pickWorker selects an available worker in a round-robin fashion.
func (s *Scheduler) pickWorker() (string, error) {
	s.workersMu.Lock()
	defer s.workersMu.Unlock()

	if len(s.workerQueue) == 0 {
		return "", errors.New("no available workers")
	}
	workerID := s.workerQueue[s.nextWorker%len(s.workerQueue)]
	s.nextWorker++
	return workerID, nil
}

// processTask simulates task processing.
func (s *Scheduler) processTask(task *Task, workerID string) {
	// Simulate processing time.
	time.Sleep(100 * time.Millisecond)

	s.tasksMu.Lock()
	defer s.tasksMu.Unlock()
	// Only complete the task if its status is still "assigned".
	if task.Status != "assigned" {
		return
	}
	task.Status = "completed"
	task.Result = "Processed: " + task.Content
}

// MarkWorkerFailed simulates a worker failure.
// It marks the given worker as inactive and reassigns its pending tasks.
func (s *Scheduler) MarkWorkerFailed(workerID string) error {
	s.workersMu.Lock()
	worker, exists := s.workers[workerID]
	if !exists {
		s.workersMu.Unlock()
		return fmt.Errorf("worker %s not found", workerID)
	}
	worker.Active = false
	// Remove the worker from the workerQueue.
	newQueue := make([]string, 0, len(s.workerQueue))
	for _, id := range s.workerQueue {
		if id != workerID {
			newQueue = append(newQueue, id)
		}
	}
	s.workerQueue = newQueue
	s.workersMu.Unlock()

	// Reassign tasks that were assigned to the failed worker.
	s.tasksMu.Lock()
	var tasksToReassign []*Task
	for _, task := range s.tasks {
		if task.Worker == workerID && task.Status == "assigned" {
			task.Status = "pending"
			task.Worker = ""
			tasksToReassign = append(tasksToReassign, task)
		}
	}
	s.tasksMu.Unlock()

	// Reassign each task.
	for _, t := range tasksToReassign {
		go s.assignTask(t)
	}
	return nil
}

// GetTaskStatus returns the status of a task.
func (s *Scheduler) GetTaskStatus(taskID string) (string, error) {
	s.tasksMu.Lock()
	defer s.tasksMu.Unlock()

	task, exists := s.tasks[taskID]
	if !exists {
		return "", fmt.Errorf("task %s not found", taskID)
	}
	return task.Status, nil
}

// GetTaskResult returns the result of a completed task.
func (s *Scheduler) GetTaskResult(taskID string) (string, error) {
	s.tasksMu.Lock()
	defer s.tasksMu.Unlock()

	task, exists := s.tasks[taskID]
	if !exists {
		return "", fmt.Errorf("task %s not found", taskID)
	}
	if task.Status != "completed" {
		return "", fmt.Errorf("task %s not completed yet", taskID)
	}
	return task.Result, nil
}

// GetTaskWorker returns the worker assigned to a task.
func (s *Scheduler) GetTaskWorker(taskID string) (string, error) {
	s.tasksMu.Lock()
	defer s.tasksMu.Unlock()

	task, exists := s.tasks[taskID]
	if !exists {
		return "", fmt.Errorf("task %s not found", taskID)
	}
	return task.Worker, nil
}