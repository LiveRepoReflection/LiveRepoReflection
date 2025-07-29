package bft_coordinator

import (
	"sync"
	"time"
)

type Coordinator struct {
	n             int
	f             int
	transactions  map[int]*Transaction
	lock          sync.RWMutex
	timeout       time.Duration
}

type Transaction struct {
	id           int
	proposed     bool
	prepareVotes map[int]bool
	commitVotes  map[int]bool
	decision     *bool
	prepareLock  sync.Mutex
	commitLock   sync.Mutex
	decisionLock sync.Mutex
}

func NewCoordinator(n, f int) *Coordinator {
	return &Coordinator{
		n:            n,
		f:            f,
		transactions: make(map[int]*Transaction),
		timeout:      5 * time.Second,
	}
}

func (c *Coordinator) StartTransaction(txID int, commit bool) {
	c.lock.Lock()
	defer c.lock.Unlock()

	if _, exists := c.transactions[txID]; exists {
		return
	}

	tx := &Transaction{
		id:           txID,
		proposed:     commit,
		prepareVotes: make(map[int]bool),
		commitVotes:  make(map[int]bool),
	}
	c.transactions[txID] = tx

	go c.monitorTransactionTimeout(txID)
}

func (c *Coordinator) ReceiveVote(txID, participantID int, vote bool) {
	c.lock.RLock()
	tx, exists := c.transactions[txID]
	c.lock.RUnlock()

	if !exists {
		return
	}

	tx.prepareLock.Lock()
	tx.prepareVotes[participantID] = vote
	prepareCount := len(tx.prepareVotes)
	tx.prepareLock.Unlock()

	if prepareCount >= c.n-c.f {
		tx.commitLock.Lock()
		tx.commitVotes[participantID] = vote
		commitCount := len(tx.commitVotes)
		tx.commitLock.Unlock()

		if commitCount >= c.n-c.f {
			tx.decisionLock.Lock()
			if tx.decision == nil {
				decision := true
				for _, v := range tx.prepareVotes {
					if !v {
						decision = false
						break
					}
				}
				tx.decision = &decision
			}
			tx.decisionLock.Unlock()
		}
	}
}

func (c *Coordinator) monitorTransactionTimeout(txID int) {
	<-time.After(c.timeout)

	c.lock.Lock()
	defer c.lock.Unlock()

	if tx, exists := c.transactions[txID]; exists && tx.decision == nil {
		decision := false // timeout results in abort
		tx.decision = &decision
	}
}

func (c *Coordinator) GetDecision(txID int) (bool, bool) {
	c.lock.RLock()
	defer c.lock.RUnlock()

	if tx, exists := c.transactions[txID]; exists {
		tx.decisionLock.Lock()
		defer tx.decisionLock.Unlock()
		if tx.decision != nil {
			return *tx.decision, true
		}
	}
	return false, false
}