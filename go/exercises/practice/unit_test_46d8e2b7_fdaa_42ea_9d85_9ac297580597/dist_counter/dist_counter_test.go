package dist_counter

import (
	"sync"
	"testing"
	"time"
)

func TestCounterBasic(t *testing.T) {
	c := NewCounter()
	if val := c.Get(); val != 0 {
		t.Errorf("Expected initial value 0, got %d", val)
	}

	if val := c.Increment(); val != 1 {
		t.Errorf("Expected incremented value 1, got %d", val)
	}

	if val := c.Get(); val != 1 {
		t.Errorf("Expected get value 1, got %d", val)
	}
}

func TestCounterConcurrentIncrement(t *testing.T) {
	c := NewCounter()
	var wg sync.WaitGroup
	const routines = 100

	wg.Add(routines)
	for i := 0; i < routines; i++ {
		go func() {
			c.Increment()
			wg.Done()
		}()
	}
	wg.Wait()

	if val := c.Get(); val != routines {
		t.Errorf("Expected final value %d, got %d", routines, val)
	}
}

func TestCounterSync(t *testing.T) {
	c1 := NewCounter()
	c2 := NewCounter()

	c1.Increment()
	c1.Increment()
	c2.Increment()

	// Sync c2 with c1's state
	c2.Sync([]int64{c1.Get()})

	if val := c2.Get(); val != 2 {
		t.Errorf("Expected c2 to sync to 2, got %d", val)
	}

	// Sync c1 with c2's state (shouldn't change)
	c1.Sync([]int64{c2.Get()})
	if val := c1.Get(); val != 2 {
		t.Errorf("Expected c1 to remain at 2, got %d", val)
	}
}

func TestCounterEventualConsistency(t *testing.T) {
	const nodes = 5
	counters := make([]*Counter, nodes)
	for i := range counters {
		counters[i] = NewCounter()
	}

	// Simulate independent increments
	for i := 0; i < 100; i++ {
		counters[i%nodes].Increment()
	}

	// Simulate periodic syncs
	for syncRound := 0; syncRound < 10; syncRound++ {
		for i := 0; i < nodes; i++ {
			otherValues := make([]int64, 0, nodes-1)
			for j := 0; j < nodes; j++ {
				if j != i {
					otherValues = append(otherValues, counters[j].Get())
				}
			}
			counters[i].Sync(otherValues)
		}
	}

	// Verify all nodes converged to same value
	expected := counters[0].Get()
	for i := 1; i < nodes; i++ {
		if val := counters[i].Get(); val != expected {
			t.Errorf("Node %d has value %d, expected %d", i, val, expected)
		}
	}
}

func TestCounterMonotonic(t *testing.T) {
	c := NewCounter()
	vals := make([]int64, 0, 100)

	var wg sync.WaitGroup
	wg.Add(2)

	// Concurrent increments
	go func() {
		for i := 0; i < 50; i++ {
			vals = append(vals, c.Increment())
			time.Sleep(time.Millisecond)
		}
		wg.Done()
	}()

	// Concurrent syncs with higher values
	go func() {
		for i := 0; i < 50; i++ {
			c.Sync([]int64{int64(i + 100)})
			vals = append(vals, c.Get())
			time.Sleep(time.Millisecond)
		}
		wg.Done()
	}()

	wg.Wait()

	// Verify all values are monotonically increasing
	for i := 1; i < len(vals); i++ {
		if vals[i] < vals[i-1] {
			t.Errorf("Counter decreased from %d to %d", vals[i-1], vals[i])
		}
	}
}

func BenchmarkCounterIncrement(b *testing.B) {
	c := NewCounter()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		c.Increment()
	}
}

func BenchmarkCounterSync(b *testing.B) {
	c := NewCounter()
	otherValues := []int64{100, 200, 300, 400, 500}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		c.Sync(otherValues)
	}
}