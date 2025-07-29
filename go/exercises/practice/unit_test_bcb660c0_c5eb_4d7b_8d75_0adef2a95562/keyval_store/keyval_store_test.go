package keyval_store

import (
	"os"
	"testing"
)

func TestKeyValStore(t *testing.T) {
	// Initialize store
	store := NewKeyValStore()

	// Test basic operations
	t.Run("Put and Get", func(t *testing.T) {
		store.Put("key1", "value1")
		if val := store.Get("key1"); val != "value1" {
			t.Errorf("Get() = %v, want %v", val, "value1")
		}
	})

	t.Run("Get non-existent key", func(t *testing.T) {
		if val := store.Get("nonexistent"); val != "" {
			t.Errorf("Get() = %v, want empty string", val)
		}
	})

	t.Run("Delete", func(t *testing.T) {
		store.Put("key2", "value2")
		store.Delete("key2")
		if val := store.Get("key2"); val != "" {
			t.Errorf("Get() after Delete() = %v, want empty string", val)
		}
	})

	// Test range operations
	t.Run("Range", func(t *testing.T) {
		store.Put("a", "1")
		store.Put("b", "2")
		store.Put("c", "3")
		store.Put("d", "4")

		results := store.Range("b", "d")
		if len(results) != 2 {
			t.Errorf("Range() returned %d items, want 2", len(results))
		}
		if results[0].Key != "b" || results[0].Value != "2" {
			t.Errorf("Range() first item = %v, want {b 2}", results[0])
		}
		if results[1].Key != "c" || results[1].Value != "3" {
			t.Errorf("Range() second item = %v, want {c 3}", results[1])
		}
	})

	t.Run("Count", func(t *testing.T) {
		count := store.Count("a", "e")
		if count != 4 {
			t.Errorf("Count() = %d, want 4", count)
		}
	})

	// Test persistence
	t.Run("Backup and Restore", func(t *testing.T) {
		testFile := "test_backup.dat"
		defer os.Remove(testFile)

		err := store.Backup(testFile)
		if err != nil {
			t.Fatalf("Backup() failed: %v", err)
		}

		newStore := NewKeyValStore()
		err = newStore.Restore(testFile)
		if err != nil {
			t.Fatalf("Restore() failed: %v", err)
		}

		if val := newStore.Get("a"); val != "1" {
			t.Errorf("Restored Get(a) = %v, want 1", val)
		}
	})

	// Test concurrency
	t.Run("Concurrent operations", func(t *testing.T) {
		done := make(chan bool)
		go func() {
			for i := 0; i < 1000; i++ {
				store.Put("concurrent", "value")
			}
			done <- true
		}()
		go func() {
			for i := 0; i < 1000; i++ {
				store.Get("concurrent")
			}
			done <- true
		}()
		<-done
		<-done
	})
}