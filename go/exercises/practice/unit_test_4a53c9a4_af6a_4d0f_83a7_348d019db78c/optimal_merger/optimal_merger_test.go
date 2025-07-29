package optimalmerger

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func createTestFile(name string, content string) error {
	return os.WriteFile(name, []byte(content), 0644)
}

func cleanupTestFiles(files []string) {
	for _, f := range files {
		os.Remove(f)
	}
}

func TestOptimalMerger(t *testing.T) {
	testCases := []struct {
		name           string
		inputFiles     []string
		inputContents  []string
		memoryBudget   int64
		maxOpenFiles   int
		expectedError  error
		expectedOutput string
	}{
		{
			name:          "Basic merge test",
			inputFiles:    []string{"file1.log", "file2.log", "file3.log"},
			inputContents: []string{
				"1000 log entry 1\n1002 log entry 2\n1004 log entry 3\n",
				"1001 log entry 4\n1003 log entry 5\n1005 log entry 6\n",
				"1006 log entry 7\n1007 log entry 8\n1008 log entry 9\n",
			},
			memoryBudget: 1024 * 1024, // 1MB
			maxOpenFiles: 5,
			expectedOutput: "1000 log entry 1\n1001 log entry 4\n1002 log entry 2\n" +
				"1003 log entry 5\n1004 log entry 3\n1005 log entry 6\n" +
				"1006 log entry 7\n1007 log entry 8\n1008 log entry 9\n",
		},
		{
			name:          "Empty files test",
			inputFiles:    []string{"empty1.log", "empty2.log"},
			inputContents: []string{"", ""},
			memoryBudget:  1024 * 1024,
			maxOpenFiles:  5,
			expectedOutput: "",
		},
		{
			name:          "Single timestamp test",
			inputFiles:    []string{"same1.log", "same2.log"},
			inputContents: []string{
				"1000 first entry\n1000 second entry\n",
				"1000 third entry\n1000 fourth entry\n",
			},
			memoryBudget:  1024 * 1024,
			maxOpenFiles:  5,
			expectedOutput: "1000 first entry\n1000 second entry\n1000 third entry\n1000 fourth entry\n",
		},
		{
			name:          "Limited file handles test",
			inputFiles:    []string{"file1.log", "file2.log", "file3.log", "file4.log"},
			inputContents: []string{
				"1000 entry 1\n",
				"1001 entry 2\n",
				"1002 entry 3\n",
				"1003 entry 4\n",
			},
			memoryBudget: 1024 * 1024,
			maxOpenFiles: 2, // Very limited file handles
			expectedOutput: "1000 entry 1\n1001 entry 2\n1002 entry 3\n1003 entry 4\n",
		},
		{
			name:          "Limited memory test",
			inputFiles:    []string{"big1.log", "big2.log"},
			inputContents: []string{
				strings.Repeat("1000 very long entry\n", 100),
				strings.Repeat("1001 very long entry\n", 100),
			},
			memoryBudget: 1024, // Very limited memory
			maxOpenFiles: 5,
			expectedOutput: strings.Repeat("1000 very long entry\n", 100) +
				strings.Repeat("1001 very long entry\n", 100),
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Create temporary directory for test files
			tmpDir, err := os.MkdirTemp("", "merger_test")
			if err != nil {
				t.Fatalf("Failed to create temp directory: %v", err)
			}
			defer os.RemoveAll(tmpDir)

			// Create input files
			var fullPaths []string
			for i, filename := range tc.inputFiles {
				fullPath := filepath.Join(tmpDir, filename)
				fullPaths = append(fullPaths, fullPath)
				if err := createTestFile(fullPath, tc.inputContents[i]); err != nil {
					t.Fatalf("Failed to create test file %s: %v", filename, err)
				}
			}

			// Create output file path
			outputPath := filepath.Join(tmpDir, "output.log")

			// Run merger
			merger := New()
			err = merger.Merge(fullPaths, outputPath, tc.memoryBudget, tc.maxOpenFiles)

			// Check error if expected
			if tc.expectedError != nil {
				if err == nil {
					t.Errorf("Expected error %v, got nil", tc.expectedError)
				} else if err.Error() != tc.expectedError.Error() {
					t.Errorf("Expected error %v, got %v", tc.expectedError, err)
				}
				return
			}

			// Check for unexpected error
			if err != nil {
				t.Fatalf("Unexpected error: %v", err)
			}

			// Read and verify output
			output, err := os.ReadFile(outputPath)
			if err != nil {
				t.Fatalf("Failed to read output file: %v", err)
			}

			if string(output) != tc.expectedOutput {
				t.Errorf("Output mismatch\nExpected:\n%s\nGot:\n%s",
					tc.expectedOutput, string(output))
			}

			// Verify sorting
			lines := strings.Split(strings.TrimSpace(string(output)), "\n")
			if len(lines) > 0 && lines[0] != "" {
				var prevTimestamp int64
				for i, line := range lines {
					var timestamp int64
					_, err := fmt.Sscanf(line, "%d", &timestamp)
					if err != nil {
						t.Errorf("Invalid timestamp format in line: %s", line)
						continue
					}
					if i > 0 && timestamp < prevTimestamp {
						t.Errorf("Timestamps not in order: %d comes after %d",
							timestamp, prevTimestamp)
					}
					prevTimestamp = timestamp
				}
			}
		})
	}
}

func TestMergerErrors(t *testing.T) {
	testCases := []struct {
		name          string
		inputFiles    []string
		memoryBudget  int64
		maxOpenFiles  int
		expectedError string
	}{
		{
			name:          "No input files",
			inputFiles:    []string{},
			memoryBudget:  1024 * 1024,
			maxOpenFiles:  5,
			expectedError: "no input files provided",
		},
		{
			name:          "Invalid file path",
			inputFiles:    []string{"nonexistent.log"},
			memoryBudget:  1024 * 1024,
			maxOpenFiles:  5,
			expectedError: "failed to open input file",
		},
		{
			name:          "Zero memory budget",
			inputFiles:    []string{"file1.log"},
			memoryBudget:  0,
			maxOpenFiles:  5,
			expectedError: "invalid memory budget",
		},
		{
			name:          "Zero max open files",
			inputFiles:    []string{"file1.log"},
			memoryBudget:  1024 * 1024,
			maxOpenFiles:  0,
			expectedError: "invalid max open files limit",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			merger := New()
			err := merger.Merge(tc.inputFiles, "output.log", tc.memoryBudget, tc.maxOpenFiles)

			if err == nil {
				t.Errorf("Expected error containing '%s', got nil", tc.expectedError)
			} else if !strings.Contains(err.Error(), tc.expectedError) {
				t.Errorf("Expected error containing '%s', got '%s'", tc.expectedError, err.Error())
			}
		})
	}
}

func BenchmarkOptimalMerger(b *testing.B) {
	// Create test files
	tmpDir, err := os.MkdirTemp("", "merger_benchmark")
	if err != nil {
		b.Fatalf("Failed to create temp directory: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	numFiles := 5
	entriesPerFile := 1000
	var files []string

	for i := 0; i < numFiles; i++ {
		filename := filepath.Join(tmpDir, fmt.Sprintf("bench_%d.log", i))
		files = append(files, filename)

		var content strings.Builder
		for j := 0; j < entriesPerFile; j++ {
			timestamp := i*entriesPerFile + j
			fmt.Fprintf(&content, "%d benchmark log entry %d\n", timestamp, j)
		}

		if err := createTestFile(filename, content.String()); err != nil {
			b.Fatalf("Failed to create benchmark file: %v", err)
		}
	}

	outputPath := filepath.Join(tmpDir, "bench_output.log")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		merger := New()
		err := merger.Merge(files, outputPath, 1024*1024, 10)
		if err != nil {
			b.Fatalf("Benchmark failed: %v", err)
		}
	}
}