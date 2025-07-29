package async_rate_limit

import (
	"container/heap"
	"errors"
	"sync"
	"time"
)

var ErrShuttingDown = errors.New("rate limiter is shutting down")

type Task struct {
	fn       func()
	priority int
	order    int
}

type PriorityTaskQueue []*Task

func (pq PriorityTaskQueue) Len() int { return len(pq) }
func (pq PriorityTaskQueue) Less(i, j int) bool {
	if pq[i].priority == pq[j].priority {
		return pq[i].order < pq[j].order
	}
	return pq[i].priority < pq[j].priority
}
func (pq PriorityTaskQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}
func (pq *PriorityTaskQueue) Push(x interface{}) {
	task := x.(*Task)
	*pq = append(*pq, task)
}
func (pq *PriorityTaskQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	task := old[n-1]
	*pq = old[0 : n-1]
	return task
}

type RateLimiter struct {
	mu           sync.Mutex
	tasks        PriorityTaskQueue
	ticker       *time.Ticker
	rate         int
	shuttingDown bool
	orderCounter int
	taskWG       sync.WaitGroup
	workerWG     sync.WaitGroup
}

func NewRateLimiter(rate int) *RateLimiter {
	rl := &RateLimiter{
		tasks:  make(PriorityTaskQueue, 0),
		rate:   rate,
		ticker: time.NewTicker(time.Second / time.Duration(rate)),
	}
	heap.Init(&rl.tasks)
	rl.workerWG.Add(1)
	go rl.worker()
	return rl
}

func (rl *RateLimiter) Submit(task func(), priority int) error {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	if rl.shuttingDown {
		return ErrShuttingDown
	}
	rl.orderCounter++
	newTask := &Task{
		fn:       task,
		priority: priority,
		order:    rl.orderCounter,
	}
	heap.Push(&rl.tasks, newTask)
	return nil
}

func (rl *RateLimiter) worker() {
	defer rl.workerWG.Done()
	for {
		<-rl.ticker.C
		rl.mu.Lock()
		if len(rl.tasks) > 0 {
			t := heap.Pop(&rl.tasks).(*Task)
			rl.taskWG.Add(1)
			rl.mu.Unlock()
			go func(taskFn func()) {
				taskFn()
				rl.taskWG.Done()
			}(t.fn)
		} else {
			if rl.shuttingDown {
				rl.mu.Unlock()
				return
			}
			rl.mu.Unlock()
		}
	}
}

func (rl *RateLimiter) Shutdown(timeout time.Duration) error {
	rl.mu.Lock()
	rl.shuttingDown = true
	rl.mu.Unlock()

	doneChan := make(chan struct{})
	go func() {
		rl.workerWG.Wait()
		rl.taskWG.Wait()
		close(doneChan)
	}()

	select {
	case <-doneChan:
		rl.ticker.Stop()
		return nil
	case <-time.After(timeout):
		rl.ticker.Stop()
		return errors.New("shutdown timeout reached before completing all tasks")
	}
}