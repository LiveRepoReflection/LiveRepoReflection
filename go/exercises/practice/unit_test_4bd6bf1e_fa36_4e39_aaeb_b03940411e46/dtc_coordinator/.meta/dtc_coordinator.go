package dtc_coordinator

import (
	"errors"
	"log"
	"sync"
	"time"
)

type ServiceOperation struct {
	ServiceID    string
	PrepareFunc  func(transactionID string) error
	CommitFunc   func(transactionID string) error
	RollbackFunc func(transactionID string) error
}

// CoordinateTransaction implements a simplified two-phase commit protocol.
// It first runs the prepare phase concurrently with a specified timeout. If all
// services prepare successfully, the commit phase is executed concurrently.
// If any service fails to prepare or times out, rollback is executed concurrently
// for all services that prepared successfully.
func CoordinateTransaction(transactionID string, operations []ServiceOperation, timeout time.Duration) error {
	type prepareResult struct {
		index int
		err   error
	}
	prepareCh := make(chan prepareResult, len(operations))
	var preparedIndices []int

	// Launch prepare calls concurrently.
	for i, op := range operations {
		go func(i int, op ServiceOperation) {
			err := op.PrepareFunc(transactionID)
			prepareCh <- prepareResult{index: i, err: err}
		}(i, op)
	}

	timer := time.NewTimer(timeout)
	defer timer.Stop()

	prepareFail := false
	received := 0
loop:
	for received < len(operations) {
		select {
		case res := <-prepareCh:
			received++
			if res.err != nil {
				log.Println("Prepare error for service", operations[res.index].ServiceID, ":", res.err)
				prepareFail = true
			} else {
				preparedIndices = append(preparedIndices, res.index)
			}
		case <-timer.C:
			log.Println("Prepare phase timeout reached.")
			prepareFail = true
			break loop
		}
	}

	if prepareFail {
		// Rollback for all services that prepared successfully.
		var wgRollback sync.WaitGroup
		for _, idx := range preparedIndices {
			wgRollback.Add(1)
			go func(op ServiceOperation) {
				defer wgRollback.Done()
				if err := op.RollbackFunc(transactionID); err != nil {
					log.Println("Rollback error for service", op.ServiceID, ":", err)
				}
			}(operations[idx])
		}
		wgRollback.Wait()
		return errors.New("transaction rolled back due to prepare failure or timeout")
	}

	// Commit phase: all services prepared successfully.
	var wgCommit sync.WaitGroup
	commitFailure := false
	// Use a mutex to safely set commitFailure flag.
	var mu sync.Mutex

	for _, op := range operations {
		wgCommit.Add(1)
		go func(op ServiceOperation) {
			defer wgCommit.Done()
			if err := op.CommitFunc(transactionID); err != nil {
				mu.Lock()
				commitFailure = true
				mu.Unlock()
				log.Println("Commit error for service", op.ServiceID, ":", err)
			}
		}(op)
	}
	wgCommit.Wait()

	if commitFailure {
		return errors.New("transaction commit failed for one or more services")
	}
	return nil
}