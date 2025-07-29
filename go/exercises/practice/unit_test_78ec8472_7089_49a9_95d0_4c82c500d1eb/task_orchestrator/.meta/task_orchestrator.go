package task_orchestrator

import (
	"context"
	"errors"
	"sync"
	"time"
)

type TaskStatus string

const (
	StatusPending   TaskStatus = "pending"
	StatusRunning   TaskStatus = "running"
	StatusCompleted TaskStatus = "completed"
	StatusFailed    TaskStatus = "failed"
)

type Task struct {
	ID           string
	Dependencies []string
	Status       TaskStatus
	RetryCount   int
	Worker       string
}

type Worker struct {
	ID        string
	Available bool
	mutex     sync.Mutex
}

type Orchestrator struct {
	tasks        map[string]*Task
	workers      map[string]*Worker
	maxRetries   int
	simulateFunc func(string) bool
	taskMutex    sync.RWMutex
	ctx          context.Context
	cancel       context.CancelFunc
}

func NewOrchestrator(taskDeps map[string][]string, workerIDs []string, maxRetries int, simulateFunc func(string) bool) *Orchestrator {
	ctx, cancel := context.WithCancel(context.Background())
	o := &Orchestrator{
		tasks:        make(map[string]*Task),
		workers:      make(map[string]*Worker),
		maxRetries:   maxRetries,
		simulateFunc: simulateFunc,
		ctx:          ctx,
		cancel:       cancel,
	}

	// Initialize tasks
	for taskID, deps := range taskDeps {
		o.tasks[taskID] = &Task{
			ID:           taskID,
			Dependencies: deps,
			Status:       StatusPending,
			RetryCount:   0,
		}
	}

	// Initialize workers
	for _, workerID := range workerIDs {
		o.workers[workerID] = &Worker{
			ID:        workerID,
			Available: true,
		}
	}

	return o
}

func (o *Orchestrator) Cancel() {
	o.cancel()
}

func (o *Orchestrator) detectCycle(taskID string, visited map[string]bool, stack map[string]bool) bool {
	visited[taskID] = true
	stack[taskID] = true

	for _, depID := range o.tasks[taskID].Dependencies {
		if !visited[depID] {
			if o.detectCycle(depID, visited, stack) {
				return true
			}
		} else if stack[depID] {
			return true
		}
	}

	stack[taskID] = false
	return false
}

func (o *Orchestrator) hasCyclicDependencies() bool {
	visited := make(map[string]bool)
	stack := make(map[string]bool)

	for taskID := range o.tasks {
		if !visited[taskID] {
			if o.detectCycle(taskID, visited, stack) {
				return true
			}
		}
	}
	return false
}

func (o *Orchestrator) isTaskReady(taskID string) bool {
	task := o.tasks[taskID]
	if task.Status != StatusPending {
		return false
	}

	for _, depID := range task.Dependencies {
		if o.tasks[depID].Status != StatusCompleted {
			return false
		}
	}
	return true
}

func (o *Orchestrator) getAvailableWorker() *Worker {
	for _, worker := range o.workers {
		worker.mutex.Lock()
		if worker.Available {
			worker.Available = false
			worker.mutex.Unlock()
			return worker
		}
		worker.mutex.Unlock()
	}
	return nil
}

func (o *Orchestrator) releaseWorker(worker *Worker) {
	worker.mutex.Lock()
	worker.Available = true
	worker.mutex.Unlock()
}

func (o *Orchestrator) executeTask(task *Task, worker *Worker) error {
	o.taskMutex.Lock()
	task.Status = StatusRunning
	task.Worker = worker.ID
	o.taskMutex.Unlock()

	success := o.simulateFunc(task.ID)

	o.taskMutex.Lock()
	defer o.taskMutex.Unlock()

	if success {
		task.Status = StatusCompleted
		return nil
	}

	task.RetryCount++
	if task.RetryCount >= o.maxRetries {
		task.Status = StatusFailed
		return errors.New("task failed after max retries")
	}

	task.Status = StatusPending
	return errors.New("task failed, will retry")
}

func (o *Orchestrator) Execute() (map[string]string, error) {
	if o.hasCyclicDependencies() {
		return nil, errors.New("cyclic dependencies detected")
	}

	var wg sync.WaitGroup
	errorChan := make(chan error, len(o.tasks))

	for {
		select {
		case <-o.ctx.Done():
			return nil, errors.New("execution cancelled")
		default:
			allCompleted := true
			anyProgress := false

			for taskID, task := range o.tasks {
				if task.Status == StatusCompleted || task.Status == StatusRunning {
					continue
				}

				if task.Status == StatusFailed {
					return o.getStatusMap(), errors.New("task execution failed")
				}

				allCompleted = false

				if o.isTaskReady(taskID) {
					worker := o.getAvailableWorker()
					if worker != nil {
						anyProgress = true
						wg.Add(1)
						go func(t *Task, w *Worker) {
							defer wg.Done()
							defer o.releaseWorker(w)

							if err := o.executeTask(t, w); err != nil {
								errorChan <- err
							}
						}(task, worker)
					}
				}
			}

			if allCompleted {
				wg.Wait()
				return o.getStatusMap(), nil
			}

			if !anyProgress {
				time.Sleep(100 * time.Millisecond)
			}

			select {
			case err := <-errorChan:
				if err.Error() == "task failed after max retries" {
					return o.getStatusMap(), err
				}
			default:
			}
		}
	}
}

func (o *Orchestrator) getStatusMap() map[string]string {
	o.taskMutex.RLock()
	defer o.taskMutex.RUnlock()

	result := make(map[string]string)
	for taskID, task := range o.tasks {
		result[taskID] = string(task.Status)
	}
	return result
}