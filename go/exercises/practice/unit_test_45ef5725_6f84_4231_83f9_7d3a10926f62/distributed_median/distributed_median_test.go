package distributed_median

import (
	"testing"
	"time"
)

func TestCalculateDistributedMedian(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			coordinator := NewCoordinatorNode()
			
			// Simulate workers sending their buffers to coordinator
			for _, buffer := range tc.workerBuffers {
				worker := NewWorkerNode(len(buffer))
				for _, num := range buffer {
					worker.ReceiveNumber(num)
				}
				coordinator.ReceiveWorkerBuffer(worker.GetBuffer())
			}

			// Allow time for coordinator to process (if async)
			time.Sleep(100 * time.Millisecond)
			
			median := coordinator.CalculateMedian()
			if median != tc.expectedMedian {
				t.Errorf("Expected median %.1f, got %.1f", tc.expectedMedian, median)
			}
		})
	}
}

func BenchmarkCalculateDistributedMedian(b *testing.B) {
	coordinator := NewCoordinatorNode()
	workers := make([]*WorkerNode, 1000)
	
	// Setup 1000 workers with sample data
	for i := 0; i < 1000; i++ {
		workers[i] = NewWorkerNode(100)
		for j := 0; j < 100; j++ {
			workers[i].ReceiveNumber((i * 100) + j)
		}
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		// Simulate sending all worker buffers to coordinator
		for _, worker := range workers {
			coordinator.ReceiveWorkerBuffer(worker.GetBuffer())
		}
		coordinator.CalculateMedian()
	}
}

func TestWorkerNodeBufferManagement(t *testing.T) {
	tests := []struct {
		name          string
		bufferSize    int
		inputNumbers  []int
		expectedCount int
	}{
		{
			name:          "buffer not full",
			bufferSize:    5,
			inputNumbers:  []int{1, 2, 3},
			expectedCount: 3,
		},
		{
			name:          "buffer exactly full",
			bufferSize:    3,
			inputNumbers:  []int{1, 2, 3},
			expectedCount: 3,
		},
		{
			name:          "buffer over capacity",
			bufferSize:    3,
			inputNumbers:  []int{1, 2, 3, 4, 5},
			expectedCount: 3,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			worker := NewWorkerNode(tt.bufferSize)
			for _, num := range tt.inputNumbers {
				worker.ReceiveNumber(num)
			}
			buffer := worker.GetBuffer()
			if len(buffer) != tt.expectedCount {
				t.Errorf("Expected buffer size %d, got %d", tt.expectedCount, len(buffer))
			}
		})
	}
}