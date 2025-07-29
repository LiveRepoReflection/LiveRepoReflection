package taskscheduler

import (
	"reflect"
	"testing"
)

func TestScheduleTasks(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			gotOrder, gotSpan, gotFeasible := ScheduleTasks(tc.tasks)
			
			if gotFeasible != tc.wantFeasible {
				t.Errorf("ScheduleTasks() feasibility = %v, want %v", gotFeasible, tc.wantFeasible)
			}

			if !tc.wantFeasible {
				if len(gotOrder) != 0 || gotSpan != 0 {
					t.Errorf("ScheduleTasks() for infeasible case returned non-empty result: order=%v, span=%d", gotOrder, gotSpan)
				}
				return
			}

			if gotSpan != tc.wantSpan {
				t.Errorf("ScheduleTasks() span = %v, want %v", gotSpan, tc.wantSpan)
			}

			if tc.description != "multiple valid solutions" {
				if !reflect.DeepEqual(gotOrder, tc.wantOrder) {
					t.Errorf("ScheduleTasks() order = %v, want %v", gotOrder, tc.wantOrder)
				}
			} else {
				// For cases with multiple valid solutions, just verify the length
				if len(gotOrder) != len(tc.tasks) {
					t.Errorf("ScheduleTasks() order length = %d, want %d", len(gotOrder), len(tc.tasks))
				}
			}

			// Verify that the order respects dependencies
			timeMap := make(map[int]int)
			currentTime := 0
			for _, taskID := range gotOrder {
				var task Task
				for _, t := range tc.tasks {
					if t.ID == taskID {
						task = t
						break
					}
				}

				// Check all dependencies are completed
				for _, dep := range task.Dependencies {
					if completionTime, exists := timeMap[dep]; !exists {
						t.Errorf("Task %d scheduled before its dependency %d", taskID, dep)
					} else if currentTime < completionTime {
						t.Errorf("Task %d started at %d before dependency %d completed at %d", 
							taskID, currentTime, dep, completionTime)
					}
				}

				// Check deadline
				if currentTime+task.Duration > task.Deadline {
					t.Errorf("Task %d misses deadline: completes at %d, deadline was %d", 
						taskID, currentTime+task.Duration, task.Deadline)
				}

				timeMap[taskID] = currentTime + task.Duration
				currentTime += task.Duration
			}
		})
	}
}

func BenchmarkScheduleTasks(b *testing.B) {
	// Create a large test case
	largeTasks := make([]Task, 100)
	for i := 0; i < 100; i++ {
		deps := []int{}
		if i > 0 {
			deps = append(deps, i-1)
		}
		largeTasks[i] = Task{
			ID:           i,
			Duration:     1,
			Deadline:     200,
			Dependencies: deps,
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ScheduleTasks(largeTasks)
	}
}