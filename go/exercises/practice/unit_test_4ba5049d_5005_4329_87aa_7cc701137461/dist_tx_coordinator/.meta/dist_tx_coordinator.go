package dtc

import (
	"math/rand"
	"sync"
	"time"
)

const (
	maxRetries    = 3
	retryInterval = 500 * time.Millisecond
	txTimeout     = 5 * time.Second
)

type TransactionState int

const (
	Idle TransactionState = iota
	Preparing
	Committing
	Rolling
)

type Microservice struct {
	id           int
	state        int
	tempState    int
	minValue     int
	maxValue     int
	mu           sync.RWMutex
	txState      TransactionState
	coordinator  *Coordinator
}

type Coordinator struct {
	services              []*Microservice
	messageLossProbability float64
	mu                    sync.RWMutex
	txLock               sync.Mutex
}

func NewCoordinator(n int, minValue, maxValue int, lossProbability float64) *Coordinator {
	coord := &Coordinator{
		services:              make([]*Microservice, n),
		messageLossProbability: lossProbability,
	}

	for i := 0; i < n; i++ {
		coord.services[i] = &Microservice{
			id:       i,
			minValue: minValue,
			maxValue: maxValue,
			coordinator: coord,
		}
	}

	return coord
}

func (c *Coordinator) simulateMessageLoss() bool {
	return rand.Float64() < c.messageLossProbability
}

func (c *Coordinator) InitiateTransaction(deltas []int) bool {
	c.txLock.Lock()
	defer c.txLock.Unlock()

	if len(deltas) != len(c.services) {
		return false
	}

	// Prepare phase
	prepareResults := make([]bool, len(c.services))
	var wg sync.WaitGroup

	for i, service := range c.services {
		wg.Add(1)
		go func(idx int, svc *Microservice, delta int) {
			defer wg.Done()
			success := false
			for retry := 0; retry < maxRetries; retry++ {
				if !c.simulateMessageLoss() {
					success = svc.prepare(delta)
					break
				}
				time.Sleep(retryInterval)
			}
			prepareResults[idx] = success
		}(i, service, deltas[i])
	}

	done := make(chan bool)
	go func() {
		wg.Wait()
		done <- true
	}()

	select {
	case <-done:
	case <-time.After(txTimeout):
		c.rollbackAll()
		return false
	}

	// Check if all services prepared successfully
	for _, success := range prepareResults {
		if !success {
			c.rollbackAll()
			return false
		}
	}

	// Commit phase
	return c.commitAll()
}

func (c *Coordinator) rollbackAll() {
	var wg sync.WaitGroup
	for _, service := range c.services {
		wg.Add(1)
		go func(svc *Microservice) {
			defer wg.Done()
			for retry := 0; retry < maxRetries; retry++ {
				if !c.simulateMessageLoss() {
					svc.rollback()
					break
				}
				time.Sleep(retryInterval)
			}
		}(service)
	}
	wg.Wait()
}

func (c *Coordinator) commitAll() bool {
	var wg sync.WaitGroup
	commitResults := make([]bool, len(c.services))

	for i, service := range c.services {
		wg.Add(1)
		go func(idx int, svc *Microservice) {
			defer wg.Done()
			success := false
			for retry := 0; retry < maxRetries; retry++ {
				if !c.simulateMessageLoss() {
					success = svc.commit()
					break
				}
				time.Sleep(retryInterval)
			}
			commitResults[idx] = success
		}(i, service)
	}

	wg.Wait()

	for _, success := range commitResults {
		if !success {
			c.rollbackAll()
			return false
		}
	}

	return true
}

func (m *Microservice) prepare(delta int) bool {
	m.mu.Lock()
	defer m.mu.Unlock()

	if m.txState != Idle {
		return false
	}

	newState := m.state + delta
	if newState < m.minValue || newState > m.maxValue {
		return false
	}

	m.tempState = newState
	m.txState = Preparing
	return true
}

func (m *Microservice) commit() bool {
	m.mu.Lock()
	defer m.mu.Unlock()

	if m.txState != Preparing {
		return false
	}

	m.state = m.tempState
	m.txState = Idle
	return true
}

func (m *Microservice) rollback() {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.tempState = m.state
	m.txState = Idle
}

func (c *Coordinator) GetAllStates() []int {
	states := make([]int, len(c.services))
	for i, service := range c.services {
		service.mu.RLock()
		states[i] = service.state
		service.mu.RUnlock()
	}
	return states
}

func (c *Coordinator) IsConsistent() bool {
	for _, service := range c.services {
		service.mu.RLock()
		state := service.state
		txState := service.txState
		service.mu.RUnlock()

		if txState != Idle || state < service.minValue || state > service.maxValue {
			return false
		}
	}
	return true
}