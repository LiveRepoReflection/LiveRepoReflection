package transaction_ordering

import (
	"sort"
	"sync"
	"time"
)

type Transaction struct {
	From      int
	To        int
	Amount    int
	Timestamp time.Time
}

type TransactionProcessor struct {
	balances map[int]int
	mu       sync.Mutex
}

func NewTransactionProcessor(initialBalances map[int]int) *TransactionProcessor {
	balances := make(map[int]int)
	for k, v := range initialBalances {
		balances[k] = v
	}
	return &TransactionProcessor{balances: balances}
}

func (tp *TransactionProcessor) Process(transactions []Transaction) []Transaction {
	sorted := make([]Transaction, len(transactions))
	copy(sorted, transactions)

	sort.Slice(sorted, func(i, j int) bool {
		if sorted[i].Timestamp.Equal(sorted[j].Timestamp) {
			if sorted[i].From == sorted[j].From {
				return sorted[i].To < sorted[j].To
			}
			return sorted[i].From < sorted[j].From
		}
		return sorted[i].Timestamp.Before(sorted[j].Timestamp)
	})

	var rejected []Transaction
	var wg sync.WaitGroup
	rejectChan := make(chan Transaction, len(sorted))

	for _, txn := range sorted {
		wg.Add(1)
		go func(t Transaction) {
			defer wg.Done()
			if !tp.processTransaction(t) {
				rejectChan <- t
			}
		}(txn)
	}

	go func() {
		wg.Wait()
		close(rejectChan)
	}()

	for t := range rejectChan {
		rejected = append(rejected, t)
	}

	return rejected
}

func (tp *TransactionProcessor) processTransaction(t Transaction) bool {
	tp.mu.Lock()
	defer tp.mu.Unlock()

	if tp.balances[t.From] < t.Amount {
		return false
	}

	tp.balances[t.From] -= t.Amount
	tp.balances[t.To] += t.Amount
	return true
}

func (tp *TransactionProcessor) GetBalances() map[int]int {
	tp.mu.Lock()
	defer tp.mu.Unlock()

	balances := make(map[int]int)
	for k, v := range tp.balances {
		balances[k] = v
	}
	return balances
}