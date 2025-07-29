package stream_merger

import (
	"testing"
	"time"
)

type mockStream struct {
	values  []int
	current int
	stall   bool
	delay   time.Duration
}

func (m *mockStream) Next() (int, bool) {
	if m.current >= len(m.values) {
		return 0, false
	}

	if m.stall {
		time.Sleep(m.delay)
		m.stall = false
	}

	val := m.values[m.current]
	m.current++
	return val, true
}

func TestMergeKSortedStreams_Basic(t *testing.T) {
	streams := []Stream{
		&mockStream{values: []int{1, 4, 7}},
		&mockStream{values: []int{2, 5, 8}},
		&mockStream{values: []int{3, 6, 9}},
	}

	merger := MergeKSortedStreams(streams)
	expected := []int{1, 2, 3, 4, 5, 6, 7, 8, 9}

	for _, want := range expected {
		got, ok := merger.Next()
		if !ok {
			t.Fatalf("Expected %d but stream ended prematurely", want)
		}
		if got != want {
			t.Errorf("Expected %d, got %d", want, got)
		}
	}

	// Verify stream is properly exhausted
	if _, ok := merger.Next(); ok {
		t.Error("Expected stream to be exhausted but it returned more values")
	}
}

func TestMergeKSortedStreams_EmptyInput(t *testing.T) {
	merger := MergeKSortedStreams(nil)
	if _, ok := merger.Next(); ok {
		t.Error("Expected empty stream from nil input")
	}

	merger = MergeKSortedStreams([]Stream{})
	if _, ok := merger.Next(); ok {
		t.Error("Expected empty stream from empty slice input")
	}
}

func TestMergeKSortedStreams_StalledStreams(t *testing.T) {
	streams := []Stream{
		&mockStream{values: []int{1, 4, 7}, stall: true, delay: 100 * time.Millisecond},
		&mockStream{values: []int{2, 5, 8}},
		&mockStream{values: []int{3, 6, 9}},
	}

	merger := MergeKSortedStreams(streams)
	expected := []int{1, 2, 3, 4, 5, 6, 7, 8, 9}

	for _, want := range expected {
		got, ok := merger.Next()
		if !ok {
			t.Fatalf("Expected %d but stream ended prematurely", want)
		}
		if got != want {
			t.Errorf("Expected %d, got %d", want, got)
		}
	}
}

func TestMergeKSortedStreams_Duplicates(t *testing.T) {
	streams := []Stream{
		&mockStream{values: []int{1, 1, 3}},
		&mockStream{values: []int{1, 2, 2}},
		&mockStream{values: []int{2, 4, 4}},
	}

	merger := MergeKSortedStreams(streams)
	expected := []int{1, 1, 1, 2, 2, 2, 3, 4, 4}

	for _, want := range expected {
		got, ok := merger.Next()
		if !ok {
			t.Fatalf("Expected %d but stream ended prematurely", want)
		}
		if got != want {
			t.Errorf("Expected %d, got %d", want, got)
		}
	}
}

func TestMergeKSortedStreams_VaryingLengths(t *testing.T) {
	streams := []Stream{
		&mockStream{values: []int{1, 5}},
		&mockStream{values: []int{2, 6, 7, 10}},
		&mockStream{values: []int{3}},
		&mockStream{values: []int{4, 8, 9}},
	}

	merger := MergeKSortedStreams(streams)
	expected := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

	for _, want := range expected {
		got, ok := merger.Next()
		if !ok {
			t.Fatalf("Expected %d but stream ended prematurely", want)
		}
		if got != want {
			t.Errorf("Expected %d, got %d", want, got)
		}
	}
}

func BenchmarkMergeKSortedStreams(b *testing.B) {
	streams := make([]Stream, 100)
	for i := 0; i < 100; i++ {
		values := make([]int, 1000)
		for j := 0; j < 1000; j++ {
			values[j] = i*1000 + j
		}
		streams[i] = &mockStream{values: values}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		merger := MergeKSortedStreams(streams)
		for {
			if _, ok := merger.Next(); !ok {
				break
			}
		}
	}
}