package message_queue

import (
	"fmt"
	"sync"
	"time"
)

// Topic represents a message topic with its subscribers and messages
type Topic struct {
	messages        []string
	subscribers     []chan string
	retentionLimit int
	mutex          sync.RWMutex
}

// MessageQueue represents the main message queue system
type MessageQueue struct {
	topics map[string]*Topic
	mutex  sync.RWMutex
}

// NewMessageQueue creates a new message queue instance
func NewMessageQueue() *MessageQueue {
	return &MessageQueue{
		topics: make(map[string]*Topic),
	}
}

// getTopic returns an existing topic or creates a new one
func (mq *MessageQueue) getTopic(name string) *Topic {
	mq.mutex.Lock()
	defer mq.mutex.Unlock()

	topic, exists := mq.topics[name]
	if !exists {
		topic = &Topic{
			messages:        make([]string, 0),
			subscribers:     make([]chan string, 0),
			retentionLimit: 1000, // default retention limit
		}
		mq.topics[name] = topic
	}
	return topic
}

// SetTopicRetentionLimit sets the message retention limit for a specific topic
func (mq *MessageQueue) SetTopicRetentionLimit(topicName string, limit int) {
	topic := mq.getTopic(topicName)
	topic.mutex.Lock()
	defer topic.mutex.Unlock()
	topic.retentionLimit = limit
}

// Publish publishes a message to a topic
func (mq *MessageQueue) Publish(topicName, message string) error {
	topic := mq.getTopic(topicName)
	topic.mutex.Lock()
	defer topic.mutex.Unlock()

	// Add message to the topic
	topic.messages = append(topic.messages, message)

	// Remove oldest messages if exceeding retention limit
	if len(topic.messages) > topic.retentionLimit {
		topic.messages = topic.messages[len(topic.messages)-topic.retentionLimit:]
	}

	// Deliver message to all subscribers
	for _, ch := range topic.subscribers {
		select {
		case ch <- message:
			// Message delivered successfully
		default:
			// Skip slow consumers
			go func(c chan string) {
				select {
				case c <- message:
				case <-time.After(time.Second):
					// Message dropped after timeout
				}
			}(ch)
		}
	}

	return nil
}

// Subscribe creates a subscription to a topic
func (mq *MessageQueue) Subscribe(topicName string) (<-chan string, error) {
	topic := mq.getTopic(topicName)
	topic.mutex.Lock()
	defer topic.mutex.Unlock()

	// Create a buffered channel for the subscriber
	ch := make(chan string, 100)

	// Add subscriber to the topic
	topic.subscribers = append(topic.subscribers, ch)

	// Send existing messages within retention limit to the new subscriber
	go func() {
		for _, msg := range topic.messages {
			ch <- msg
		}
	}()

	return ch, nil
}

// Unsubscribe removes a subscription from a topic
func (mq *MessageQueue) Unsubscribe(topicName string, ch <-chan string) error {
	topic := mq.getTopic(topicName)
	topic.mutex.Lock()
	defer topic.mutex.Unlock()

	for i, subscriber := range topic.subscribers {
		if subscriber == ch {
			// Close the channel
			close(subscriber)
			// Remove subscriber from the slice
			topic.subscribers = append(topic.subscribers[:i], topic.subscribers[i+1:]...)
			return nil
		}
	}

	return fmt.Errorf("subscriber not found for topic: %s", topicName)
}

// GetTopicStats returns statistics about a topic
func (mq *MessageQueue) GetTopicStats(topicName string) (int, int, error) {
	topic := mq.getTopic(topicName)
	topic.mutex.RLock()
	defer topic.mutex.RUnlock()

	return len(topic.messages), len(topic.subscribers), nil
}

// Close closes all topics and their subscriptions
func (mq *MessageQueue) Close() {
	mq.mutex.Lock()
	defer mq.mutex.Unlock()

	for _, topic := range mq.topics {
		topic.mutex.Lock()
		for _, subscriber := range topic.subscribers {
			close(subscriber)
		}
		topic.subscribers = nil
		topic.messages = nil
		topic.mutex.Unlock()
	}
	mq.topics = make(map[string]*Topic)
}