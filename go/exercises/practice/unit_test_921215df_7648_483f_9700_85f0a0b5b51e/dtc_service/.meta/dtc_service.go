package dtc_service

import (
	"encoding/json"
	"io"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

type Transaction struct {
	ID           string   `json:"id"`
	Participants []string `json:"participants"`
	Status       string   `json:"status"`
}

var (
	txMu             sync.Mutex
	transactions     = map[string]*Transaction{}
	transactionCount int
)

// NewHandler returns an HTTP handler that implements the Distributed Transaction Coordinator (DTC) service.
func NewHandler() http.Handler {
	mux := http.NewServeMux()

	// Handle POST /transactions to create a new transaction.
	mux.HandleFunc("/transactions", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
			return
		}
		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "Bad Request: unable to read body", http.StatusBadRequest)
			return
		}
		var participants []string
		err = json.Unmarshal(body, &participants)
		if err != nil {
			http.Error(w, "Bad Request: invalid JSON", http.StatusBadRequest)
			return
		}

		// Execute the prepare phase concurrently on all participant prepare URLs.
		prepareSuccess := true
		var wg sync.WaitGroup
		var prepareMu sync.Mutex

		for _, url := range participants {
			wg.Add(1)
			go func(participantURL string) {
				defer wg.Done()
				client := &http.Client{Timeout: 1 * time.Second}
				resp, err := client.Post(participantURL, "application/json", nil)
				if err != nil || resp.StatusCode != http.StatusOK {
					prepareMu.Lock()
					prepareSuccess = false
					prepareMu.Unlock()
				}
				if resp != nil {
					io.Copy(io.Discard, resp.Body)
					resp.Body.Close()
				}
			}(url)
		}
		wg.Wait()

		// Create a new transaction.
		txMu.Lock()
		transactionCount++
		txnID := strconv.Itoa(transactionCount)
		tx := &Transaction{
			ID:           txnID,
			Participants: participants,
			Status:       "pending",
		}
		transactions[txnID] = tx
		txMu.Unlock()

		// Asynchronously execute the commit or rollback phase.
		go func(t *Transaction, commit bool) {
			time.Sleep(200 * time.Millisecond)
			client := &http.Client{Timeout: 1 * time.Second}
			if commit {
				// Commit: call commit on each participant by replacing /prepare with /commit.
				for _, p := range t.Participants {
					commitURL := strings.Replace(p, "/prepare", "/commit", 1)
					resp, err := client.Post(commitURL, "application/json", nil)
					if err == nil && resp != nil {
						io.Copy(io.Discard, resp.Body)
						resp.Body.Close()
					}
				}
				txMu.Lock()
				t.Status = "committed"
				txMu.Unlock()
			} else {
				// Rollback: call rollback on each participant by replacing /prepare with /rollback.
				for _, p := range t.Participants {
					rollbackURL := strings.Replace(p, "/prepare", "/rollback", 1)
					resp, err := client.Post(rollbackURL, "application/json", nil)
					if err == nil && resp != nil {
						io.Copy(io.Discard, resp.Body)
						resp.Body.Close()
					}
				}
				txMu.Lock()
				t.Status = "rolledback"
				txMu.Unlock()
			}
		}(tx, prepareSuccess)

		host := r.Host
		if host == "" {
			host = "localhost"
		}
		location := "http://" + host + "/transactions/" + txnID
		w.Header().Set("Location", location)
		w.WriteHeader(http.StatusCreated)
	})

	// Handle GET /transactions/{transactionId} to retrieve the status of a transaction.
	mux.HandleFunc("/transactions/", func(w http.ResponseWriter, r *http.Request) {
		parts := strings.Split(r.URL.Path, "/")
		if len(parts) < 3 {
			http.Error(w, "Bad Request", http.StatusBadRequest)
			return
		}
		id := parts[2]
		txMu.Lock()
		tx, exists := transactions[id]
		txMu.Unlock()
		if !exists {
			http.NotFound(w, r)
			return
		}
		respBody, err := json.Marshal(map[string]string{"status": tx.Status})
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		w.Write(respBody)
	})

	return mux
}