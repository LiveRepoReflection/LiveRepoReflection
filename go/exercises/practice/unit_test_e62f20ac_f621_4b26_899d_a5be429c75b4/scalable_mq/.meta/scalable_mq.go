package scalable_mq

import (
	"bufio"
	"errors"
	"fmt"
	"os"
	"strings"
	"sync"
	"time"
)

type Config struct {
	Directory      string
	AckTimeout     time.Duration
	ConsumerGroups []string
}

type Message struct {
	ID      string
	Payload string
}

type consumerState struct {
	currentIndex     int
	inFlight         bool
	lastDeliveryTime time.Time
}

type MQ struct {
	config    Config
	messages  []Message
	file      *os.File
	consumers map[string]*consumerState
	mutex     sync.Mutex
}

func NewMQ(config Config) (*MQ, error) {
	err := os.MkdirAll(config.Directory, 0755)
	if err != nil {
		return nil, err
	}
	filePath := config.Directory + string(os.PathSeparator) + "messages.log"
	file, err := os.OpenFile(filePath, os.O_RDWR|os.O_CREATE|os.O_APPEND, 0644)
	if err != nil {
		return nil, err
	}
	mq := &MQ{
		config:    config,
		file:      file,
		consumers: make(map[string]*consumerState),
	}
	for _, group := range config.ConsumerGroups {
		mq.consumers[group] = &consumerState{
			currentIndex:     0,
			inFlight:         false,
			lastDeliveryTime: time.Time{},
		}
	}
	err = mq.loadMessages(filePath)
	if err != nil {
		return nil, err
	}
	return mq, nil
}

func (mq *MQ) loadMessages(filePath string) error {
	f, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer f.Close()
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.SplitN(line, "\t", 2)
		if len(parts) != 2 {
			continue
		}
		msg := Message{
			ID:      parts[0],
			Payload: parts[1],
		}
		mq.messages = append(mq.messages, msg)
	}
	return scanner.Err()
}

func (mq *MQ) Enqueue(msg Message) error {
	mq.mutex.Lock()
	defer mq.mutex.Unlock()
	line := fmt.Sprintf("%s\t%s\n", msg.ID, msg.Payload)
	_, err := mq.file.WriteString(line)
	if err != nil {
		return err
	}
	mq.messages = append(mq.messages, msg)
	return nil
}

func (mq *MQ) Dequeue(group string) (Message, error) {
	mq.mutex.Lock()
	defer mq.mutex.Unlock()
	cs, ok := mq.consumers[group]
	if !ok {
		return Message{}, errors.New("consumer group not found")
	}
	now := time.Now()
	if cs.inFlight {
		if now.Sub(cs.lastDeliveryTime) >= mq.config.AckTimeout {
			cs.lastDeliveryTime = now
			if cs.currentIndex < len(mq.messages) {
				return mq.messages[cs.currentIndex], nil
			}
			return Message{}, errors.New("no message available")
		}
		if cs.currentIndex < len(mq.messages) {
			return mq.messages[cs.currentIndex], nil
		}
		return Message{}, errors.New("no message available")
	}
	if cs.currentIndex < len(mq.messages) {
		cs.inFlight = true
		cs.lastDeliveryTime = now
		return mq.messages[cs.currentIndex], nil
	}
	return Message{}, errors.New("no message available")
}

func (mq *MQ) Ack(group, messageID string) error {
	mq.mutex.Lock()
	defer mq.mutex.Unlock()
	cs, ok := mq.consumers[group]
	if !ok {
		return errors.New("consumer group not found")
	}
	if !cs.inFlight {
		return errors.New("no message in flight for group")
	}
	if cs.currentIndex >= len(mq.messages) {
		return errors.New("invalid message index")
	}
	if mq.messages[cs.currentIndex].ID != messageID {
		return errors.New("message ID does not match in-flight message")
	}
	cs.inFlight = false
	cs.currentIndex++
	return nil
}

func (mq *MQ) Shutdown() error {
	mq.mutex.Lock()
	defer mq.mutex.Unlock()
	if mq.file != nil {
		err := mq.file.Sync()
		if err != nil {
			return err
		}
		err = mq.file.Close()
		if err != nil {
			return err
		}
		mq.file = nil
	}
	return nil
}