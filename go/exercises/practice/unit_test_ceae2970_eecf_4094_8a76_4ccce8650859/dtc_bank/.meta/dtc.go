package dtc_bank

import (
	"os"
	"strconv"
	"sync"
)

type DTC struct {
	Nodes   []BankService
	LogPath string

	mu                sync.Mutex
	lastTransactionID int
	lastTxID          string
}

func NewDTC(nodes []BankService, logPath string) *DTC {
	return &DTC{
		Nodes:   nodes,
		LogPath: logPath,
	}
}

func (d *DTC) generateTransactionID() string {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.lastTransactionID++
	return "tx_" + strconv.Itoa(d.lastTransactionID)
}

func (d *DTC) appendLog(transactionID, message string) error {
	f, err := os.OpenFile(d.LogPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer f.Close()
	logLine := transactionID + ": " + message + "\n"
	_, err = f.WriteString(logLine)
	return err
}

func (d *DTC) setLastTransactionID(transactionID string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.lastTxID = transactionID
}

func (d *DTC) ExecuteTransaction(operations map[BankService][]Operation) error {
	transactionID := d.generateTransactionID()
	// Log prepare phase.
	if err := d.appendLog(transactionID, "Prepare sent"); err != nil {
		return err
	}

	preparedResults := make(map[BankService]string)
	var wg sync.WaitGroup
	errCh := make(chan error, len(operations))
	resCh := make(chan struct {
		node   BankService
		result string
	}, len(operations))
	// For each node, send a Prepare request concurrently.
	for node, ops := range operations {
		wg.Add(1)
		go func(nd BankService, ops []Operation) {
			defer wg.Done()
			result, err := nd.Prepare(transactionID, ops)
			if err != nil {
				errCh <- err
				resCh <- struct {
					node   BankService
					result string
				}{nd, ResponseAborted}
				return
			}
			resCh <- struct {
				node   BankService
				result string
			}{nd, result}
		}(node, ops)
	}
	wg.Wait()
	close(errCh)
	close(resCh)

	abort := false
	for res := range resCh {
		preparedResults[res.node] = res.result
		if res.result == ResponseAborted {
			abort = true
		}
	}

	// If any error occurred or a node aborted, rollback.
	if abort || len(errCh) > 0 {
		if err := d.appendLog(transactionID, "Rollback sent"); err != nil {
			return err
		}
		var rbWg sync.WaitGroup
		for node := range preparedResults {
			rbWg.Add(1)
			go func(nd BankService) {
				defer rbWg.Done()
				nd.Rollback(transactionID)
			}(node)
		}
		rbWg.Wait()
		if err := d.appendLog(transactionID, "Transaction rolled back"); err != nil {
			return err
		}
		d.setLastTransactionID(transactionID)
		return nil
	}

	// Otherwise, commit.
	if err := d.appendLog(transactionID, "Commit sent"); err != nil {
		return err
	}
	var commitWg sync.WaitGroup
	for node := range preparedResults {
		commitWg.Add(1)
		go func(nd BankService) {
			defer commitWg.Done()
			nd.Commit(transactionID)
		}(node)
	}
	commitWg.Wait()
	if err := d.appendLog(transactionID, "Transaction committed"); err != nil {
		return err
	}
	d.setLastTransactionID(transactionID)
	return nil
}

func (d *DTC) Recover() error {
	d.mu.Lock()
	defer d.mu.Unlock()
	if d.lastTxID != "" {
		f, err := os.OpenFile(d.LogPath, os.O_APPEND|os.O_WRONLY, 0644)
		if err != nil {
			return err
		}
		defer f.Close()
		_, err = f.WriteString(d.lastTxID + ": Recovery completed\n")
		if err != nil {
			return err
		}
	}
	return nil
}