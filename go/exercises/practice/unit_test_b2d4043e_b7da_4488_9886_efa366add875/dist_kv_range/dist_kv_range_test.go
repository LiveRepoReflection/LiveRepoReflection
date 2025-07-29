package dist_kv_range

import (
	"fmt"
	"math/rand"
	"strconv"
	"sync"
	"testing"
	"time"
)

// The following tests assume that a Store type is available in the package
// along with the following functions and methods:
//   NewStore(nodeCount int) *Store
//   (s *Store) Put(key uint64, value string)
//   (s *Store) Get(key uint64) string
//   (s *Store) RangeQuery(startKey, endKey uint64) map[uint64]string
//
// These tests validate the expected behavior of the distributed key-value store.

func setupStoreWithKeys(t *testing.T) *Store {
	store := NewStore(5)
	// Insert keys 0,10,20,...,90 into the store.
	for i := uint64(0); i < 100; i += 10 {
		store.Put(i, fmt.Sprintf("value_%d", i))
	}
	return store
}

func TestPutAndGet(t *testing.T) {
	store := NewStore(3)
	keys := []uint64{1, 2, 3, 100, 1000}
	for _, key := range keys {
		expected := fmt.Sprintf("val_%d", key)
		store.Put(key, expected)
		got := store.Get(key)
		if got != expected {
			t.Errorf("Get(%d) = %s, expected %s", key, got, expected)
		}
	}
}

func TestGetNonExistentKey(t *testing.T) {
	store := NewStore(3)
	// Retrieving a key that was not inserted should return an empty string.
	if got := store.Get(9999); got != "" {
		t.Errorf("Get(9999) = %s, expected empty string", got)
	}
}

func TestRangeQuery(t *testing.T) {
	store := NewStore(4)
	// Insert a set of keys with distinct values.
	keysToInsert := []uint64{10, 20, 30, 40, 50, 60, 70}
	for _, key := range keysToInsert {
		store.Put(key, fmt.Sprintf("v%d", key))
	}

	// Query a range that should include keys 30, 40, 50, and 60.
	result := store.RangeQuery(25, 65)
	expected := map[uint64]string{
		30: "v30",
		40: "v40",
		50: "v50",
		60: "v60",
	}
	if len(result) != len(expected) {
		t.Fatalf("RangeQuery(25,65) returned %d items, expected %d", len(result), len(expected))
	}
	for k, v := range expected {
		if got, ok := result[k]; !ok || got != v {
			t.Errorf("For key %d, got %s, expected %s", k, got, v)
		}
	}
}

func TestRangeQueryStartGreaterThanEnd(t *testing.T) {
	store := NewStore(4)
	store.Put(10, "v10")
	store.Put(20, "v20")
	// When startKey > endKey, RangeQuery should return an empty map.
	result := store.RangeQuery(50, 30)
	if len(result) != 0 {
		t.Errorf("RangeQuery(50,30) expected empty result, got %v", result)
	}
}

func TestConcurrentAccess(t *testing.T) {
	store := NewStore(8)
	var wg sync.WaitGroup
	numGoroutines := 50
	numOps := 100

	// Seed the random number generator.
	rand.Seed(time.Now().UnixNano())

	// Concurrently perform Put and Get operations.
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for j := 0; j < numOps; j++ {
				key := uint64(rand.Intn(1000))
				val := "goroutine_" + strconv.Itoa(id) + "_" + strconv.Itoa(j)
				store.Put(key, val)
				// Immediately read after write.
				got := store.Get(key)
				// Since concurrent writes may override each other,
				// check that some non-empty value is returned.
				if got == "" {
					t.Errorf("Concurrent Get(%d) returned empty string after put", key)
				}
			}
		}(i)
	}
	wg.Wait()
}

func TestRangeQueryConcurrent(t *testing.T) {
	store := setupStoreWithKeys(t)
	var wg sync.WaitGroup
	numGoroutines := 20

	// Seed the random number generator.
	rand.Seed(time.Now().UnixNano())

	// Perform concurrent range queries over random intervals.
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			start := uint64(rand.Intn(50))
			end := start + uint64(rand.Intn(50))
			_ = store.RangeQuery(start, end)
		}()
	}
	wg.Wait()
}

func TestOverwriteKey(t *testing.T) {
	store := NewStore(3)
	key := uint64(123)
	store.Put(key, "initial")
	store.Put(key, "overwrite")
	result := store.Get(key)
	if result != "overwrite" {
		t.Errorf("Overwrite test failed: got %s, expected %s", result, "overwrite")
	}
}