package txncoordinator

import (
	"errors"
	"sync"
	"testing"
	"time"
)

// MockParticipant implements the Participant interface for testing
type MockParticipant struct {
	mu               sync.Mutex
	prepareSuccess   bool
	commitSuccess    bool
	rollbackSuccess  bool
	prepareCalled    bool
	commitCalled     bool
	rollbackCalled   bool
	prepareDelay    time.Duration
	lastTransaction  string
	lastPrepareData  map[string]interface{}
	prepareCallCount int
	commitCallCount  int
	rollbackCount    int
}

func NewMockParticipant(prepareSuccess, commitSuccess, rollbackSuccess bool) *MockParticipant {
	return &MockParticipant{
		prepareSuccess:   prepareSuccess,
		commitSuccess:    commitSuccess,
		rollbackSuccess: rollbackSuccess,
	}
}

func (m *MockParticipant) Prepare(transactionID string, data map[string]interface{}) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	m.prepareCalled = true
	m.lastTransaction = transactionID
	m.lastPrepareData = data
	m.prepareCallCount++
	
	if m.prepareDelay > 0 {
		time.Sleep(m.prepareDelay)
	}
	
	if !m.prepareSuccess {
		return errors.New("prepare failed")
	}
	return nil
}

func (m *MockParticipant) Commit(transactionID string) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	m.commitCalled = true
	m.commitCallCount++
	
	if !m.commitSuccess {
		return errors.New("commit failed")
	}
	return nil
}

func (m *MockParticipant) Rollback(transactionID string) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	m.rollbackCalled = true
	m.rollbackCount++
	
	if !m.rollbackSuccess {
		return errors.New("rollback failed")
	}
	return nil
}

func TestBeginTransaction(t *testing.T) {
	coordinator := NewCoordinator()
	txID1 := coordinator.BeginTransaction()
	txID2 := coordinator.BeginTransaction()
	
	if txID1 == "" {
		t.Error("Expected non-empty transaction ID")
	}
	if txID1 == txID2 {
		t.Error("Expected unique transaction IDs")
	}
}

func TestSuccessfulTransaction(t *testing.T) {
	coordinator := NewCoordinator()
	p1 := NewMockParticipant(true, true, true)
	p2 := NewMockParticipant(true, true, true)
	
	txID := coordinator.BeginTransaction()
	coordinator.EnlistParticipant(txID, p1)
	coordinator.EnlistParticipant(txID, p2)
	
	data := map[string]interface{}{"key": "value"}
	err := coordinator.CommitTransaction(txID, data)
	
	if err != nil {
		t.Errorf("Expected successful commit, got error: %v", err)
	}
	
	if !p1.prepareCalled || !p2.prepareCalled {
		t.Error("Expected all participants to be prepared")
	}
	if !p1.commitCalled || !p2.commitCalled {
		t.Error("Expected all participants to be committed")
	}
}

func TestFailedPrepare(t *testing.T) {
	coordinator := NewCoordinator()
	p1 := NewMockParticipant(true, true, true)
	p2 := NewMockParticipant(false, true, true) // p2 will fail prepare
	
	txID := coordinator.BeginTransaction()
	coordinator.EnlistParticipant(txID, p1)
	coordinator.EnlistParticipant(txID, p2)
	
	data := map[string]interface{}{"key": "value"}
	err := coordinator.CommitTransaction(txID, data)
	
	if err == nil {
		t.Error("Expected error on commit with failed prepare")
	}
	
	if !p1.rollbackCalled || !p2.rollbackCalled {
		t.Error("Expected all participants to be rolled back after prepare failure")
	}
}

func TestTimeout(t *testing.T) {
	coordinator := NewCoordinator()
	p1 := NewMockParticipant(true, true, true)
	p2 := NewMockParticipant(true, true, true)
	p2.prepareDelay = 6 * time.Second // Longer than default timeout
	
	txID := coordinator.BeginTransaction()
	coordinator.EnlistParticipant(txID, p1)
	coordinator.EnlistParticipant(txID, p2)
	
	data := map[string]interface{}{"key": "value"}
	err := coordinator.CommitTransaction(txID, data)
	
	if err == nil {
		t.Error("Expected timeout error")
	}
	
	if !p1.rollbackCalled {
		t.Error("Expected rollback after timeout")
	}
}

func TestConcurrentTransactions(t *testing.T) {
	coordinator := NewCoordinator()
	var wg sync.WaitGroup
	numTransactions := 10
	
	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func() {
			defer wg.Add(-1)
			p1 := NewMockParticipant(true, true, true)
			p2 := NewMockParticipant(true, true, true)
			
			txID := coordinator.BeginTransaction()
			coordinator.EnlistParticipant(txID, p1)
			coordinator.EnlistParticipant(txID, p2)
			
			data := map[string]interface{}{"key": "value"}
			err := coordinator.CommitTransaction(txID, data)
			
			if err != nil {
				t.Errorf("Concurrent transaction failed: %v", err)
			}
		}()
	}
	
	wg.Wait()
}

func TestIdempotency(t *testing.T) {
	coordinator := NewCoordinator()
	p := NewMockParticipant(true, true, true)
	
	txID := coordinator.BeginTransaction()
	coordinator.EnlistParticipant(txID, p)
	
	data := map[string]interface{}{"key": "value"}
	
	// Commit multiple times
	coordinator.CommitTransaction(txID, data)
	coordinator.CommitTransaction(txID, data)
	coordinator.CommitTransaction(txID, data)
	
	if p.commitCallCount != 1 {
		t.Errorf("Expected exactly one commit call, got %d", p.commitCallCount)
	}
}

func TestRetryMechanism(t *testing.T) {
	coordinator := NewCoordinator()
	p := NewMockParticipant(true, false, true) // commit will fail
	
	txID := coordinator.BeginTransaction()
	coordinator.EnlistParticipant(txID, p)
	
	data := map[string]interface{}{"key": "value"}
	err := coordinator.CommitTransaction(txID, data)
	
	if err == nil {
		t.Error("Expected error after retry exhaustion")
	}
	
	if p.commitCallCount < 2 {
		t.Error("Expected multiple commit attempts")
	}
}

func TestRollbackTransaction(t *testing.T) {
	coordinator := NewCoordinator()
	p1 := NewMockParticipant(true, true, true)
	p2 := NewMockParticipant(true, true, true)
	
	txID := coordinator.BeginTransaction()
	coordinator.EnlistParticipant(txID, p1)
	coordinator.EnlistParticipant(txID, p2)
	
	err := coordinator.RollbackTransaction(txID)
	
	if err != nil {
		t.Errorf("Expected successful rollback, got error: %v", err)
	}
	
	if !p1.rollbackCalled || !p2.rollbackCalled {
		t.Error("Expected all participants to be rolled back")
	}
}