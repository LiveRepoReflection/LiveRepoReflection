package txn_ordering

import (
	"reflect"
	"sort"
	"testing"
	"time"
)

// Helper function to send transactions over a channel.
func sliceToChannel(transactions []Transaction) <-chan Transaction {
	ch := make(chan Transaction, len(transactions))
	for _, tx := range transactions {
		ch <- tx
	}
	close(ch)
	return ch
}

// Helper function to extract IDs from transactions for easier comparison.
func extractIDs(txs []Transaction) []string {
	ids := make([]string, len(txs))
	for i, tx := range txs {
		ids[i] = tx.ID
	}
	return ids
}

// compareTransactions is used to sort expected transactions according to the specification:
// primarily by Timestamp (ascending), then by Priority (descending) and finally by Sender (lexicographical order).
func compareTransactions(a, b Transaction) bool {
	if a.Timestamp != b.Timestamp {
		return a.Timestamp < b.Timestamp
	}
	if a.Priority != b.Priority {
		return a.Priority > b.Priority
	}
	return a.Sender < b.Sender
}

func TestOrderTransactions_EmptyStream(t *testing.T) {
	nodeID := "node1"
	nodeList := []string{"node1", "node2", "node3"}
	emptyChan := sliceToChannel([]Transaction{})

	result := OrderTransactions(nodeID, emptyChan, nodeList)
	if len(result) != 0 {
		t.Errorf("Expected empty result, got %v transactions", len(result))
	}
}

func TestOrderTransactions_BasicOrdering(t *testing.T) {
	nodeID := "node1"
	nodeList := []string{"node1", "node2", "node3"}
	
	// Create transactions with varying timestamps, priorities and senders.
	tx1 := Transaction{ID: "tx1", Timestamp: 100, Priority: 1, Sender: "node2", Data: "data1"}
	tx2 := Transaction{ID: "tx2", Timestamp: 90, Priority: 1, Sender: "node1", Data: "data2"}
	tx3 := Transaction{ID: "tx3", Timestamp: 100, Priority: 2, Sender: "node3", Data: "data3"}
	tx4 := Transaction{ID: "tx4", Timestamp: 100, Priority: 2, Sender: "node1", Data: "data4"}
	
	// Expected order:
	// 1. tx2 (timestamp 90)
	// 2. Among tx1, tx3, tx4 (all timestamp 100):
	//    Priority: higher first so tx3 and tx4 (priority 2) come before tx1 (priority 1).
	//    Then tie break by Sender: between tx3 ("node3") and tx4 ("node1"), tx4 comes first.
	// Final order: tx2, tx4, tx3, tx1
	inputTransactions := []Transaction{tx1, tx2, tx3, tx4}
	transactionChan := sliceToChannel(inputTransactions)
	
	expected := []Transaction{tx2, tx4, tx3, tx1}
	
	result := OrderTransactions(nodeID, transactionChan, nodeList)
	
	// Since ordering is deterministic, compare length and then each transaction ID.
	if len(result) != len(expected) {
		t.Fatalf("Expected %d transactions, got %d", len(expected), len(result))
	}
	
	for i := range expected {
		if result[i].ID != expected[i].ID {
			t.Errorf("At index %d, expected transaction ID %s, got %s", i, expected[i].ID, result[i].ID)
		}
	}
}

func TestOrderTransactions_DuplicateTransactions(t *testing.T) {
	nodeID := "node2"
	nodeList := []string{"node1", "node2", "node3"}
	
	// Create duplicate transactions (same ID).
	txA := Transaction{ID: "dup1", Timestamp: 100, Priority: 1, Sender: "node1", Data: "first"}
	txB := Transaction{ID: "dup1", Timestamp: 100, Priority: 1, Sender: "node1", Data: "duplicate"}
	txC := Transaction{ID: "unique", Timestamp: 101, Priority: 1, Sender: "node2", Data: "unique data"}
	
	inputTransactions := []Transaction{txA, txB, txC}
	transactionChan := sliceToChannel(inputTransactions)
	
	result := OrderTransactions(nodeID, transactionChan, nodeList)
	
	// Expect that duplicate transactions are removed (only one instance exists).
	// Thus, the resulting length should be 2 and contain one instance of transaction with ID "dup1".
	seenDup := false
	for _, tx := range result {
		if tx.ID == "dup1" {
			if seenDup {
				t.Errorf("Duplicate transaction with ID 'dup1' found more than once")
			}
			seenDup = true
		}
	}
	if !seenDup {
		t.Errorf("Expected transaction with ID 'dup1' not found")
	}
	if len(result) != 2 {
		t.Errorf("Expected 2 transactions after duplicate removal, got %d", len(result))
	}
	
	// Additionally, ensure overall ordering is maintained.
	// Sort expected transactions according to the specification.
	expected := []Transaction{txA, txC}
	sort.Slice(expected, func(i, j int) bool {
		return compareTransactions(expected[i], expected[j])
	})
	
	if !reflect.DeepEqual(extractIDs(result), extractIDs(expected)) {
		t.Errorf("Expected ordering %v, got %v", extractIDs(expected), extractIDs(result))
	}
}

func TestOrderTransactions_InvalidTransactions(t *testing.T) {
	nodeID := "node3"
	nodeList := []string{"node1", "node2", "node3"}
	
	// For the purpose of testing, assume that a transaction with a "future" timestamp is invalid.
	// We'll simulate this by using a timestamp far in the future relative to a fixed point.
	currentUnix := time.Now().Unix()
	futureTimestamp := currentUnix + 1000000
	
	txValid := Transaction{ID: "tx_valid", Timestamp: currentUnix, Priority: 1, Sender: "node1", Data: "valid"}
	txInvalid := Transaction{ID: "tx_invalid", Timestamp: futureTimestamp, Priority: 1, Sender: "node2", Data: "invalid future timestamp"}
	
	inputTransactions := []Transaction{txValid, txInvalid}
	transactionChan := sliceToChannel(inputTransactions)
	
	result := OrderTransactions(nodeID, transactionChan, nodeList)
	
	// Expect that the invalid transaction is dropped from the final ordering.
	for _, tx := range result {
		if tx.ID == "tx_invalid" {
			t.Errorf("Invalid transaction with future timestamp was not dropped")
		}
	}
	
	// Also, the valid transaction should appear.
	foundValid := false
	for _, tx := range result {
		if tx.ID == "tx_valid" {
			foundValid = true
			break
		}
	}
	if !foundValid {
		t.Errorf("Valid transaction 'tx_valid' not found in the result")
	}
}