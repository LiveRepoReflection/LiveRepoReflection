package dist_counter

import (
	"sync"
)

type Counter struct {
	mu    sync.Mutex
	value int64
}

func NewCounter() *Counter {
	return &Counter{}
}

func (c *Counter) Increment() int64 {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.value++
	return c.value
}

func (c *Counter) Get() int64 {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.value
}

func (c *Counter) Sync(otherValues []int64) {
	c.mu.Lock()
	defer c.mu.Unlock()

	for _, val := range otherValues {
		if val > c.value {
			c.value = val
		}
	}
}