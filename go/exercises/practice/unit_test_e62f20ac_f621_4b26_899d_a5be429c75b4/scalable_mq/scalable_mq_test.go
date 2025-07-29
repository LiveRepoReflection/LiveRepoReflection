package scalable_mq

import (
	"os"
	"path/filepath"
	"testing"
	"time"
)

// Assuming these types and functions are defined in the project:
//
// type Config struct {
//     Directory      string
//     AckTimeout     time.Duration
//     ConsumerGroups []string
// }
// 
// type Message struct {
//     ID      string
//     Payload string
// }
//
// type MQ struct { /* internal state */ }
//
// func NewMQ(config Config) (*MQ, error)
// func (mq *MQ) Enqueue(msg Message) error
// func (mq *MQ) Dequeue(group string) (Message, error)
// func (mq *MQ) Ack(group, messageID string) error
// func (mq *MQ) Shutdown() error

func setupTestDirectory(dir string, t *testing.T) {
	err := os.MkdirAll(dir, 0755)
	if err != nil {
		t.Fatalf("Failed to create test directory: %v", err)
	}
}

func cleanupTestDirectory(dir string, t *testing.T) {
	err := os.RemoveAll(dir)
	if err != nil {
		t.Fatalf("Failed to remove test directory: %v", err)
	}
}

func TestOrdering(t *testing.T) {
	testDir := filepath.Join(os.TempDir(), "scalable_mq_ordering")
	setupTestDirectory(testDir, t)
	defer cleanupTestDirectory(testDir, t)

	config := Config{
		Directory:      testDir,
		AckTimeout:     2 * time.Second,
		ConsumerGroups: []string{"group1"},
	}
	mq, err := NewMQ(config)
	if err != nil {
		t.Fatalf("Failed to initialize MQ: %v", err)
	}
	defer mq.Shutdown()

	messages := []Message{
		{ID: "1", Payload: "first"},
		{ID: "2", Payload: "second"},
		{ID: "3", Payload: "third"},
	}

	for _, msg := range messages {
		err := mq.Enqueue(msg)
		if err != nil {
			t.Fatalf("Failed to enqueue message %s: %v", msg.ID, err)
		}
	}

	// Verify that messages are dequeued in FIFO order for the consumer group.
	for i, expected := range messages {
		received, err := mq.Dequeue("group1")
		if err != nil {
			t.Fatalf("Failed to dequeue message at index %d: %v", i, err)
		}
		if received.ID != expected.ID {
			t.Fatalf("Expected message ID %s, got %s", expected.ID, received.ID)
		}
		err = mq.Ack("group1", received.ID)
		if err != nil {
			t.Fatalf("Failed to acknowledge message %s: %v", received.ID, err)
		}
	}
}

func TestAtLeastOnceDelivery(t *testing.T) {
	testDir := filepath.Join(os.TempDir(), "scalable_mq_atleastonce")
	setupTestDirectory(testDir, t)
	defer cleanupTestDirectory(testDir, t)

	config := Config{
		Directory:      testDir,
		AckTimeout:     1 * time.Second,
		ConsumerGroups: []string{"group1"},
	}
	mq, err := NewMQ(config)
	if err != nil {
		t.Fatalf("Failed to initialize MQ: %v", err)
	}
	defer mq.Shutdown()

	msg := Message{ID: "redeliveryTest", Payload: "test message for redelivery"}
	err = mq.Enqueue(msg)
	if err != nil {
		t.Fatalf("Failed to enqueue message: %v", err)
	}

	// Dequeue and do not acknowledge to trigger redelivery.
	received, err := mq.Dequeue("group1")
	if err != nil {
		t.Fatalf("Failed to dequeue message: %v", err)
	}
	if received.ID != msg.ID {
		t.Fatalf("Expected message ID %s, got %s", msg.ID, received.ID)
	}

	// Wait for the ack timeout to expire, plus a margin.
	time.Sleep(1500 * time.Millisecond)

	// The message should be redelivered.
	redelivered, err := mq.Dequeue("group1")
	if err != nil {
		t.Fatalf("Failed to dequeue redelivered message: %v", err)
	}
	if redelivered.ID != msg.ID {
		t.Fatalf("Expected redelivered message ID %s, got %s", msg.ID, redelivered.ID)
	}
	err = mq.Ack("group1", redelivered.ID)
	if err != nil {
		t.Fatalf("Failed to acknowledge redelivered message: %v", err)
	}
}

func TestMultipleConsumerGroups(t *testing.T) {
	testDir := filepath.Join(os.TempDir(), "scalable_mq_multigroup")
	setupTestDirectory(testDir, t)
	defer cleanupTestDirectory(testDir, t)

	config := Config{
		Directory:      testDir,
		AckTimeout:     2 * time.Second,
		ConsumerGroups: []string{"group1", "group2"},
	}
	mq, err := NewMQ(config)
	if err != nil {
		t.Fatalf("Failed to initialize MQ: %v", err)
	}
	defer mq.Shutdown()

	msg := Message{ID: "multiGroup", Payload: "message for multiple groups"}
	err = mq.Enqueue(msg)
	if err != nil {
		t.Fatalf("Failed to enqueue message: %v", err)
	}

	// Each consumer group should receive its own copy of the message.
	receivedGroup1, err := mq.Dequeue("group1")
	if err != nil {
		t.Fatalf("Group1 failed to dequeue message: %v", err)
	}
	receivedGroup2, err := mq.Dequeue("group2")
	if err != nil {
		t.Fatalf("Group2 failed to dequeue message: %v", err)
	}

	if receivedGroup1.ID != msg.ID {
		t.Fatalf("Group1 expected message ID %s, got %s", msg.ID, receivedGroup1.ID)
	}
	if receivedGroup2.ID != msg.ID {
		t.Fatalf("Group2 expected message ID %s, got %s", msg.ID, receivedGroup2.ID)
	}

	err = mq.Ack("group1", receivedGroup1.ID)
	if err != nil {
		t.Fatalf("Group1 failed to acknowledge message: %v", err)
	}
	err = mq.Ack("group2", receivedGroup2.ID)
	if err != nil {
		t.Fatalf("Group2 failed to acknowledge message: %v", err)
	}
}

func TestPersistenceRecovery(t *testing.T) {
	testDir := filepath.Join(os.TempDir(), "scalable_mq_persistence")
	setupTestDirectory(testDir, t)
	defer cleanupTestDirectory(testDir, t)

	config := Config{
		Directory:      testDir,
		AckTimeout:     2 * time.Second,
		ConsumerGroups: []string{"group1"},
	}
	
	// Initialize queue and enqueue messages.
	mq, err := NewMQ(config)
	if err != nil {
		t.Fatalf("Failed to initialize MQ: %v", err)
	}

	messages := []Message{
		{ID: "persist1", Payload: "data1"},
		{ID: "persist2", Payload: "data2"},
	}
	for _, msg := range messages {
		err = mq.Enqueue(msg)
		if err != nil {
			t.Fatalf("Failed to enqueue message %s: %v", msg.ID, err)
		}
	}

	// Shutdown the queue to simulate a crash or restart.
	err = mq.Shutdown()
	if err != nil {
		t.Fatalf("Failed to shutdown MQ: %v", err)
	}

	// Reinitialize the queue from the persisted state.
	mqRecovered, err := NewMQ(config)
	if err != nil {
		t.Fatalf("Failed to recover MQ: %v", err)
	}
	defer mqRecovered.Shutdown()

	// Dequeue and acknowledge all persisted messages.
	for _, expected := range messages {
		received, err := mqRecovered.Dequeue("group1")
		if err != nil {
			t.Fatalf("Failed to dequeue message after recovery: %v", err)
		}
		if received.ID != expected.ID {
			t.Fatalf("After recovery, expected message ID %s, got %s", expected.ID, received.ID)
		}
		err = mqRecovered.Ack("group1", received.ID)
		if err != nil {
			t.Fatalf("Failed to acknowledge message %s after recovery: %v", received.ID, err)
		}
	}
}