package task_deadlock

import (
	"reflect"
	"testing"
)

func TestDetectDeadlock(t *testing.T) {
	tests := []struct {
		name     string
		tasks    []Task
		capacity int
		want     []int
	}{
		{
			name: "simple deadlock cycle",
			tasks: []Task{
				{ID: 1, Dependencies: []int{2}},
				{ID: 2, Dependencies: []int{3}},
				{ID: 3, Dependencies: []int{1}},
			},
			capacity: 1,
			want:     []int{1, 2, 3},
		},
		{
			name: "no deadlock",
			tasks: []Task{
				{ID: 1, Dependencies: []int{}},
				{ID: 2, Dependencies: []int{1}},
				{ID: 3, Dependencies: []int{2}},
			},
			capacity: 1,
			want:     []int{},
		},
		{
			name: "multiple dependencies no deadlock",
			tasks: []Task{
				{ID: 1, Dependencies: []int{2, 3}},
				{ID: 2, Dependencies: []int{}},
				{ID: 3, Dependencies: []int{}},
			},
			capacity: 1,
			want:     []int{},
		},
		{
			name: "multiple deadlock cycles",
			tasks: []Task{
				{ID: 1, Dependencies: []int{2}},
				{ID: 2, Dependencies: []int{1}},
				{ID: 3, Dependencies: []int{4}},
				{ID: 4, Dependencies: []int{3}},
				{ID: 5, Dependencies: []int{}},
			},
			capacity: 1,
			want:     []int{1, 2},
		},
		{
			name: "nested deadlock cycle",
			tasks: []Task{
				{ID: 1, Dependencies: []int{2}},
				{ID: 2, Dependencies: []int{3}},
				{ID: 3, Dependencies: []int{4}},
				{ID: 4, Dependencies: []int{2}},
			},
			capacity: 2,
			want:     []int{2, 3, 4},
		},
		{
			name: "large capacity no deadlock",
			tasks: []Task{
				{ID: 1, Dependencies: []int{2}},
				{ID: 2, Dependencies: []int{1}},
				{ID: 3, Dependencies: []int{4}},
				{ID: 4, Dependencies: []int{3}},
				{ID: 5, Dependencies: []int{1, 2, 3, 4}},
			},
			capacity: 2,
			want:     []int{1, 2},
		},
		{
			name:     "empty task list",
			tasks:    []Task{},
			capacity: 5,
			want:     []int{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := DetectDeadlock(tt.tasks, tt.capacity)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("DetectDeadlock() = %v, want %v", got, tt.want)
			}
		})
	}
}