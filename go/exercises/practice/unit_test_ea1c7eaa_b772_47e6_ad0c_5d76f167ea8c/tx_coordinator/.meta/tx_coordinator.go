package tx_coordinator

import (
	"errors"
	"fmt"
	"log"
	"sync"
	"time"
)

var (
	processedTransactions sync.Map // transactionID -> bool
)

const opTimeout = 5 * time.Second

// ExecuteTransaction implements a two-phase commit distributed transaction coordinator.
func ExecuteTransaction(transactionID string, participants []string, prepareFunc func(participant, transactionID string) error, commitFunc func(participant, transactionID string) error, rollbackFunc func(participant, transactionID string) error) error {
	// Check for duplicate transaction processing.
	if _, loaded := processedTransactions.LoadOrStore(transactionID, true); loaded {
		return errors.New("transaction already processed")
	}

	log.Printf("Transaction %s started with participants: %v", transactionID, participants)
	// If there are no participants, simply return success.
	if len(participants) == 0 {
		log.Printf("Transaction %s: no participants, nothing to do", transactionID)
		return nil
	}

	var (
		prepareWG  sync.WaitGroup
		mu         sync.Mutex
	)
	preparedParticipants := make(map[string]bool) // Track participants that have successfully prepared.
	prepareErrors := make(chan error, len(participants))

	// Prepare Phase: Run all prepareFunc calls concurrently.
	for _, participant := range participants {
		prepareWG.Add(1)
		p := participant
		go func() {
			defer prepareWG.Done()
			err := callWithTimeout(func() error {
				return prepareFunc(p, transactionID)
			}, opTimeout)
			if err != nil {
				log.Printf("Transaction %s: prepare failed for participant %s: %v", transactionID, p, err)
				prepareErrors <- fmt.Errorf("prepare failed for %s: %w", p, err)
			} else {
				log.Printf("Transaction %s: prepared participant %s", transactionID, p)
				mu.Lock()
				preparedParticipants[p] = true
				mu.Unlock()
			}
		}()
	}

	prepareWG.Wait()
	close(prepareErrors)

	var firstPrepareError error
	for err := range prepareErrors {
		if firstPrepareError == nil {
			firstPrepareError = err
		}
	}

	// If any prepare operation failed, initiate Rollback on successfully prepared participants.
	if firstPrepareError != nil {
		log.Printf("Transaction %s: prepare phase failed, initiating rollback", transactionID)
		var rollbackWG sync.WaitGroup
		rollbackErrors := make(chan error, len(preparedParticipants))
		for participant := range preparedParticipants {
			rollbackWG.Add(1)
			p := participant
			go func() {
				defer rollbackWG.Done()
				err := callWithTimeout(func() error {
					return rollbackFunc(p, transactionID)
				}, opTimeout)
				if err != nil {
					log.Printf("Transaction %s: rollback failed for participant %s: %v", transactionID, p, err)
					rollbackErrors <- fmt.Errorf("rollback failed for %s: %w", p, err)
				} else {
					log.Printf("Transaction %s: rolled back participant %s", transactionID, p)
				}
			}()
		}
		rollbackWG.Wait()
		close(rollbackErrors)

		var firstRollbackError error
		for err := range rollbackErrors {
			if firstRollbackError == nil {
				firstRollbackError = err
			}
		}
		if firstRollbackError != nil {
			return fmt.Errorf("transaction %s failed during prepare and rollback: prepare error: %v, rollback error: %v", transactionID, firstPrepareError, firstRollbackError)
		}
		return fmt.Errorf("transaction %s failed during prepare: %v", transactionID, firstPrepareError)
	}

	// Commit Phase: All participants prepared successfully, proceed with commit.
	log.Printf("Transaction %s: prepare phase successful, initiating commit", transactionID)
	var commitWG sync.WaitGroup
	commitErrors := make(chan error, len(participants))
	for _, participant := range participants {
		commitWG.Add(1)
		p := participant
		go func() {
			defer commitWG.Done()
			err := callWithTimeout(func() error {
				return commitFunc(p, transactionID)
			}, opTimeout)
			if err != nil {
				log.Printf("Transaction %s: commit failed for participant %s: %v", transactionID, p, err)
				commitErrors <- fmt.Errorf("commit failed for %s: %w", p, err)
			} else {
				log.Printf("Transaction %s: committed participant %s", transactionID, p)
			}
		}()
	}
	commitWG.Wait()
	close(commitErrors)
	var firstCommitError error
	for err := range commitErrors {
		if firstCommitError == nil {
			firstCommitError = err
		}
	}
	if firstCommitError != nil {
		return fmt.Errorf("transaction %s failed during commit: %v", transactionID, firstCommitError)
	}
	log.Printf("Transaction %s: committed successfully for all participants", transactionID)
	return nil
}

// callWithTimeout runs an operation with a specified timeout.
func callWithTimeout(operation func() error, timeout time.Duration) error {
	resultChan := make(chan error, 1)
	go func() {
		resultChan <- operation()
	}()
	select {
	case res := <-resultChan:
		return res
	case <-time.After(timeout):
		return errors.New("operation timed out")
	}
}