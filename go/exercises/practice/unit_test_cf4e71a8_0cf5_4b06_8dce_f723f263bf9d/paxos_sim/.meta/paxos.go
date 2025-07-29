package paxos

import (
	"math/rand"
	"sync"
	"time"
)

type MessageType int

const (
	Prepare MessageType = iota
	Promise
	Accept
	Accepted
)

type Message struct {
	From        int
	To          int
	Type        MessageType
	ProposalNum int
	Value       int
	AcceptedNum int
}

type Node struct {
	id          int
	nodes       int
	quorum      int
	timeout     time.Duration
	messageLoss float64

	mu               sync.Mutex
	proposalNum      int
	promisedNum      int
	acceptedNum      int
	acceptedValue    int
	learnedValue     int
	state            map[int]int // proposalNum -> value
	inbox            chan Message
	stop             chan struct{}
	active          bool
	highestSeenNum  int
}

func NewNode(id, nodes int, timeout time.Duration) *Node {
	return &Node{
		id:          id,
		nodes:       nodes,
		quorum:      nodes/2 + 1,
		timeout:     timeout,
		messageLoss: 0,
		inbox:       make(chan Message, 100),
		stop:        make(chan struct{}),
		active:      true,
		state:       make(map[int]int),
	}
}

func (n *Node) SetMessageLossProbability(p float64) {
	n.messageLoss = p
}

func (n *Node) Run() {
	for {
		select {
		case msg := <-n.inbox:
			if !n.active {
				continue
			}
			if rand.Float64() < n.messageLoss {
				continue
			}
			n.handleMessage(msg)
		case <-n.stop:
			return
		}
	}
}

func (n *Node) handleMessage(msg Message) {
	n.mu.Lock()
	defer n.mu.Unlock()

	switch msg.Type {
	case Prepare:
		if msg.ProposalNum > n.promisedNum {
			n.promisedNum = msg.ProposalNum
			response := Message{
				From:        n.id,
				To:          msg.From,
				Type:        Promise,
				ProposalNum: msg.ProposalNum,
				AcceptedNum: n.acceptedNum,
				Value:       n.acceptedValue,
			}
			n.send(response)
		} else {
			response := Message{
				From:        n.id,
				To:          msg.From,
				Type:        Promise,
				ProposalNum: n.promisedNum,
			}
			n.send(response)
		}

	case Promise:
		if msg.ProposalNum != n.proposalNum {
			return
		}

		n.state[msg.From] = msg.AcceptedNum
		if msg.AcceptedNum > n.highestSeenNum {
			n.highestSeenNum = msg.AcceptedNum
			n.acceptedValue = msg.Value
		}

		if len(n.state) >= n.quorum {
			acceptMsg := Message{
				From:        n.id,
				To:          -1, // broadcast
				Type:        Accept,
				ProposalNum: n.proposalNum,
				Value:       n.acceptedValue,
			}
			if n.highestSeenNum == 0 {
				acceptMsg.Value = n.acceptedValue
			}
			n.send(acceptMsg)
		}

	case Accept:
		if msg.ProposalNum >= n.promisedNum {
			n.promisedNum = msg.ProposalNum
			n.acceptedNum = msg.ProposalNum
			n.acceptedValue = msg.Value

			acceptedMsg := Message{
				From:        n.id,
				To:          -1, // broadcast to learners
				Type:        Accepted,
				ProposalNum: msg.ProposalNum,
				Value:       msg.Value,
			}
			n.send(acceptedMsg)
		}

	case Accepted:
		if msg.ProposalNum == n.proposalNum {
			n.state[msg.From] = msg.ProposalNum
			if len(n.state) >= n.quorum {
				n.learnedValue = msg.Value
			}
		}
	}
}

func (n *Node) send(msg Message) {
	if msg.To == -1 { // broadcast
		for i := 0; i < n.nodes; i++ {
			if i != n.id {
				m := msg
				m.To = i
				go func(to int) {
					time.Sleep(time.Duration(rand.Intn(50)) * time.Millisecond)
					if to < len(nodes) && nodes[to] != nil {
						nodes[to].inbox <- m
					}
				}(i)
			}
		}
	} else {
		go func() {
			time.Sleep(time.Duration(rand.Intn(50)) * time.Millisecond)
			if msg.To < len(nodes) && nodes[msg.To] != nil {
				nodes[msg.To].inbox <- msg
			}
		}()
	}
}

func (n *Node) Propose(value int) {
	n.mu.Lock()
	defer n.mu.Unlock()

	n.proposalNum = n.id + 1 // Start with unique proposal number
	n.acceptedValue = value
	n.state = make(map[int]int)

	prepareMsg := Message{
		From:        n.id,
		To:          -1, // broadcast
		Type:        Prepare,
		ProposalNum: n.proposalNum,
	}
	n.send(prepareMsg)

	go func() {
		time.Sleep(n.timeout)
		n.mu.Lock()
		if n.learnedValue == 0 && n.active {
			n.mu.Unlock()
			n.Propose(value)
		} else {
			n.mu.Unlock()
		}
	}()
}

func (n *Node) Crash() {
	n.mu.Lock()
	defer n.mu.Unlock()
	n.active = false
	n.state = make(map[int]int)
	n.promisedNum = 0
	n.acceptedNum = 0
	n.acceptedValue = 0
}

func (n *Node) Recover() {
	n.mu.Lock()
	defer n.mu.Unlock()
	n.active = true
	n.state = make(map[int]int)
}

func (n *Node) LearnedValue() int {
	n.mu.Lock()
	defer n.mu.Unlock()
	return n.learnedValue
}

var nodes []*Node

func init() {
	rand.Seed(time.Now().UnixNano())
}

func SetNodes(ns []*Node) {
	nodes = ns
}