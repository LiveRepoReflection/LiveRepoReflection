package bank_tx

import (
	"errors"
	"sync"
	"testing"
)

func TestInitialize(t *testing.T) {
	t.Run("valid initialization", func(t *testing.T) {
		b := NewBank()
		err := b.Initialize(3, []int{100, 200, 300})
		if err != nil {
			t.Fatalf("Initialize failed: %v", err)
		}

		for i, expected := range []int{100, 200, 300} {
			balance, err := b.GetBalance(i)
			if err != nil {
				t.Fatalf("GetBalance(%d) failed: %v", i, err)
			}
			if balance != expected {
				t.Errorf("GetBalance(%d) = %d, want %d", i, balance, expected)
			}
		}
	})

	t.Run("invalid branch count", func(t *testing.T) {
		b := NewBank()
		err := b.Initialize(2, []int{100, 200, 300})
		if !errors.Is(err, ErrInvalidBranchCount) {
			t.Errorf("Initialize() error = %v, want %v", err, ErrInvalidBranchCount)
		}
	})

	t.Run("negative balance", func(t *testing.T) {
		b := NewBank()
		err := b.Initialize(2, []int{100, -200})
		if !errors.Is(err, ErrNegativeBalance) {
			t.Errorf("Initialize() error = %v, want %v", err, ErrNegativeBalance)
		}
	})
}

func TestTransfer(t *testing.T) {
	b := NewBank()
	err := b.Initialize(3, []int{100, 200, 300})
	if err != nil {
		t.Fatal(err)
	}

	t.Run("successful transfer", func(t *testing.T) {
		err := b.Transfer(0, 1, 50)
		if err != nil {
			t.Fatalf("Transfer failed: %v", err)
		}

		balance0, _ := b.GetBalance(0)
		balance1, _ := b.GetBalance(1)
		if balance0 != 50 || balance1 != 250 {
			t.Errorf("Balances after transfer = %d, %d, want 50, 250", balance0, balance1)
		}
	})

	t.Run("insufficient funds", func(t *testing.T) {
		err := b.Transfer(0, 1, 100)
		if !errors.Is(err, ErrInsufficientFunds) {
			t.Errorf("Transfer() error = %v, want %v", err, ErrInsufficientFunds)
		}
	})

	t.Run("invalid branch", func(t *testing.T) {
		err := b.Transfer(-1, 1, 50)
		if !errors.Is(err, ErrInvalidBranchID) {
			t.Errorf("Transfer() error = %v, want %v", err, ErrInvalidBranchID)
		}

		err = b.Transfer(0, 3, 50)
		if !errors.Is(err, ErrInvalidBranchID) {
			t.Errorf("Transfer() error = %v, want %v", err, ErrInvalidBranchID)
		}
	})
}

func TestConcurrentTransfers(t *testing.T) {
	b := NewBank()
	err := b.Initialize(2, []int{1000, 1000})
	if err != nil {
		t.Fatal(err)
	}

	var wg sync.WaitGroup
	transfers := 100

	for i := 0; i < transfers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_ = b.Transfer(0, 1, 1)
			_ = b.Transfer(1, 0, 1)
		}()
	}

	wg.Wait()

	balance0, _ := b.GetBalance(0)
	balance1, _ := b.GetBalance(1)
	if balance0 != 1000 || balance1 != 1000 {
		t.Errorf("Final balances = %d, %d, want 1000, 1000", balance0, balance1)
	}
}

func TestNetworkPartition(t *testing.T) {
	b := NewBank()
	err := b.Initialize(3, []int{100, 200, 300})
	if err != nil {
		t.Fatal(err)
	}

	t.Run("partition affects transfers", func(t *testing.T) {
		err := b.SimulateNetworkPartition([]int{1})
		if err != nil {
			t.Fatal(err)
		}

		err = b.Transfer(0, 1, 50)
		if !errors.Is(err, ErrBranchUnavailable) {
			t.Errorf("Transfer() error = %v, want %v", err, ErrBranchUnavailable)
		}

		err = b.RecoverNetworkPartition([]int{1})
		if err != nil {
			t.Fatal(err)
		}

		err = b.Transfer(0, 1, 50)
		if err != nil {
			t.Fatalf("Transfer after recovery failed: %v", err)
		}
	})

	t.Run("partition affects balance checks", func(t *testing.T) {
		err := b.SimulateNetworkPartition([]int{2})
		if err != nil {
			t.Fatal(err)
		}

		_, err = b.GetBalance(2)
		if !errors.Is(err, ErrBranchUnavailable) {
			t.Errorf("GetBalance() error = %v, want %v", err, ErrBranchUnavailable)
		}
	})
}

func TestEdgeCases(t *testing.T) {
	b := NewBank()
	err := b.Initialize(2, []int{100, 200})
	if err != nil {
		t.Fatal(err)
	}

	t.Run("zero amount transfer", func(t *testing.T) {
		err := b.Transfer(0, 1, 0)
		if err != nil {
			t.Errorf("Transfer with zero amount failed: %v", err)
		}
	})

	t.Run("transfer to self", func(t *testing.T) {
		err := b.Transfer(0, 0, 50)
		if !errors.Is(err, ErrInvalidTransfer) {
			t.Errorf("Transfer() error = %v, want %v", err, ErrInvalidTransfer)
		}
	})
}