package dist_shortest_paths

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
	"sync"
	"time"
)

type Coordinator struct {
	workers []*Worker
	cache   *Cache
	mu      sync.RWMutex
}

type Cache struct {
	entries map[string]int
	mu      sync.RWMutex
}

func NewCoordinator(numWorkers int) *Coordinator {
	workers := make([]*Worker, numWorkers)
	for i := 0; i < numWorkers; i++ {
		workers[i] = NewWorker(i)
	}
	return &Coordinator{
		workers: workers,
		cache: &Cache{
			entries: make(map[string]int),
		},
	}
}

func (c *Coordinator) LoadGraph(edges []string) error {
	for _, edgeStr := range edges {
		parts := strings.Split(edgeStr, ":")
		if len(parts) != 2 {
			return errors.New("invalid edge format")
		}

		nodeID, err := strconv.Atoi(parts[0])
		if err != nil {
			return fmt.Errorf("invalid node ID: %v", err)
		}

		workerIdx := nodeID % len(c.workers)
		err = c.workers[workerIdx].AddNode(nodeID, parts[1])
		if err != nil {
			return fmt.Errorf("worker %d failed to add node: %v", workerIdx, err)
		}
	}
	return nil
}

func (c *Coordinator) ShortestPath(source, destination int) (int, error) {
	cacheKey := fmt.Sprintf("%d-%d", source, destination)
	
	c.cache.mu.RLock()
	if weight, exists := c.cache.entries[cacheKey]; exists {
		c.cache.mu.RUnlock()
		return weight, nil
	}
	c.cache.mu.RUnlock()

	workerIdx := source % len(c.workers)
	resultChan := make(chan int, 1)
	errorChan := make(chan error, 1)

	go func() {
		weight, err := c.workers[workerIdx].ComputeShortestPath(source, destination, c.workers)
		if err != nil {
			errorChan <- err
			return
		}
		resultChan <- weight
	}()

	select {
	case weight := <-resultChan:
		c.cache.mu.Lock()
		c.cache.entries[cacheKey] = weight
		c.cache.mu.Unlock()
		return weight, nil
	case err := <-errorChan:
		return -1, err
	case <-time.After(5 * time.Second):
		return -1, errors.New("timeout computing shortest path")
	}
}