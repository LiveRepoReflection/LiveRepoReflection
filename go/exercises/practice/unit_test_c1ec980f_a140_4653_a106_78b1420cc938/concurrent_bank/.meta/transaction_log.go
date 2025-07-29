package concurrent_bank

import (
	"encoding/json"
	"os"
	"time"
)

func (t TransactionLog) MarshalJSON() ([]byte, error) {
	type Alias TransactionLog
	return json.Marshal(&struct {
		Timestamp string `json:"timestamp"`
		*Alias
	}{
		Timestamp: t.Timestamp.Format(time.RFC3339Nano),
		Alias:    (*Alias)(&t),
	})
}

func (t *TransactionLog) UnmarshalJSON(data []byte) error {
	type Alias TransactionLog
	aux := &struct {
		Timestamp string `json:"timestamp"`
		*Alias
	}{
		Alias: (*Alias)(t),
	}
	if err := json.Unmarshal(data, &aux); err != nil {
		return err
	}

	parsedTime, err := time.Parse(time.RFC3339Nano, aux.Timestamp)
	if err != nil {
		return err
	}
	t.Timestamp = parsedTime
	return nil
}

func (b *Bank) SaveTransactionLog(filename string) error {
	b.logMu.Lock()
	defer b.logMu.Unlock()

	data, err := json.Marshal(b.logs)
	if err != nil {
		return err
	}

	return os.WriteFile(filename, data, 0644)
}

func (b *Bank) LoadTransactionLog(filename string) error {
	b.logMu.Lock()
	defer b.logMu.Unlock()

	data, err := os.ReadFile(filename)
	if err != nil {
		return err
	}

	var logs []TransactionLog
	if err := json.Unmarshal(data, &logs); err != nil {
		return err
	}

	b.logs = logs
	return nil
}