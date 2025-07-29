package skyline_reconstruction

import (
	"reflect"
	"testing"
)

func TestGetSkyline(t *testing.T) {
	tests := []struct {
		name      string
		buildings [][]int
		want      [][]int
	}{
		{
			name:      "empty input",
			buildings: [][]int{},
			want:      [][]int{},
		},
		{
			name:      "single building",
			buildings: [][]int{{2, 9, 10}},
			want:      [][]int{{2, 10}, {9, 0}},
		},
		{
			name:      "two non-overlapping buildings",
			buildings: [][]int{{2, 9, 10}, {12, 16, 8}},
			want:      [][]int{{2, 10}, {9, 0}, {12, 8}, {16, 0}},
		},
		{
			name:      "two overlapping buildings",
			buildings: [][]int{{2, 9, 10}, {3, 7, 15}},
			want:      [][]int{{2, 10}, {3, 15}, {7, 10}, {9, 0}},
		},
		{
			name:      "multiple buildings with complex overlaps",
			buildings: [][]int{{2, 9, 10}, {3, 7, 15}, {5, 12, 12}, {15, 20, 10}, {19, 24, 8}},
			want:      [][]int{{2, 10}, {3, 15}, {7, 12}, {12, 0}, {15, 10}, {20, 8}, {24, 0}},
		},
		{
			name:      "buildings with same height",
			buildings: [][]int{{0, 2, 3}, {2, 5, 3}},
			want:      [][]int{{0, 3}, {5, 0}},
		},
		{
			name:      "tall building behind short one",
			buildings: [][]int{{1, 5, 5}, {2, 4, 3}},
			want:      [][]int{{1, 5}, {5, 0}},
		},
		{
			name:      "adjacent buildings",
			buildings: [][]int{{1, 3, 4}, {3, 5, 4}},
			want:      [][]int{{1, 4}, {5, 0}},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := GetSkyline(tt.buildings); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("GetSkyline() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkGetSkyline(b *testing.B) {
	buildings := [][]int{
		{2, 9, 10}, {3, 7, 15}, {5, 12, 12},
		{15, 20, 10}, {19, 24, 8}, {25, 30, 12},
		{28, 35, 15}, {32, 40, 10}, {38, 45, 8},
	}
	for i := 0; i < b.N; i++ {
		GetSkyline(buildings)
	}
}