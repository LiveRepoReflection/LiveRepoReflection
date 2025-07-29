package bank_tx

import (
	"errors"
	"sync"
)

var (
	ErrInvalidBranchCount = errors.New("invalid branch count")
	ErrNegativeBalance    = errors.New("negative balance not allowed")
	ErrInvalidBranchID    = errors.New("invalid branch ID")
	ErrInsufficientFunds  = errors.New("insufficient funds")
	ErrBranchUnavailable  = errors.New("branch unavailable")
	ErrInvalidTransfer    = errors.New("invalid transfer")
)

type Bank struct {
	mu          sync.RWMutex
	balances    []int
	reservations map[int]int // branch ID -> reserved amount
	partitions  map[int]bool // branch ID -> partitioned status
}

func NewBank() *Bank {
	return &Bank{
		reservations: make(map[int]int),
		partitions:   make(map[int]bool),
	}
}

func (b *Bank) Initialize(N int, initialBalances []int) error {
	if len(initialBalances) != N {
		return ErrInvalidBranchCount
	}

	for _, balance := range initialBalances {
		if balance < 0 {
			return ErrNegativeBalance
		}
	}

	b.mu.Lock()
	defer b.mu.Unlock()

	b.balances = make([]int, N)
	copy(b.balances, initialBalances)
	b.reservations = make(map[int]int)
	b.partitions = make(map[int]bool)
	return nil
}

func (b *Bank) GetBalance(branch int) (int, error) {
	b.mu.RLock()
	defer b.mu.RUnlock()

	if branch < 0 || branch >= len(b.balances) {
		return 0, ErrInvalidBranchID
	}

	if b.partitions[branch] {
		return 0, ErrBranchUnavailable
	}

	return b.balances[branch] - b.reservations[branch], nil
}

func (b *Bank) Transfer(from, to, amount int) error {
	if from < 0 || from >= len(b.balances) || to < 0 || to >= len(b.balances) {
		return ErrInvalidBranchID
	}

	if from == to {
		return ErrInvalidTransfer
	}

	if amount < 0 {
		return ErrInvalidTransfer
	}

	b.mu.Lock()
	defer b.mu.Unlock()

	if b.partitions[from] || b.partitions[to] {
		return ErrBranchUnavailable
	}

	available := b.balances[from] - b.reservations[from]
	if available < amount {
		return ErrInsufficientFunds
	}

	b.reservations[from] += amount
	b.reservations[to] += amount

	b.balances[from] -= amount
	b.balances[to] += amount

	b.reservations[from] -= amount
	b.reservations[to] -= amount

	return nil
}

func (b *Bank) SimulateNetworkPartition(branches []int) error {
	b.mu.Lock()
	defer b.mu.Unlock()

	for _, branch := range branches {
		if branch < 0 || branch >= len(b.balances) {
			return ErrInvalidBranchID
		}
		b.partitions[branch] = true
	}
	return nil
}

func (b *Bank) RecoverNetworkPartition(branches []int) error {
	b.mu.Lock()
	defer b.mu.Unlock()

	for _, branch := range branches {
		if branch < 0 || branch >= len(b.balances) {
			return ErrInvalidBranchID
		}
		delete(b.partitions, branch)
	}
	return nil
}