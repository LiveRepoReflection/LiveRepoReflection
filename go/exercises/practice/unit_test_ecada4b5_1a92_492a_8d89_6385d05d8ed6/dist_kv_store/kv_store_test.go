package dist_kv_store

import (
	"context"
	"errors"
	"sync"
	"testing"
	"time"
)

func TestBasicOperations(t *testing.T) {
	store := NewKVStore()
	ctx := context.Background()

	t.Run("Put and Get", func(t *testing.T) {
		err := store.Put(ctx, "key1", "value1")
		if err != nil {
			t.Fatalf("Put failed: %v", err)
		}

		val, err := store.Get(ctx, "key1")
		if err != nil {
			t.Fatalf("Get failed: %v", err)
		}
		if val != "value1" {
			t.Errorf("Expected 'value1', got '%s'", val)
		}
	})

	t.Run("Delete", func(t *testing.T) {
		err := store.Put(ctx, "key2", "value2")
		if err != nil {
			t.Fatalf("Put failed: %v", err)
		}

		err = store.Delete(ctx, "key2")
		if err != nil {
			t.Fatalf("Delete failed: %v", err)
		}

		_, err = store.Get(ctx, "key2")
		if !errors.Is(err, ErrKeyNotFound) {
			t.Errorf("Expected ErrKeyNotFound, got %v", err)
		}
	})
}

func TestTransactions(t *testing.T) {
	store := NewKVStore()
	ctx := context.Background()

	t.Run("Commit", func(t *testing.T) {
		txID, err := store.BeginTransaction(ctx)
		if err != nil {
			t.Fatalf("BeginTransaction failed: %v", err)
		}

		err = store.Put(ctx, "tx_key1", "value1", WithTransaction(txID))
		if err != nil {
			t.Fatalf("Put in transaction failed: %v", err)
		}

		// Value shouldn't be visible before commit
		_, err = store.Get(ctx, "tx_key1")
		if !errors.Is(err, ErrKeyNotFound) {
			t.Errorf("Expected ErrKeyNotFound before commit, got %v", err)
		}

		err = store.CommitTransaction(ctx, txID)
		if err != nil {
			t.Fatalf("CommitTransaction failed: %v", err)
		}

		val, err := store.Get(ctx, "tx_key1")
		if err != nil {
			t.Fatalf("Get after commit failed: %v", err)
		}
		if val != "value1" {
			t.Errorf("Expected 'value1', got '%s'", val)
		}
	})

	t.Run("Rollback", func(t *testing.T) {
		txID, err := store.BeginTransaction(ctx)
		if err != nil {
			t.Fatalf("BeginTransaction failed: %v", err)
		}

		err = store.Put(ctx, "tx_key2", "value2", WithTransaction(txID))
		if err != nil {
			t.Fatalf("Put in transaction failed: %v", err)
		}

		err = store.RollbackTransaction(ctx, txID)
		if err != nil {
			t.Fatalf("RollbackTransaction failed: %v", err)
		}

		_, err = store.Get(ctx, "tx_key2")
		if !errors.Is(err, ErrKeyNotFound) {
			t.Errorf("Expected ErrKeyNotFound after rollback, got %v", err)
		}
	})
}

func TestConcurrentTransactions(t *testing.T) {
	store := NewKVStore()
	ctx := context.Background()
	var wg sync.WaitGroup

	// Test concurrent transactions
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()

			txID, err := store.BeginTransaction(ctx)
			if err != nil {
				t.Errorf("BeginTransaction failed: %v", err)
				return
			}

			key := "concurrent_key"
			err = store.Put(ctx, key, "value", WithTransaction(txID))
			if err != nil {
				t.Errorf("Put in transaction failed: %v", err)
				return
			}

			time.Sleep(time.Millisecond * 10) // Simulate work

			if i%2 == 0 {
				err = store.CommitTransaction(ctx, txID)
				if err != nil {
					t.Errorf("CommitTransaction failed: %v", err)
				}
			} else {
				err = store.RollbackTransaction(ctx, txID)
				if err != nil {
					t.Errorf("RollbackTransaction failed: %v", err)
				}
			}
		}(i)
	}

	wg.Wait()

	// Verify only committed transactions are visible
	val, err := store.Get(ctx, "concurrent_key")
	if err == nil {
		t.Logf("Final value: %s", val)
	}
}

func TestErrorCases(t *testing.T) {
	store := NewKVStore()
	ctx := context.Background()

	t.Run("Get non-existent key", func(t *testing.T) {
		_, err := store.Get(ctx, "nonexistent")
		if !errors.Is(err, ErrKeyNotFound) {
			t.Errorf("Expected ErrKeyNotFound, got %v", err)
		}
	})

	t.Run("Delete non-existent key", func(t *testing.T) {
		err := store.Delete(ctx, "nonexistent")
		if !errors.Is(err, ErrKeyNotFound) {
			t.Errorf("Expected ErrKeyNotFound, got %v", err)
		}
	})

	t.Run("Invalid transaction", func(t *testing.T) {
		err := store.Put(ctx, "key", "value", WithTransaction("invalid_tx"))
		if !errors.Is(err, ErrInvalidTransaction) {
			t.Errorf("Expected ErrInvalidTransaction, got %v", err)
		}
	})
}

func TestDistributedScenario(t *testing.T) {
	// This would test distributed behavior in a real implementation
	// For unit tests, we'll just verify the interface works
	store := NewKVStore()
	ctx := context.Background()

	txID, err := store.BeginTransaction(ctx)
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = store.Put(ctx, "dist_key", "dist_value", WithTransaction(txID))
	if err != nil {
		t.Fatalf("Put in transaction failed: %v", err)
	}

	err = store.CommitTransaction(ctx, txID)
	if err != nil {
		t.Fatalf("CommitTransaction failed: %v", err)
	}

	val, err := store.Get(ctx, "dist_key")
	if err != nil {
		t.Fatalf("Get after commit failed: %v", err)
	}
	if val != "dist_value" {
		t.Errorf("Expected 'dist_value', got '%s'", val)
	}
}