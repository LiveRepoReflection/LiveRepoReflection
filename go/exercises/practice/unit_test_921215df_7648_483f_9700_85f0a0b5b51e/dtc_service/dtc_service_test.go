package dtc_service

import (
	"bytes"
	"encoding/json"
	"io"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"sync"
	"testing"
	"time"
)

// transactionResponse represents the JSON response from GET /transactions/{id}.
type transactionResponse struct {
	Status string `json:"status"`
}

// participantServer simulates an external participant.
// behavior: "success" means prepare always returns 200 OK, "fail" means prepare returns 409 Conflict.
func newParticipantServer(behavior string) *httptest.Server {
	mux := http.NewServeMux()
	mux.HandleFunc("/prepare", func(w http.ResponseWriter, r *http.Request) {
		if behavior == "fail" {
			w.WriteHeader(http.StatusConflict)
			return
		}
		w.WriteHeader(http.StatusOK)
	})
	// commit endpoint: always return 200.
	mux.HandleFunc("/commit", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})
	// rollback endpoint: always return 200.
	mux.HandleFunc("/rollback", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})
	return httptest.NewServer(mux)
}

// waitForTransactionStatus polls the DTC API until the transaction reaches the expectedStatus or times out.
func waitForTransactionStatus(t *testing.T, serverURL, transactionID, expectedStatus string) {
	maxWait := 5 * time.Second
	interval := 100 * time.Millisecond
	deadline := time.Now().Add(maxWait)

	for time.Now().Before(deadline) {
		resp, err := http.Get(serverURL + "/transactions/" + transactionID)
		if err != nil {
			t.Fatalf("error sending GET request: %v", err)
		}
		body, err := ioutil.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			t.Fatalf("error reading response body: %v", err)
		}
		var tr transactionResponse
		if err := json.Unmarshal(body, &tr); err != nil {
			t.Fatalf("error unmarshaling JSON: %v", err)
		}
		if strings.ToLower(tr.Status) == strings.ToLower(expectedStatus) {
			return
		}
		time.Sleep(interval)
	}
	t.Fatalf("transaction did not reach expected status '%s' within %v", expectedStatus, maxWait)
}

// mockDTCHandler simulates a minimal DTC HTTP API for testing purposes.
// This is a stub implementation intended for the unit test; in a real scenario,
// this would be replaced by the full distributed transaction coordinator implementation.
func mockDTCHandler() http.Handler {
	// Use in-memory storage for transactions.
	var mu sync.Mutex
	transactions := make(map[string]string)
	transactionCount := 0

	mux := http.NewServeMux()

	// POST /transactions: start a new transaction with participant prepare URLs in JSON array.
	mux.HandleFunc("/transactions", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}
		body, err := io.ReadAll(r.Body)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		var participants []string
		if err := json.Unmarshal(body, &participants); err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		// Simulate calling prepare for each participant concurrently.
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
					resp.Body.Close()
				}
			}(url)
		}
		wg.Wait()

		// Create a new transaction record.
		mu.Lock()
		transactionCount++
		txnID := strconv.Itoa(transactionCount)
		if prepareSuccess {
			transactions[txnID] = "pending"
		} else {
			transactions[txnID] = "pending"
		}
		mu.Unlock()

		// Asynchronously commit or rollback.
		go func(id string, success bool) {
			// simulate processing delay
			time.Sleep(200 * time.Millisecond)
			if success {
				// Call commit on all participants.
				for _, url := range participants {
					commitURL := strings.Replace(url, "/prepare", "/commit", 1)
					client := &http.Client{Timeout: 1 * time.Second}
					resp, err := client.Post(commitURL, "application/json", nil)
					if err == nil && resp != nil {
						resp.Body.Close()
					}
				}
				mu.Lock()
				transactions[id] = "committed"
				mu.Unlock()
			} else {
				// Call rollback on all participants.
				for _, url := range participants {
					rollbackURL := strings.Replace(url, "/prepare", "/rollback", 1)
					client := &http.Client{Timeout: 1 * time.Second}
					resp, err := client.Post(rollbackURL, "application/json", nil)
					if err == nil && resp != nil {
						resp.Body.Close()
					}
				}
				mu.Lock()
				transactions[id] = "rolledback"
				mu.Unlock()
			}
		}(txnID, prepareSuccess)

		w.Header().Set("Location", r.Host+"/transactions/"+txnID)
		w.WriteHeader(http.StatusCreated)
	})

	// GET /transactions/{id}: return transaction status.
	mux.HandleFunc("/transactions/", func(w http.ResponseWriter, r *http.Request) {
		parts := strings.Split(r.URL.Path, "/")
		if len(parts) < 3 {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		id := parts[2]
		mu.Lock()
		status, exists := transactions[id]
		mu.Unlock()
		if !exists {
			w.WriteHeader(http.StatusNotFound)
			return
		}
		respJSON, _ := json.Marshal(transactionResponse{Status: status})
		w.Header().Set("Content-Type", "application/json")
		w.Write(respJSON)
	})
	return mux
}

func TestSuccessfulTransaction(t *testing.T) {
	// Start two participant servers that always succeed.
	participant1 := newParticipantServer("success")
	defer participant1.Close()
	participant2 := newParticipantServer("success")
	defer participant2.Close()

	// Prepare participant URLs (pointing to /prepare endpoint).
	participants := []string{
		participant1.URL + "/prepare",
		participant2.URL + "/prepare",
	}

	// Start the mock DTC server.
	dtcServer := httptest.NewServer(mockDTCHandler())
	defer dtcServer.Close()

	// Create transaction by POSTing participant URLs.
	reqBody, err := json.Marshal(participants)
	if err != nil {
		t.Fatalf("error marshaling participant URLs: %v", err)
	}
	resp, err := http.Post(dtcServer.URL+"/transactions", "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		t.Fatalf("error sending POST /transactions: %v", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusCreated {
		t.Fatalf("expected status 201 Created, got %d", resp.StatusCode)
	}
	location := resp.Header.Get("Location")
	if location == "" {
		t.Fatal("missing Location header in response")
	}
	// Extract transaction ID from Location header.
	parts := strings.Split(location, "/")
	transactionID := parts[len(parts)-1]
	// Wait for the transaction to be committed.
	waitForTransactionStatus(t, dtcServer.URL, transactionID, "committed")
}

func TestRolledBackTransaction(t *testing.T) {
	// Start one participant server that fails, and one that succeeds.
	participantFail := newParticipantServer("fail")
	defer participantFail.Close()
	participantSuccess := newParticipantServer("success")
	defer participantSuccess.Close()

	participants := []string{
		participantFail.URL + "/prepare",
		participantSuccess.URL + "/prepare",
	}

	// Start the mock DTC server.
	dtcServer := httptest.NewServer(mockDTCHandler())
	defer dtcServer.Close()

	// Create transaction by POSTing participant URLs.
	reqBody, err := json.Marshal(participants)
	if err != nil {
		t.Fatalf("error marshaling participant URLs: %v", err)
	}
	resp, err := http.Post(dtcServer.URL+"/transactions", "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		t.Fatalf("error sending POST /transactions: %v", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusCreated {
		t.Fatalf("expected status 201 Created, got %d", resp.StatusCode)
	}
	location := resp.Header.Get("Location")
	if location == "" {
		t.Fatal("missing Location header in response")
	}
	parts := strings.Split(location, "/")
	transactionID := parts[len(parts)-1]
	// Wait for the transaction to be rolled back.
	waitForTransactionStatus(t, dtcServer.URL, transactionID, "rolledback")
}