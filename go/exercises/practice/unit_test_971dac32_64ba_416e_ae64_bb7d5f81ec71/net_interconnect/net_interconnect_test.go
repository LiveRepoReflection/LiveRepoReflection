package network

import (
	"testing"
)

func TestMinimumHops(t *testing.T) {
	tests := []struct {
		name   string
		n      int
		r      int
		m      int
		k      int
		src    int
		dest   int
		want   int
		faults []FaultyLink
	}{
		{
			name: "Basic case with 16 servers",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  0,
			dest: 15,
			want: 4,
		},
		{
			name: "Same server src and dest",
			n:    100,
			r:    10,
			m:    5,
			k:    10,
			src:  42,
			dest: 42,
			want: 0,
		},
		{
			name: "Servers in same input switch but different output switches",
			n:    20,
			r:    5,
			m:    3,
			k:    5,
			src:  0,
			dest: 3,
			want: 4,
		},
		{
			name: "Large network",
			n:    10000,
			r:    100,
			m:    50,
			k:    100,
			src:  123,
			dest: 9876,
			want: 4,
		},
		{
			name: "Edge case - n equals r and k",
			n:    5,
			r:    5,
			m:    1,
			k:    5,
			src:  1,
			dest: 4,
			want: 4,
		},
		{
			name: "Invalid parameters - n not divisible by r",
			n:    10,
			r:    3,
			m:    2,
			k:    5,
			src:  1,
			dest: 8,
			want: -1,
		},
		{
			name: "Invalid parameters - n not divisible by k",
			n:    10,
			r:    2,
			m:    2,
			k:    3,
			src:  1,
			dest: 8,
			want: -1,
		},
		{
			name: "Invalid src - negative",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  -1,
			dest: 15,
			want: -1,
		},
		{
			name: "Invalid src - out of range",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  16,
			dest: 15,
			want: -1,
		},
		{
			name: "Invalid dest - negative",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  0,
			dest: -1,
			want: -1,
		},
		{
			name: "Invalid dest - out of range",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  0,
			dest: 16,
			want: -1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := MinimumHops(tt.n, tt.r, tt.m, tt.k, tt.src, tt.dest, nil); got != tt.want {
				t.Errorf("MinimumHops() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMinimumHopsWithFaultyLinks(t *testing.T) {
	tests := []struct {
		name   string
		n      int
		r      int
		m      int
		k      int
		src    int
		dest   int
		faults []FaultyLink
		want   int
	}{
		{
			name: "No faulty links",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  0,
			dest: 15,
			faults: []FaultyLink{},
			want: 4,
		},
		{
			name: "With some faulty middle links but path available",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  0,
			dest: 15,
			faults: []FaultyLink{
				{"middle", 0, 3},
				{"middle", 1, 3},
				{"middle", 2, 3},
			},
			want: 4, // Still one middle switch connects to output 3
		},
		{
			name: "All middle links to output broken - no path available",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  0,
			dest: 15,
			faults: []FaultyLink{
				{"middle", 0, 3},
				{"middle", 1, 3},
				{"middle", 2, 3},
				{"middle", 3, 3},
			},
			want: -1,
		},
		{
			name: "Input to all middle switches broken - no path available",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  0,
			dest: 15,
			faults: []FaultyLink{
				{"input", 0, 0},
				{"input", 0, 1},
				{"input", 0, 2},
				{"input", 0, 3},
			},
			want: -1,
		},
		{
			name: "Output to destination server broken - no path available",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  0,
			dest: 15,
			faults: []FaultyLink{
				{"output", 3, 15},
			},
			want: -1,
		},
		{
			name: "Complex scenario with multiple faulty links but path available",
			n:    100,
			r:    10,
			m:    10,
			k:    10,
			src:  5,
			dest: 95,
			faults: []FaultyLink{
				{"input", 0, 1},
				{"input", 0, 2},
				{"middle", 1, 9},
				{"middle", 2, 9},
				{"middle", 3, 9},
				{"output", 5, 55},
			},
			want: 4,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := MinimumHops(tt.n, tt.r, tt.m, tt.k, tt.src, tt.dest, tt.faults); got != tt.want {
				t.Errorf("MinimumHops() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkMinimumHops(b *testing.B) {
	benchmarks := []struct {
		name string
		n    int
		r    int
		m    int
		k    int
		src  int
		dest int
	}{
		{
			name: "Small network",
			n:    16,
			r:    4,
			m:    4,
			k:    4,
			src:  0,
			dest: 15,
		},
		{
			name: "Medium network",
			n:    1000,
			r:    50,
			m:    20,
			k:    50,
			src:  123,
			dest: 789,
		},
		{
			name: "Large network",
			n:    10000,
			r:    100,
			m:    50,
			k:    100,
			src:  1234,
			dest: 9876,
		},
	}

	for _, bm := range benchmarks {
		b.Run(bm.name, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				MinimumHops(bm.n, bm.r, bm.m, bm.k, bm.src, bm.dest, nil)
			}
		})
	}
}

func BenchmarkMinimumHopsWithFaultyLinks(b *testing.B) {
	// Setup a medium-sized network with some faulty links
	n, r, m, k := 1000, 50, 20, 50
	src, dest := 123, 789
	faults := []FaultyLink{
		{"input", 2, 5},
		{"middle", 10, 25},
		{"output", 30, 600},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MinimumHops(n, r, m, k, src, dest, faults)
	}
}