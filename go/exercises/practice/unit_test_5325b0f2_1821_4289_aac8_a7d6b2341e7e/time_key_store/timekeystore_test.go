package timekeystore

import (
    "sync"
    "testing"
)

func TestTimeKeyStore(t *testing.T) {
    for _, tc := range tests {
        t.Run(tc.description, func(t *testing.T) {
            store := Constructor()
            results := make([]string, 0)

            for _, op := range tc.operations {
                switch op.op {
                case "set":
                    store.Set(op.key, op.value, op.timestamp)
                    results = append(results, "")
                case "get":
                    result := store.Get(op.key, op.timestamp)
                    results = append(results, result)
                }
            }

            if len(results) != len(tc.expected) {
                t.Fatalf("Expected %d results, got %d", len(tc.expected), len(results))
            }

            for i := range results {
                if results[i] != tc.expected[i] {
                    t.Errorf("Operation %d: expected %q, got %q", i, tc.expected[i], results[i])
                }
            }
        })
    }
}

func TestConcurrent(t *testing.T) {
    store := Constructor()
    var wg sync.WaitGroup
    numGoroutines := 100

    // Concurrent sets
    for i := 0; i < numGoroutines; i++ {
        wg.Add(1)
        go func(i int) {
            defer wg.Done()
            store.Set("key", string(rune('A'+i%26)), i+1)
        }(i)
    }

    // Concurrent gets
    for i := 0; i < numGoroutines; i++ {
        wg.Add(1)
        go func(i int) {
            defer wg.Done()
            _ = store.Get("key", i+1)
        }(i)
    }

    wg.Wait()
}

func BenchmarkSet(b *testing.B) {
    store := Constructor()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        store.Set("key", "value", i+1)
    }
}

func BenchmarkGet(b *testing.B) {
    store := Constructor()
    // Pre-populate with some data
    for i := 0; i < 1000; i++ {
        store.Set("key", "value", i+1)
    }
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        store.Get("key", i%1000+1)
    }
}

func BenchmarkConcurrentOperations(b *testing.B) {
    store := Constructor()
    b.RunParallel(func(pb *testing.PB) {
        i := 0
        for pb.Next() {
            if i%2 == 0 {
                store.Set("key", "value", i+1)
            } else {
                store.Get("key", i+1)
            }
            i++
        }
    })
}