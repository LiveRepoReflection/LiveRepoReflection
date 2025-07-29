package txn_coord

import (
	"errors"
	"strconv"
	"sync"
	"testing"
	"time"
)

// mockBankService simulates a bank service for testing purposes.
type mockBankService struct {
	name               string
	prepareDelay       time.Duration
	commitDelay        time.Duration
	rollbackDelay      time.Duration
	failPrepare        bool
	commitFailAttempts int
	commitCallCount    int

	prepared   bool
	committed  bool
	rolledback bool

	mu sync.Mutex
}

func (m *mockBankService) Prepare(txnID string) (bool, error) {
	if m.prepareDelay > 0 {
		time.Sleep(m.prepareDelay)
	}
	if m.failPrepare {
		return false, errors.New("prepare failure: " + m.name)
	}
	m.mu.Lock()
	m.prepared = true
	m.mu.Unlock()
	return true, nil
}

func (m *mockBankService) Commit(txnID string) error {
	if m.commitDelay > 0 {
		time.Sleep(m.commitDelay)
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	m.commitCallCount++
	if m.commitCallCount <= m.commitFailAttempts {
		return errors.New("commit failure: " + m.name)
	}
	m.committed = true
	return nil
}

func (m *mockBankService) Rollback(txnID string) error {
	if m.rollbackDelay > 0 {
		time.Sleep(m.rollbackDelay)
	}
	m.mu.Lock()
	m.rolledback = true
	m.mu.Unlock()
	return nil
}

// TestSuccessfulTransaction tests that a transaction with all services behaving normally commits.
func TestSuccessfulTransaction(t *testing.T) {
	svc1 := &mockBankService{name: "svc1"}
	svc2 := &mockBankService{name: "svc2"}
	services := []BankService{svc1, svc2}

	config := CoordinatorConfig{
		PrepareTimeout:  100 * time.Millisecond,
		CommitTimeout:   100 * time.Millisecond,
		RollbackTimeout: 100 * time.Millisecond,
		RetryCount:      3,
		BackoffInterval: 10 * time.Millisecond,
	}

	err := ExecuteTransaction(services, config)
	if err != nil {
		t.Fatalf("Expected successful transaction, got error: %v", err)
	}
	if !svc1.committed || !svc2.committed {
		t.Fatalf("Expected both services to have committed, got svc1.committed=%v, svc2.committed=%v", svc1.committed, svc2.committed)
	}
	if svc1.rolledback || svc2.rolledback {
		t.Fatalf("Did not expect rollback, but got svc1.rolledback=%v, svc2.rolledback=%v", svc1.rolledback, svc2.rolledback)
	}
}

// TestPrepareFailure verifies that if any service fails in the prepare phase the coordinator rolls back.
func TestPrepareFailure(t *testing.T) {
	svc1 := &mockBankService{name: "svc1"}
	svc2 := &mockBankService{name: "svc2", failPrepare: true}
	services := []BankService{svc1, svc2}

	config := CoordinatorConfig{
		PrepareTimeout:  100 * time.Millisecond,
		CommitTimeout:   100 * time.Millisecond,
		RollbackTimeout: 100 * time.Millisecond,
		RetryCount:      3,
		BackoffInterval: 10 * time.Millisecond,
	}

	err := ExecuteTransaction(services, config)
	if err == nil {
		t.Fatalf("Expected failure due to prepare error, got nil")
	}
	if !svc1.rolledback {
		t.Fatalf("Expected svc1 to be rolled back")
	}
	if !svc2.rolledback {
		t.Fatalf("Expected svc2 to be rolled back")
	}
}

// TestTimeoutDuringPrepare simulates a long delay in one service's prepare phase causing a timeout.
func TestTimeoutDuringPrepare(t *testing.T) {
	svc1 := &mockBankService{name: "svc1"}
	svc2 := &mockBankService{name: "svc2", prepareDelay: 200 * time.Millisecond}
	services := []BankService{svc1, svc2}

	config := CoordinatorConfig{
		PrepareTimeout:  100 * time.Millisecond,
		CommitTimeout:   100 * time.Millisecond,
		RollbackTimeout: 100 * time.Millisecond,
		RetryCount:      3,
		BackoffInterval: 10 * time.Millisecond,
	}

	err := ExecuteTransaction(services, config)
	if err == nil {
		t.Fatalf("Expected failure due to prepare timeout, got nil")
	}
	if !svc1.rolledback {
		t.Fatalf("Expected svc1 to be rolled back due to timeout")
	}
	if !svc2.rolledback {
		t.Fatalf("Expected svc2 to be rolled back due to timeout")
	}
}

// TestCommitRetry verifies that services with transient commit failures eventually succeed through retries.
func TestCommitRetry(t *testing.T) {
	svc1 := &mockBankService{name: "svc1", commitFailAttempts: 2}
	svc2 := &mockBankService{name: "svc2", commitFailAttempts: 1}
	services := []BankService{svc1, svc2}

	config := CoordinatorConfig{
		PrepareTimeout:  100 * time.Millisecond,
		CommitTimeout:   100 * time.Millisecond,
		RollbackTimeout: 100 * time.Millisecond,
		RetryCount:      3,
		BackoffInterval: 10 * time.Millisecond,
	}

	err := ExecuteTransaction(services, config)
	if err != nil {
		t.Fatalf("Expected successful transaction with commit retries, got error: %v", err)
	}
	if !svc1.committed || !svc2.committed {
		t.Fatalf("Expected both services to have eventually committed, got svc1.committed=%v, svc2.committed=%v", svc1.committed, svc2.committed)
	}
	if svc1.rolledback || svc2.rolledback {
		t.Fatalf("Did not expect any service to rollback, but got svc1.rolledback=%v, svc2.rolledback=%v", svc1.rolledback, svc2.rolledback)
	}
}

// TestConcurrentTransactions verifies that multiple transactions can be processed concurrently without interference.
func TestConcurrentTransactions(t *testing.T) {
	numTransactions := 10
	var wg sync.WaitGroup
	var mu sync.Mutex
	failedCount := 0

	config := CoordinatorConfig{
		PrepareTimeout:  200 * time.Millisecond,
		CommitTimeout:   200 * time.Millisecond,
		RollbackTimeout: 200 * time.Millisecond,
		RetryCount:      3,
		BackoffInterval: 10 * time.Millisecond,
	}

	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func(txnNum int) {
			defer wg.Done()
			svc1 := &mockBankService{name: "svc1_" + strconv.Itoa(txnNum)}
			svc2 := &mockBankService{name: "svc2_" + strconv.Itoa(txnNum)}
			services := []BankService{svc1, svc2}
			err := ExecuteTransaction(services, config)
			if err != nil {
				mu.Lock()
				failedCount++
				mu.Unlock()
				return
			}
			if !svc1.committed || !svc2.committed {
				mu.Lock()
				failedCount++
				mu.Unlock()
			}
		}(i)
	}
	wg.Wait()

	if failedCount != 0 {
		t.Fatalf("Expected all concurrent transactions to succeed, but %d transactions failed", failedCount)
	}
}