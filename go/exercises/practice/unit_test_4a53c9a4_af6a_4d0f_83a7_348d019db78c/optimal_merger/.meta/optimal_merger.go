package optimalmerger

import (
	"bufio"
	"container/heap"
	"errors"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
)

type LogEntry struct {
	timestamp int64
	content   string
	fileIndex int
}

type LogHeap struct {
	entries []*LogEntry
}

func (h LogHeap) Len() int { return len(h.entries) }

func (h LogHeap) Less(i, j int) bool {
	if h.entries[i].timestamp == h.entries[j].timestamp {
		return h.entries[i].fileIndex < h.entries[j].fileIndex
	}
	return h.entries[i].timestamp < h.entries[j].timestamp
}

func (h LogHeap) Swap(i, j int) {
	h.entries[i], h.entries[j] = h.entries[j], h.entries[i]
}

func (h *LogHeap) Push(x interface{}) {
	h.entries = append(h.entries, x.(*LogEntry))
}

func (h *LogHeap) Pop() interface{} {
	old := h.entries
	n := len(old)
	x := old[n-1]
	h.entries = old[0 : n-1]
	return x
}

type Merger struct {
	bufferSize int
}

func New() *Merger {
	return &Merger{
		bufferSize: 4096, // Default buffer size
	}
}

func (m *Merger) parseLogEntry(line string, fileIndex int) (*LogEntry, error) {
	parts := strings.SplitN(line, " ", 2)
	if len(parts) < 2 {
		return nil, fmt.Errorf("invalid log entry format: %s", line)
	}

	timestamp, err := strconv.ParseInt(parts[0], 10, 64)
	if err != nil {
		return nil, fmt.Errorf("invalid timestamp: %s", parts[0])
	}

	return &LogEntry{
		timestamp: timestamp,
		content:   line,
		fileIndex: fileIndex,
	}, nil
}

func (m *Merger) Merge(inputFiles []string, outputPath string, memoryBudget int64, maxOpenFiles int) error {
	if len(inputFiles) == 0 {
		return errors.New("no input files provided")
	}
	if memoryBudget <= 0 {
		return errors.New("invalid memory budget")
	}
	if maxOpenFiles <= 0 {
		return errors.New("invalid max open files limit")
	}

	// Create output file
	outFile, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("failed to create output file: %v", err)
	}
	defer outFile.Close()

	writer := bufio.NewWriter(outFile)
	defer writer.Flush()

	// Initialize min-heap for merging
	logHeap := &LogHeap{}
	heap.Init(logHeap)

	// Calculate buffer size based on memory budget and number of files
	bufferSizePerFile := memoryBudget / int64(len(inputFiles))
	if bufferSizePerFile < 4096 {
		bufferSizePerFile = 4096 // Minimum buffer size
	}

	// Process files in batches to respect maxOpenFiles
	for i := 0; i < len(inputFiles); i += maxOpenFiles {
		end := i + maxOpenFiles
		if end > len(inputFiles) {
			end = len(inputFiles)
		}

		// Open current batch of files
		readers := make([]*bufio.Reader, end-i)
		files := make([]*os.File, end-i)
		for j := i; j < end; j++ {
			file, err := os.Open(inputFiles[j])
			if err != nil {
				// Clean up already opened files
				for k := 0; k < j-i; k++ {
					files[k].Close()
				}
				return fmt.Errorf("failed to open input file %s: %v", inputFiles[j], err)
			}
			files[j-i] = file
			readers[j-i] = bufio.NewReaderSize(file, int(bufferSizePerFile))
		}

		// Read first entry from each file
		for j := 0; j < len(readers); j++ {
			line, err := readers[j].ReadString('\n')
			if err != nil && err != io.EOF {
				// Clean up
				for _, f := range files {
					f.Close()
				}
				return fmt.Errorf("failed to read from file: %v", err)
			}
			if err == io.EOF && line == "" {
				continue
			}
			line = strings.TrimSpace(line)
			entry, err := m.parseLogEntry(line, i+j)
			if err != nil {
				// Clean up
				for _, f := range files {
					f.Close()
				}
				return fmt.Errorf("failed to parse log entry: %v", err)
			}
			heap.Push(logHeap, entry)
		}

		// Process entries
		for logHeap.Len() > 0 {
			entry := heap.Pop(logHeap).(*LogEntry)
			fileIndex := entry.fileIndex - i
			if fileIndex >= len(readers) {
				continue
			}

			// Write current entry
			if _, err := writer.WriteString(entry.content + "\n"); err != nil {
				// Clean up
				for _, f := range files {
					f.Close()
				}
				return fmt.Errorf("failed to write to output file: %v", err)
			}

			// Read next entry from the same file
			line, err := readers[fileIndex].ReadString('\n')
			if err != nil && err != io.EOF {
				// Clean up
				for _, f := range files {
					f.Close()
				}
				return fmt.Errorf("failed to read from file: %v", err)
			}
			if err == io.EOF && line == "" {
				continue
			}
			line = strings.TrimSpace(line)
			nextEntry, err := m.parseLogEntry(line, entry.fileIndex)
			if err != nil {
				// Clean up
				for _, f := range files {
					f.Close()
				}
				return fmt.Errorf("failed to parse log entry: %v", err)
			}
			heap.Push(logHeap, nextEntry)
		}

		// Close current batch of files
		for _, f := range files {
			f.Close()
		}
	}

	return nil
}