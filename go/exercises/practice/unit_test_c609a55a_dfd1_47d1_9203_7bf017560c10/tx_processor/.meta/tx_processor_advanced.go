package tx_processor

import (
	"context"
	"log"
	"os"
	"sync"
	"time"
)

// TransactionProcessorAdvanced extends the basic TransactionProcessor
// with advanced features like transaction logging, circuit breaking,
// and metrics collection.
type TransactionProcessorAdvanced struct {
	*TransactionProcessor
	
	// For transaction logging
	logFile     *os.File
	logChan     chan string
	
	// For circuit breaking
	consecutiveErrors int
	circuitOpen       bool
	circuitLock       sync.RWMutex
	circuitThreshold  int
	resetTimeout      time.Duration
	
	// For metrics
	metrics        map[string]int64
	metricsLock    sync.RWMutex
}

// NewTransactionProcessorAdvanced creates an advanced transaction processor.
func NewTransactionProcessorAdvanced(initialBalances map[string]int64, logPath string) (*TransactionProcessorAdvanced, error) {
	basicProcessor := NewTransactionProcessor(initialBalances)
	
	var logFile *os.File
	var err error
	
	// Setup transaction logging if a log path is provided
	if logPath != "" {
		logFile, err = os.OpenFile(logPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			return nil, err
		}
	}
	
	processor := &TransactionProcessorAdvanced{
		TransactionProcessor: basicProcessor,
		logFile:              logFile,
		logChan:              make(chan string, 1000), // Buffer for 1000 log messages
		circuitThreshold:     50,                     // Open circuit after 50 consecutive errors
		resetTimeout:         30 * time.Second,       // Reset circuit after 30 seconds
		metrics:              make(map[string]int64),
	}
	
	// Start background workers if we're logging
	if logFile != nil {
		go processor.logWorker()
	}
	
	return processor, nil
}

// logWorker asynchronously writes transaction logs to disk
func (tp *TransactionProcessorAdvanced) logWorker() {
	for logMsg := range tp.logChan {
		if tp.logFile != nil {
			_, err := tp.logFile.WriteString(logMsg + "\n")
			if err != nil {
				log.Printf("Error writing to transaction log: %v", err)
			}
		}
	}
}

// SubmitTransaction extends the basic implementation with advanced features
func (tp *TransactionProcessorAdvanced) SubmitTransaction(tx Transaction) error {
	// Check if circuit breaker is open
	tp.circuitLock.RLock()
	circuitOpen := tp.circuitOpen
	tp.circuitLock.RUnlock()
	
	if circuitOpen {
		tp.incrementMetric("circuit_breaks")
		return &txError{"circuit breaker open, transaction rejected"}
	}
	
	// Track transaction start time for metrics
	startTime := time.Now()
	
	// Process transaction using base implementation
	err := tp.TransactionProcessor.SubmitTransaction(tx)
	
	// Update metrics
	tp.metricsLock.Lock()
	tp.metrics["total_transactions"]++
	if err != nil {
		tp.metrics["failed_transactions"]++
		
		// Update circuit breaker
		tp.consecutiveErrors++
		if tp.consecutiveErrors >= tp.circuitThreshold {
			tp.circuitLock.Lock()
			tp.circuitOpen = true
			tp.circuitLock.Unlock()
			
			// Start timer to reset circuit
			go func() {
				time.Sleep(tp.resetTimeout)
				tp.circuitLock.Lock()
				tp.circuitOpen = false
				tp.consecutiveErrors = 0
				tp.circuitLock.Unlock()
			}()
		}
	} else {
		tp.consecutiveErrors = 0
		tp.metrics["successful_transactions"]++
	}
	
	// Record processing time
	processingTime := time.Since(startTime).Milliseconds()
	tp.metrics["total_processing_time_ms"] += processingTime
	if tp.metrics["total_transactions"] > 0 {
		tp.metrics["avg_processing_time_ms"] = tp.metrics["total_processing_time_ms"] / tp.metrics["total_transactions"]
	}
	tp.metricsLock.Unlock()
	
	// Log transaction asynchronously if logging is enabled
	if tp.logFile != nil {
		logMsg := time.Now().Format(time.RFC3339) + " | " +
			"AccountID: " + tx.AccountID + " | " +
			"TxID: " + tx.TransactionID + " | " +
			"Amount: " + string(rune(tx.Amount))
		
		if err != nil {
			logMsg += " | Error: " + err.Error()
		} else {
			logMsg += " | Success"
		}
		
		// Try to send to log channel without blocking
		select {
		case tp.logChan <- logMsg:
			// Message sent
		default:
			// Channel buffer full, log that we're dropping messages
			log.Println("Log channel full, dropping transaction log message")
		}
	}
	
	return err
}

// GetMetrics returns the current metrics
func (tp *TransactionProcessorAdvanced) GetMetrics() map[string]int64 {
	tp.metricsLock.RLock()
	defer tp.metricsLock.RUnlock()
	
	// Create a copy to avoid race conditions
	metricsCopy := make(map[string]int64, len(tp.metrics))
	for k, v := range tp.metrics {
		metricsCopy[k] = v
	}
	
	return metricsCopy
}

// ResetCircuitBreaker manually resets the circuit breaker
func (tp *TransactionProcessorAdvanced) ResetCircuitBreaker() {
	tp.circuitLock.Lock()
	tp.circuitOpen = false
	tp.consecutiveErrors = 0
	tp.circuitLock.Unlock()
}

// Shutdown gracefully shuts down the processor
func (tp *TransactionProcessorAdvanced) Shutdown(ctx context.Context) error {
	// Wait for context to be done or timeout
	<-ctx.Done()
	
	// Close log channel and file
	if tp.logChan != nil {
		close(tp.logChan)
	}
	
	if tp.logFile != nil {
		return tp.logFile.Close()
	}
	
	return nil
}

// incrementMetric safely increments a metric value
func (tp *TransactionProcessorAdvanced) incrementMetric(name string) {
	tp.metricsLock.Lock()
	tp.metrics[name]++
	tp.metricsLock.Unlock()
}