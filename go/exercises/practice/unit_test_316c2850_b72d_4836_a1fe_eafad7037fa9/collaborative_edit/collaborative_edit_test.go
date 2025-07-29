package collaborative_edit

import (
	"reflect"
	"testing"
)

func TestApplyOperations(t *testing.T) {
	tests := []struct {
		name          string
		documentState map[string]string
		operations    []Operation
		want          map[string]string
	}{
		{
			name: "Basic operations",
			documentState: map[string]string{
				"section1": "Hello",
				"section2": "World",
			},
			operations: []Operation{
				{
					AuthorID:      "user1",
					Timestamp:     1,
					SectionID:     "section1",
					OperationType: "insert",
					Content:       ", user1!",
					Version:       0,
				},
				{
					AuthorID:      "user2",
					Timestamp:     2,
					SectionID:     "section2",
					OperationType: "replace",
					Content:       "Universe",
					Version:       0,
				},
			},
			want: map[string]string{
				"section1": "Hello, user1!",
				"section2": "Universe",
			},
		},
		{
			name: "Version conflict rejection",
			documentState: map[string]string{
				"section1": "Initial",
			},
			operations: []Operation{
				{
					AuthorID:      "user1",
					Timestamp:     1,
					SectionID:     "section1",
					OperationType: "replace",
					Content:       "First",
					Version:       0,
				},
				{
					AuthorID:      "user2",
					Timestamp:     2,
					SectionID:     "section1",
					OperationType: "replace",
					Content:       "Second",
					Version:       0, // Should be rejected as version should be 1
				},
			},
			want: map[string]string{
				"section1": "First",
			},
		},
		{
			name: "Delete operations",
			documentState: map[string]string{
				"section1": "Delete me",
				"section2": "Replace with empty",
			},
			operations: []Operation{
				{
					AuthorID:      "user1",
					Timestamp:     1,
					SectionID:     "section1",
					OperationType: "delete",
					Content:       "",
					Version:       0,
				},
				{
					AuthorID:      "user2",
					Timestamp:     2,
					SectionID:     "section2",
					OperationType: "delete",
					Content:       "New content",
					Version:       0,
				},
			},
			want: map[string]string{
				"section1": "",
				"section2": "New content",
			},
		},
		{
			name: "Same timestamp operations",
			documentState: map[string]string{
				"section1": "Initial",
			},
			operations: []Operation{
				{
					AuthorID:      "user1",
					Timestamp:     1,
					SectionID:     "section1",
					OperationType: "replace",
					Content:       "First",
					Version:       0,
				},
				{
					AuthorID:      "user2",
					Timestamp:     1,
					SectionID:     "section1",
					OperationType: "replace",
					Content:       "Second",
					Version:       1,
				},
			},
			want: map[string]string{
				"section1": "Second",
			},
		},
		{
			name: "New section creation",
			documentState: map[string]string{
				"section1": "Existing",
			},
			operations: []Operation{
				{
					AuthorID:      "user1",
					Timestamp:     1,
					SectionID:     "section2",
					OperationType: "insert",
					Content:       "New section",
					Version:       0,
				},
			},
			want: map[string]string{
				"section1": "Existing",
				"section2": "New section",
			},
		},
		{
			name:          "Empty initial state",
			documentState: map[string]string{},
			operations: []Operation{
				{
					AuthorID:      "user1",
					Timestamp:     1,
					SectionID:     "section1",
					OperationType: "insert",
					Content:       "First content",
					Version:       0,
				},
			},
			want: map[string]string{
				"section1": "First content",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create a copy of the input state to ensure it's not modified
			inputState := make(map[string]string)
			for k, v := range tt.documentState {
				inputState[k] = v
			}

			got := ApplyOperations(inputState, tt.operations)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ApplyOperations() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkApplyOperations(b *testing.B) {
	documentState := map[string]string{
		"section1": "Hello",
		"section2": "World",
		"section3": "Benchmark",
	}

	operations := []Operation{
		{
			AuthorID:      "user1",
			Timestamp:     1,
			SectionID:     "section1",
			OperationType: "insert",
			Content:       ", modified!",
			Version:       0,
		},
		{
			AuthorID:      "user2",
			Timestamp:     2,
			SectionID:     "section2",
			OperationType: "replace",
			Content:       "Universe",
			Version:       0,
		},
		{
			AuthorID:      "user3",
			Timestamp:     3,
			SectionID:     "section3",
			OperationType: "delete",
			Content:       "",
			Version:       0,
		},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		// Create a fresh copy of the document state for each iteration
		stateCopy := make(map[string]string)
		for k, v := range documentState {
			stateCopy[k] = v
		}
		ApplyOperations(stateCopy, operations)
	}
}