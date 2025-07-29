package distpriorityqueue

import (
	"container/heap"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// ErrTimeout is returned when RetrieveTask times out.
var ErrTimeout = errors.New("retrieve task timed out")

// Task represents a unit of work.
type Task struct {
	ID        string
	Priority  int
	Payload   string
	timestamp time.Time // internal timestamp for tie-breaking
}

// Config holds configuration options for the Queue.
type Config struct {
	ReplicationFactor int
	RetrieveTimeout   time.Duration
	PersistencePath   string
}

// Queue represents the distributed priority queue.
type Queue struct {
	config      Config
	tasks       taskHeap
	mutex       sync.Mutex
	cond        *sync.Cond
	dlq         []Task
	inFlight    map[string]Task
	persistFile *os.File
	shutdown    bool
}

// NewQueue creates a new Queue instance with the provided configuration.
func NewQueue(config Config) *Queue {
	// Ensure persistence directory exists.
	err := os.MkdirAll(config.PersistencePath, os.ModePerm)
	if err != nil {
		panic(fmt.Sprintf("failed to create persistence directory: %v", err))
	}
	persistPath := filepath.Join(config.PersistencePath, "queue.log")
	file, err := os.OpenFile(persistPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		panic(fmt.Sprintf("failed to open persistence file: %v", err))
	}

	q := &Queue{
		config:      config,
		tasks:       make(taskHeap, 0),
		dlq:         make([]Task, 0),
		inFlight:    make(map[string]Task),
		persistFile: file,
	}
	q.cond = sync.NewCond(&q.mutex)
	heap.Init(&q.tasks)
	return q
}

// SubmitTask inserts a new task into the queue.
func (q *Queue) SubmitTask(task Task) error {
	q.mutex.Lock()
	defer q.mutex.Unlock()

	if q.shutdown {
		return errors.New("queue is shutdown")
	}
	// Set internal timestamp.
	task.timestamp = time.Now()
	heap.Push(&q.tasks, task)

	// Simulate replication. (For simplicity, actual replication is not implemented.)
	// Persist the task.
	entry := fmt.Sprintf("%s,%d,%s,%d\n", task.ID, task.Priority, task.Payload, task.timestamp.UnixNano())
	if _, err := q.persistFile.WriteString(entry); err != nil {
		return err
	}
	if err := q.persistFile.Sync(); err != nil {
		return err
	}

	// Signal waiting goroutines that a new task is available.
	q.cond.Broadcast()
	return nil
}

// RetrieveTask retrieves the highest priority task from the queue,
// waiting up to the provided timeout duration.
func (q *Queue) RetrieveTask(timeout time.Duration) (Task, error) {
	deadline := time.Now().Add(timeout)
	q.mutex.Lock()
	defer q.mutex.Unlock()

	for len(q.tasks) == 0 {
		remaining := time.Until(deadline)
		if remaining <= 0 {
			return Task{}, ErrTimeout
		}
		// Release lock and sleep for a small interval to implement timed waiting.
		q.mutex.Unlock()
		time.Sleep(10 * time.Millisecond)
		q.mutex.Lock()
		if q.shutdown {
			return Task{}, errors.New("queue is shutdown")
		}
	}

	// Retrieve the task with the highest priority.
	item := heap.Pop(&q.tasks).(Task)
	// Mark task as in-flight.
	q.inFlight[item.ID] = item
	return item, nil
}

// ReportTaskFailure moves the given task from in-flight to the Dead Letter Queue (DLQ).
func (q *Queue) ReportTaskFailure(taskID string) error {
	q.mutex.Lock()
	defer q.mutex.Unlock()

	task, ok := q.inFlight[taskID]
	if !ok {
		return fmt.Errorf("task %s not found in in-flight tasks", taskID)
	}
	q.dlq = append(q.dlq, task)
	delete(q.inFlight, taskID)
	return nil
}

// GetDLQ returns a copy of the Dead Letter Queue.
func (q *Queue) GetDLQ() []Task {
	q.mutex.Lock()
	defer q.mutex.Unlock()
	dlqCopy := make([]Task, len(q.dlq))
	copy(dlqCopy, q.dlq)
	return dlqCopy
}

// Shutdown stops the queue and closes resources.
func (q *Queue) Shutdown() {
	q.mutex.Lock()
	q.shutdown = true
	q.cond.Broadcast()
	q.mutex.Unlock()
	if q.persistFile != nil {
		q.persistFile.Close()
	}
}

// taskHeap implements heap.Interface for Task based on Priority and timestamp.
type taskHeap []Task

func (h taskHeap) Len() int { return len(h) }

func (h taskHeap) Less(i, j int) bool {
	if h[i].Priority == h[j].Priority {
		return h[i].timestamp.Before(h[j].timestamp)
	}
	return h[i].Priority < h[j].Priority
}

func (h taskHeap) Swap(i, j int) { h[i], h[j] = h[j], h[i] }

func (h *taskHeap) Push(x interface{}) {
	*h = append(*h, x.(Task))
}

func (h *taskHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}