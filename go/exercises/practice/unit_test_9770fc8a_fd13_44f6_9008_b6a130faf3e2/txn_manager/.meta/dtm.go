package txn_manager

import (
	"errors"
	"sync"
	"time"
)

// Participant represents a participant in the distributed transaction.
type Participant struct {
	ID       string
	Prepare  func() error
	Commit   func() error
	Rollback func() error
}

// TransactionState represents the state of a transaction.
type TransactionState int

const (
	Unknown TransactionState = iota
	Committed
	RolledBack
	InProgress
)

// LogEntry represents a persistent log entry for transaction state changes.
type LogEntry struct {
	TXID  string
	State TransactionState
}

// DTM represents the distributed transaction manager.
type DTM struct {
	transactions   map[string]TransactionState
	logs           []LogEntry
	mutex          sync.Mutex
	prepareTimeout time.Duration
}

// NewDTM creates a new instance of DTM.
func NewDTM() *DTM {
	return &DTM{
		transactions:   make(map[string]TransactionState),
		logs:           []LogEntry{},
		prepareTimeout: 1 * time.Second,
	}
}

// NewDTMFromLog creates a new DTM instance from a persisted log.
func NewDTMFromLog(logs []LogEntry) *DTM {
	dtm := &DTM{
		transactions:   make(map[string]TransactionState),
		logs:           logs,
		prepareTimeout: 1 * time.Second,
	}
	for _, entry := range logs {
		dtm.transactions[entry.TXID] = entry.State
	}
	return dtm
}

// ExportLog returns the current persistent log.
func (d *DTM) ExportLog() []LogEntry {
	d.mutex.Lock()
	defer d.mutex.Unlock()
	copiedLog := make([]LogEntry, len(d.logs))
	copy(copiedLog, d.logs)
	return copiedLog
}

// SetPrepareTimeout sets the timeout for the preparation phase for each participant.
func (d *DTM) SetPrepareTimeout(timeout time.Duration) {
	d.mutex.Lock()
	defer d.mutex.Unlock()
	d.prepareTimeout = timeout
}

// ProcessTransaction coordinates the 2PC transaction process.
func (d *DTM) ProcessTransaction(txid string, participants []Participant) error {
	d.mutex.Lock()
	// Idempotency: if transaction already committed or rolled back, return existing result.
	if state, exists := d.transactions[txid]; exists && (state == Committed || state == RolledBack) {
		d.mutex.Unlock()
		return nil
	}
	// Mark transaction as in progress.
	d.transactions[txid] = InProgress
	d.logs = append(d.logs, LogEntry{TXID: txid, State: InProgress})
	d.mutex.Unlock()

	// Phase 1: Prepare Phase.
	prepareResults := make(chan error, len(participants))
	var wg sync.WaitGroup

	for _, p := range participants {
		wg.Add(1)
		go func(part Participant) {
			defer wg.Done()
			ch := make(chan error, 1)
			go func() {
				err := part.Prepare()
				ch <- err
			}()
			select {
			case err := <-ch:
				prepareResults <- err
			case <-time.After(d.prepareTimeout):
				prepareResults <- errors.New("prepare timeout")
			}
		}(p)
	}
	wg.Wait()
	close(prepareResults)

	prepareFailed := false
	for err := range prepareResults {
		if err != nil {
			prepareFailed = true
			break
		}
	}

	if prepareFailed {
		d.rollbackTransaction(txid, participants)
		return errors.New("prepare phase failed, transaction rolled back")
	}

	// Phase 2: Commit Phase.
	for _, p := range participants {
		if err := p.Commit(); err != nil {
			d.rollbackTransaction(txid, participants)
			return errors.New("commit phase failed, transaction rolled back")
		}
	}

	d.mutex.Lock()
	d.transactions[txid] = Committed
	d.logs = append(d.logs, LogEntry{TXID: txid, State: Committed})
	d.mutex.Unlock()
	return nil
}

func (d *DTM) rollbackTransaction(txid string, participants []Participant) {
	for _, p := range participants {
		_ = p.Rollback()
	}
	d.mutex.Lock()
	d.transactions[txid] = RolledBack
	d.logs = append(d.logs, LogEntry{TXID: txid, State: RolledBack})
	d.mutex.Unlock()
}

// GetTransactionState returns the current state of the transaction.
func (d *DTM) GetTransactionState(txid string) TransactionState {
	d.mutex.Lock()
	defer d.mutex.Unlock()
	if state, exists := d.transactions[txid]; exists {
		return state
	}
	return Unknown
}

// SimulateCrash clears the in-memory transaction states to simulate a crash.
func (d *DTM) SimulateCrash() {
	d.mutex.Lock()
	defer d.mutex.Unlock()
	d.transactions = make(map[string]TransactionState)
}

// Recover replays the log to finalize any in-flight transactions.
func (d *DTM) Recover() error {
	d.mutex.Lock()
	defer d.mutex.Unlock()
	for _, entry := range d.logs {
		if entry.State == InProgress {
			// For simplicity, roll back any in-progress transaction.
			d.transactions[entry.TXID] = RolledBack
			d.logs = append(d.logs, LogEntry{TXID: entry.TXID, State: RolledBack})
		} else {
			d.transactions[entry.TXID] = entry.State
		}
	}
	return nil
}