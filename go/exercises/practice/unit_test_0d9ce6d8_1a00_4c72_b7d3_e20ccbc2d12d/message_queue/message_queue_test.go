package message_queue

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestBasicPublishSubscribe(t *testing.T) {
	mq := NewMessageQueue()
	topic := "test-topic"
	message := "hello world"

	// Test publishing
	err := mq.Publish(topic, message)
	if err != nil {
		t.Errorf("Failed to publish message: %v", err)
	}

	// Test subscribing
	ch, err := mq.Subscribe(topic)
	if err != nil {
		t.Errorf("Failed to subscribe to topic: %v", err)
	}

	// Test receiving message
	select {
	case msg := <-ch:
		if msg != message {
			t.Errorf("Expected message %s, got %s", message, msg)
		}
	case <-time.After(time.Second):
		t.Error("Timeout waiting for message")
	}
}

func TestMultipleSubscribers(t *testing.T) {
	mq := NewMessageQueue()
	topic := "test-topic"
	message := "broadcast message"
	subscriberCount := 5

	// Create multiple subscribers
	channels := make([]<-chan string, subscriberCount)
	for i := 0; i < subscriberCount; i++ {
		ch, err := mq.Subscribe(topic)
		if err != nil {
			t.Fatalf("Failed to create subscriber %d: %v", i, err)
		}
		channels[i] = ch
	}

	// Publish message
	err := mq.Publish(topic, message)
	if err != nil {
		t.Fatalf("Failed to publish message: %v", err)
	}

	// Verify all subscribers receive the message
	for i, ch := range channels {
		select {
		case received := <-ch:
			if received != message {
				t.Errorf("Subscriber %d: expected message %s, got %s", i, message, received)
			}
		case <-time.After(time.Second):
			t.Errorf("Subscriber %d: timeout waiting for message", i)
		}
	}
}

func TestMessageRetention(t *testing.T) {
	mq := NewMessageQueue()
	topic := "retention-test"
	retentionLimit := 3

	// Set retention limit
	mq.SetTopicRetentionLimit(topic, retentionLimit)

	// Publish more messages than the retention limit
	for i := 0; i < retentionLimit+2; i++ {
		msg := fmt.Sprintf("message-%d", i)
		err := mq.Publish(topic, msg)
		if err != nil {
			t.Fatalf("Failed to publish message %d: %v", i, err)
		}
	}

	// Subscribe and verify we only get the last 'retentionLimit' messages
	ch, err := mq.Subscribe(topic)
	if err != nil {
		t.Fatalf("Failed to subscribe: %v", err)
	}

	received := 0
	for i := 0; i < retentionLimit; i++ {
		select {
		case msg := <-ch:
			expected := fmt.Sprintf("message-%d", i+2)
			if msg != expected {
				t.Errorf("Expected message %s, got %s", expected, msg)
			}
			received++
		case <-time.After(time.Second):
			t.Error("Timeout waiting for message")
		}
	}

	if received != retentionLimit {
		t.Errorf("Expected to receive %d messages, got %d", retentionLimit, received)
	}
}

func TestConcurrentPublishing(t *testing.T) {
	mq := NewMessageQueue()
	topic := "concurrent-test"
	publishCount := 100
	publisherCount := 10

	var wg sync.WaitGroup
	wg.Add(publisherCount)

	// Create multiple publishers
	for p := 0; p < publisherCount; p++ {
		go func(publisher int) {
			defer wg.Done()
			for i := 0; i < publishCount; i++ {
				msg := fmt.Sprintf("publisher-%d-message-%d", publisher, i)
				err := mq.Publish(topic, msg)
				if err != nil {
					t.Errorf("Publisher %d failed to publish message %d: %v", publisher, i, err)
				}
			}
		}(p)
	}

	// Subscribe and count messages
	ch, err := mq.Subscribe(topic)
	if err != nil {
		t.Fatalf("Failed to subscribe: %v", err)
	}

	received := make(map[string]bool)
	done := make(chan bool)

	go func() {
		for msg := range ch {
			received[msg] = true
		}
		done <- true
	}()

	wg.Wait()
	time.Sleep(time.Second) // Allow time for messages to be processed

	expectedTotal := publishCount * publisherCount
	if len(received) != expectedTotal {
		t.Errorf("Expected %d unique messages, got %d", expectedTotal, len(received))
	}
}

func TestMultipleTopics(t *testing.T) {
	mq := NewMessageQueue()
	topics := []string{"topic1", "topic2", "topic3"}
	messages := make(map[string][]string)

	// Subscribe to all topics
	channels := make(map[string]<-chan string)
	for _, topic := range topics {
		messages[topic] = []string{
			fmt.Sprintf("%s-message-1", topic),
			fmt.Sprintf("%s-message-2", topic),
		}
		ch, err := mq.Subscribe(topic)
		if err != nil {
			t.Fatalf("Failed to subscribe to topic %s: %v", topic, err)
		}
		channels[topic] = ch
	}

	// Publish messages to each topic
	for topic, msgs := range messages {
		for _, msg := range msgs {
			err := mq.Publish(topic, msg)
			if err != nil {
				t.Fatalf("Failed to publish message %s to topic %s: %v", msg, topic, err)
			}
		}
	}

	// Verify messages are received correctly for each topic
	for topic, ch := range channels {
		expectedMsgs := messages[topic]
		for _, expected := range expectedMsgs {
			select {
			case received := <-ch:
				if received != expected {
					t.Errorf("Topic %s: expected message %s, got %s", topic, expected, received)
				}
			case <-time.After(time.Second):
				t.Errorf("Topic %s: timeout waiting for message %s", topic, expected)
			}
		}
	}
}

func BenchmarkPublishSubscribe(b *testing.B) {
	mq := NewMessageQueue()
	topic := "bench-topic"
	message := "benchmark message"

	ch, err := mq.Subscribe(topic)
	if err != nil {
		b.Fatalf("Failed to subscribe: %v", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		err := mq.Publish(topic, message)
		if err != nil {
			b.Fatalf("Failed to publish: %v", err)
		}
		<-ch
	}
}