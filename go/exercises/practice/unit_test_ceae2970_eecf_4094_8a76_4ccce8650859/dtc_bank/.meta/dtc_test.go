package dtc_bank

import (
	"os"
	"path/filepath"
	"strconv"
	"sync"
	"testing"
	"time"
)

func setupTempLogFile(t *testing.T) string {
	t.Helper()
	tmpDir := os.TempDir()
	logPath := filepath.Join(tmpDir, "dtc_test.log")
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

	dtcID := dtc.lastTxID
	node1.mu.Lock()
	if !node1.CommittedTxIDs[dtcID] {
		t.Errorf("Node1 did not commit transaction %s", dtcID)
	}
	node1.mu.Unlock()

	node2.mu.Lock()
	if !node2.CommittedTxIDs[dtcID] {
		t.Errorf("Node2 did not commit transaction %s", dtcID)
	}
	node2.mu.Unlock()
}

func TestTransactionRollbackOnPrepareFailure(t *testing.T) {
	logPath := setupTempLogFile(t)
	node1 := NewMockBankService()
	node1.Balance["acct1"] = 100
	node2 := NewMockBankService()
	node2.Balance["acct2"] = 20

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

	dtcID := dtc.lastTxID
	node1.mu.Lock()
	if !node1.RolledbackTxIDs[dtcID] {
		t.Errorf("Node1 did not rollback transaction %s", dtcID)
	}
	node1.mu.Unlock()

	node2.mu.Lock()
	if !node2.RolledbackTxIDs[dtcID] {
		t.Errorf("Node2 did not rollback transaction %s", dtcID)
	}
	node2.mu.Unlock()
}

func TestConcurrentTransactions(t *testing.T) {
	logPath := setupTempLogFile(t)
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
		time.Sleep(5 * time.Millisecond)
	}
	wg.Wait()

	data, err := os.ReadFile(logPath)
	if err != nil {
		t.Fatalf("Failed to read log file: %v", err)
	}
	logContent := string(data)
	for i := 1; i <= numTransactions; i++ {
		txID := "tx_" + strconv.Itoa(i)
		if !containsLine(logContent, txID+": Transaction committed") && !containsLine(logContent, txID+": Transaction rolled back") {
			t.Errorf("Transaction %s did not complete properly", txID)
		}
	}
}

func TestRecovery(t *testing.T) {
	logPath := setupTempLogFile(t)
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

	dtc := NewDTC(nil, logPath)
	dtc.setLastTransactionID(incompleteTx)

	err = dtc.Recover()
	if err != nil {
		t.Fatalf("Recovery failed: %v", err)
	}

	data, err := os.ReadFile(logPath)
	if err != nil {
		t.Fatalf("Failed to read log file: %v", err)
	}
	logContent := string(data)
	if !containsLine(logContent, incompleteTx+": Recovery completed") {
		t.Errorf("Recovery log entry not found for transaction %s", incompleteTx)
	}
}

func containsLine(logContent, target string) bool {
	lines := splitLines(logContent)
	for _, line := range lines {
		if line == target {
			return true
		}
	}
	return false
}

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