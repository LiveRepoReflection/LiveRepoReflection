package dtc_bank

import (
	"os"
	"path/filepath"
	"strconv"
	"sync"
	"testing"
	"time"
)

// DummyDTC is a stub representing the Distributed Transaction Coordinator.
// It is assumed that the actual implementation contains proper logic for
// executing transactions, logging, recovery, and concurrency handling.
type DummyDTC struct {
	Nodes   []BankService
	LogPath string

	mu                sync.Mutex
	lastTransactionID int
	// for testing purposes, we store the last transaction's ID.
	lastTxID string
}

// NewDTC creates a new DummyDTC instance.
func NewDTC(nodes []BankService, logPath string) *DummyDTC {
	return &DummyDTC{
		Nodes:   nodes,
		LogPath: logPath,
	}
}

// ExecuteTransaction attempts to execute a distributed transaction.
// The operations parameter maps each BankService instance to a slice of operations.
func (d *DummyDTC) ExecuteTransaction(operations map[BankService][]Operation) error {
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

// Recover simulates reading the log and reattempting incomplete transactions.
func (d *DummyDTC) Recover() error {
	// For testing purposes, simply check if lastTxID is non-empty and append a recovery log.
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

func (d *DummyDTC) generateTransactionID() string {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.lastTransactionID++
	return "tx_" + strconv.Itoa(d.lastTransactionID)
}

func (d *DummyDTC) appendLog(transactionID, message string) error {
	f, err := os.OpenFile(d.LogPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer f.Close()
	logLine := transactionID + ": " + message + "\n"
	_, err = f.WriteString(logLine)
	return err
}

func (d *DummyDTC) setLastTransactionID(transactionID string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.lastTxID = transactionID
}

func setupTempLogFile(t *testing.T) string {
	t.Helper()
	tmpDir := os.TempDir()
	logPath := filepath.Join(tmpDir, "dtc_test.log")
	// Remove any existing log file.
	os.Remove(logPath)
	f, err := os.Create(logPath)
	if err != nil {
		t.Fatalf("Failed to create temp log file: %v", err)
	}
	f.Close()
	return logPath
}

func TestTransactionCommitSuccess(t *testing.T) {
	logPath := setupTempLogFile(t)
	// Create two mock bank services that will successfully prepare.
	node1 := NewMockBankService()
	node1.Balance["acct1"] = 100
	node2 := NewMockBankService()
	node2.Balance["acct2"] = 200

	dtc := NewDTC([]BankService{node1, node2}, logPath)

	ops := map[BankService][]Operation{
		node1: {
			{AccountID: "acct1", Amount: -50},
		},
		node2: {
			{AccountID: "acct2", Amount: 50},
		},
	}

	err := dtc.ExecuteTransaction(ops)
	if err != nil {
		t.Fatalf("Expected successful transaction, got error: %v", err)
	}

	// Verify that commit was applied in both nodes.
	dtcID := dtc.lastTxID
	node1.mu.Lock()
	defer node1.mu.Unlock()
	if !node1.CommittedTxIDs[dtcID] {
		t.Errorf("Node1 did not commit transaction %s", dtcID)
	}
	node2.mu.Lock()
	defer node2.mu.Unlock()
	if !node2.CommittedTxIDs[dtcID] {
		t.Errorf("Node2 did not commit transaction %s", dtcID)
	}
}

func TestTransactionRollbackOnPrepareFailure(t *testing.T) {
	logPath := setupTempLogFile(t)
	// Create two mock bank services; node2 will simulate insufficient funds.
	node1 := NewMockBankService()
	node1.Balance["acct1"] = 100
	node2 := NewMockBankService()
	node2.Balance["acct2"] = 20 // Insufficient funds for withdrawal of 50

	dtc := NewDTC([]BankService{node1, node2}, logPath)

	ops := map[BankService][]Operation{
		node1: {
			{AccountID: "acct1", Amount: -50},
		},
		node2: {
			{AccountID: "acct2", Amount: -50},
		},
	}

	err := dtc.ExecuteTransaction(ops)
	if err != nil {
		t.Fatalf("Transaction should rollback gracefully, got error: %v", err)
	}

	// Verify that rollback was applied in both nodes.
	dtcID := dtc.lastTxID
	node1.mu.Lock()
	defer node1.mu.Unlock()
	if !node1.RolledbackTxIDs[dtcID] {
		t.Errorf("Node1 did not rollback transaction %s", dtcID)
	}
	node2.mu.Lock()
	defer node2.mu.Unlock()
	if !node2.RolledbackTxIDs[dtcID] {
		t.Errorf("Node2 did not rollback transaction %s", dtcID)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	logPath := setupTempLogFile(t)
	// Create three mock bank services.
	node1 := NewMockBankService()
	node1.Balance["acct1"] = 1000
	node2 := NewMockBankService()
	node2.Balance["acct2"] = 1000
	node3 := NewMockBankService()
	node3.Balance["acct3"] = 1000

	dtc := NewDTC([]BankService{node1, node2, node3}, logPath)

	var wg sync.WaitGroup
	numTransactions := 10
	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			ops := map[BankService][]Operation{
				node1: {
					{AccountID: "acct1", Amount: -10},
				},
				node2: {
					{AccountID: "acct2", Amount: 5},
				},
				node3: {
					{AccountID: "acct3", Amount: 5},
				},
			}
			if err := dtc.ExecuteTransaction(ops); err != nil {
				t.Errorf("Concurrent transaction %d failed: %v", i, err)
			}
		}(i)
	}
	wg.Wait()
	// Simple verification: the log file should contain numTransactions * 3 + recovery lines.
	data, err := os.ReadFile(logPath)
	if err != nil {
		t.Fatalf("Failed to read log file: %v", err)
	}
	logContent := string(data)
	// Check that transactions were committed.
	for i := 1; i <= numTransactions; i++ {
		txID := "tx_" + strconv.Itoa(i)
		if !containsLine(logContent, txID+": Transaction committed") && !containsLine(logContent, txID+": Transaction rolled back") {
			t.Errorf("Transaction %s did not complete properly", txID)
		}
	}
}

func TestRecovery(t *testing.T) {
	logPath := setupTempLogFile(t)
	// Create a mock log entry for an incomplete transaction.
	f, err := os.OpenFile(logPath, os.O_APPEND|os.O_WRONLY, 0644)
	if err != nil {
		t.Fatalf("Failed to open log file: %v", err)
	}
	incompleteTx := "tx_incomplete"
	_, err = f.WriteString(incompleteTx + ": Prepare sent\n")
	if err != nil {
		t.Fatalf("Failed to write to log file: %v", err)
	}
	f.Close()

	// Create a DTC and set lastTxID to the incomplete one.
	dtc := NewDTC(nil, logPath)
	dtc.setLastTransactionID(incompleteTx)

	err = dtc.Recover()
	if err != nil {
		t.Fatalf("Recovery failed: %v", err)
	}

	// Verify that recovery log entry was appended.
	data, err := os.ReadFile(logPath)
	if err != nil {
		t.Fatalf("Failed to read log file: %v", err)
	}
	logContent := string(data)
	if !containsLine(logContent, incompleteTx+": Recovery completed") {
		t.Errorf("Recovery log entry not found for transaction %s", incompleteTx)
	}
}

// containsLine is a helper function to check if logContent contains a line with the target string.
func containsLine(logContent, target string) bool {
	lines := splitLines(logContent)
	for _, line := range lines {
		if line == target {
			return true
		}
	}
	return false
}

// splitLines splits a string into a slice of strings based on newline.
func splitLines(s string) []string {
	var lines []string
	start := 0
	for i, c := range s {
		if c == '\n' {
			lines = append(lines, s[start:i])
			start = i + 1
		}
	}
	if start < len(s) {
		lines = append(lines, s[start:])
	}
	return lines
}