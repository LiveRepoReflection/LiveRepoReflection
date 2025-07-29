package stream_aggregate

import (
	"errors"
	"sync"
)

type Event struct {
	Timestamp int64
	EntityID  string
	Value     float64
}

type Worker struct {
	mu              sync.Mutex
	slidingWindow   int64
	events          []Event
	latestTimestamp int64
	failed          bool
}

func NewWorker(slidingWindow int64) *Worker {
	return &Worker{
		slidingWindow:   slidingWindow,
		events:          []Event{},
		latestTimestamp: 0,
		failed:          false,
	}
}

func (w *Worker) ProcessEvent(e Event) error {
	w.mu.Lock()
	defer w.mu.Unlock()
	if w.failed {
		return errors.New("worker is offline")
	}
	w.events = append(w.events, e)
	if e.Timestamp > w.latestTimestamp {
		w.latestTimestamp = e.Timestamp
	}
	return nil
}

func (w *Worker) QueryAverage() (float64, error) {
	w.mu.Lock()
	defer w.mu.Unlock()
	if w.failed {
		return 0, errors.New("worker is offline")
	}
	threshold := w.latestTimestamp - w.slidingWindow
	var sum float64
	var count int
	filtered := make([]Event, 0, len(w.events))
	for _, e := range w.events {
		if e.Timestamp >= threshold {
			filtered = append(filtered, e)
			sum += e.Value
			count++
		}
	}
	w.events = filtered
	if count == 0 {
		return 0, errors.New("no events in sliding window")
	}
	return sum / float64(count), nil
}

type Coordinator struct {
	slidingWindow int64
	mu            sync.Mutex
	workers       map[string]*Worker
}

func NewCoordinator(slidingWindow int64) *Coordinator {
	return &Coordinator{
		slidingWindow: slidingWindow,
		workers:       make(map[string]*Worker),
	}
}

func (c *Coordinator) getOrCreateWorker(entityID string) *Worker {
	c.mu.Lock()
	defer c.mu.Unlock()
	w, exists := c.workers[entityID]
	if !exists {
		w = NewWorker(c.slidingWindow)
		c.workers[entityID] = w
	}
	return w
}

func (c *Coordinator) ProcessEvent(e Event) error {
	w := c.getOrCreateWorker(e.EntityID)
	return w.ProcessEvent(e)
}

func (c *Coordinator) QueryAverage(entityID string) (float64, error) {
	c.mu.Lock()
	w, exists := c.workers[entityID]
	c.mu.Unlock()
	if !exists {
		return 0, errors.New("entity not found")
	}
	return w.QueryAverage()
}

func (c *Coordinator) SimulateWorkerFailure(entityID string) error {
	c.mu.Lock()
	w, exists := c.workers[entityID]
	c.mu.Unlock()
	if !exists {
		return errors.New("entity not found")
	}
	w.mu.Lock()
	w.failed = true
	w.mu.Unlock()
	return nil
}

func (c *Coordinator) RecoverWorker(entityID string) error {
	c.mu.Lock()
	w, exists := c.workers[entityID]
	c.mu.Unlock()
	if !exists {
		return errors.New("entity not found")
	}
	w.mu.Lock()
	w.failed = false
	w.mu.Unlock()
	return nil
}