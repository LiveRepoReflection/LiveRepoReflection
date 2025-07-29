package txnorchestrator

import (
	"sync"
	"sync/atomic"
)

type transactionState struct {
	preparedNodes sync.Map
	committed     atomic.Bool
	rollback      atomic.Bool
	prepareLock   sync.Mutex
	commitLock    sync.Mutex
}

func OrchestrateTransaction(
	n int,
	prepareFunctions []func(int, string) bool,
	commitFunctions []func(int),
	transactionID int,
	data string,
) bool {
	if n == 0 || len(prepareFunctions) != n || len(commitFunctions) != n {
		return false
	}

	txnState := &transactionState{}

	// Phase 1: Prepare
	success := preparePhase(txnState, n, prepareFunctions, transactionID, data)
	if !success {
		// If preparation failed, ensure rollback
		rollbackPhase(txnState, commitFunctions, transactionID)
		return false
	}

	// Phase 2: Commit
	return commitPhase(txnState, commitFunctions, transactionID)
}

func preparePhase(
	txnState *transactionState,
	n int,
	prepareFunctions []func(int, string) bool,
	transactionID int,
	data string,
) bool {
	var wg sync.WaitGroup
	prepareResults := make([]bool, n)

	// Execute prepare operations concurrently
	for i := 0; i < n; i++ {
		wg.Add(1)
		go func(nodeIndex int) {
			defer wg.Done()

			// Skip if we already know transaction will fail
			if txnState.rollback.Load() {
				return
			}

			success := prepareFunctions[nodeIndex](transactionID, data)
			if success {
				prepareResults[nodeIndex] = true
				txnState.preparedNodes.Store(nodeIndex, struct{}{})
			} else {
				txnState.rollback.Store(true)
			}
		}(i)
	}

	wg.Wait()

	// Check if all nodes prepared successfully
	if txnState.rollback.Load() {
		return false
	}

	for _, success := range prepareResults {
		if !success {
			return false
		}
	}

	return true
}

func commitPhase(
	txnState *transactionState,
	commitFunctions []func(int),
	transactionID int,
) bool {
	// Ensure we only commit once
	if !txnState.committed.CompareAndSwap(false, true) {
		return true // Already committed
	}

	var wg sync.WaitGroup

	// Execute commit operations concurrently
	txnState.preparedNodes.Range(func(key, value interface{}) bool {
		nodeIndex := key.(int)
		wg.Add(1)
		go func() {
			defer wg.Done()
			commitFunctions[nodeIndex](transactionID)
		}()
		return true
	})

	wg.Wait()
	return true
}

func rollbackPhase(
	txnState *transactionState,
	commitFunctions []func(int),
	transactionID int,
) {
	// No explicit rollback needed in this implementation
	// Resources are automatically released when prepare phase fails
	// This is where you would implement specific rollback logic if required
}