import time
import random
from collections import defaultdict
from typing import Dict, List, Any, Callable, Optional, Set, Tuple, Union

class MessageType:
    """Types of messages used in the Byzantine Agreement protocol."""
    PROPOSE = "PROPOSE"
    PREPARE = "PREPARE"
    COMMIT = "COMMIT"
    DECIDE = "DECIDE"
    SYNC = "SYNC"

class Message:
    """Message class for Byzantine Agreement protocol communication."""
    
    def __init__(self, 
                 sender_id: int, 
                 message_type: str, 
                 value: Any, 
                 round_number: int,
                 phase_number: int = 0):
        self.sender_id = sender_id
        self.message_type = message_type
        self.value = value
        self.round_number = round_number
        self.phase_number = phase_number
        self.timestamp = time.time()
        self.unique_id = f"{sender_id}-{message_type}-{round_number}-{phase_number}-{random.randint(0, 100000)}"
    
    def __str__(self) -> str:
        return (f"Message(sender={self.sender_id}, type={self.message_type}, "
                f"value={self.value}, round={self.round_number}, phase={self.phase_number})")

def solve_byzantine_agreement(n: int, 
                             f: int, 
                             initial_proposal: bool, 
                             communication_channel: Callable, 
                             max_rounds: int) -> bool:
    """
    Solve the Byzantine Agreement problem with network partitioning.
    
    Args:
        n: Number of nodes in the network.
        f: Maximum number of faulty nodes.
        initial_proposal: The initial proposal value (True/False) for this node.
        communication_channel: Function to send messages to other nodes.
        max_rounds: Maximum number of rounds before termination.
    
    Returns:
        The agreed upon value (True/False).
    """
    # Ensure the Byzantine fault tolerance condition is met
    if n < 3 * f + 1:
        raise ValueError(f"Need at least {3*f+1} nodes for {f} byzantine faults, but got {n}")
    
    # Choose an arbitrary node ID for this node
    # In a real implementation, this would be a unique identifier for each node
    node_id = 0
    
    # Message storage for received messages
    received_messages: Dict[str, List[Message]] = {
        MessageType.PROPOSE: [],
        MessageType.PREPARE: [],
        MessageType.COMMIT: [],
        MessageType.DECIDE: [],
        MessageType.SYNC: []
    }
    
    # Set of message IDs we've already seen to avoid duplicates
    seen_message_ids: Set[str] = set()
    
    # The values that have been decided
    decided_values: List[bool] = []
    
    # Retransmission queue for messages that might be lost
    retransmission_queue: List[Tuple[int, Message]] = []
    
    # Keep track of current round and phase
    current_round = 0
    
    # The value proposed by this node for the current round
    current_proposal = initial_proposal

    def broadcast_message(message: Message) -> None:
        """
        Broadcasts a message to all nodes and adds it to the retransmission queue.
        """
        for dest_id in range(n):
            if dest_id != node_id:  # Don't send to self
                # Add to retransmission queue
                retransmission_queue.append((dest_id, message))
                
                # Send message
                _ = communication_channel(dest_id, message)
        
        # Also add to our own received messages to process
        process_message(message)
    
    def process_message(message: Message) -> None:
        """
        Process a received message and add it to the appropriate queue.
        """
        if message.unique_id in seen_message_ids:
            return  # Duplicate message
        
        seen_message_ids.add(message.unique_id)
        received_messages[message.message_type].append(message)
    
    def handle_retransmissions() -> None:
        """
        Periodically retransmit messages to handle network partitioning.
        """
        # Copy the queue so we can modify it during iteration
        current_queue = retransmission_queue.copy()
        retransmission_queue.clear()
        
        for dest_id, message in current_queue:
            # Only retransmit messages from recent rounds
            if current_round - message.round_number <= 2:
                result = communication_channel(dest_id, message)
                if result is None:  # Message was lost
                    retransmission_queue.append((dest_id, message))
    
    def check_majority_prepare(round_num: int, phase_num: int, value: bool) -> bool:
        """
        Check if a majority of nodes sent PREPARE messages with the same value.
        """
        count = 0
        for msg in received_messages[MessageType.PREPARE]:
            if (msg.round_number == round_num and 
                msg.phase_number == phase_num and 
                msg.value == value):
                count += 1
        
        return count >= (n - f) // 2
    
    def check_majority_commit(round_num: int, value: bool) -> bool:
        """
        Check if a majority of nodes sent COMMIT messages with the same value.
        """
        count = 0
        for msg in received_messages[MessageType.COMMIT]:
            if msg.round_number == round_num and msg.value == value:
                count += 1
        
        return count >= n - f
    
    def check_decision_messages() -> Optional[bool]:
        """
        Check if enough nodes have decided on a value to consider it final.
        """
        value_counts = defaultdict(int)
        for msg in received_messages[MessageType.DECIDE]:
            if msg.round_number == current_round:
                value_counts[msg.value] += 1
                if value_counts[msg.value] >= n - f:
                    return msg.value
        return None
    
    def get_majority_proposal(round_num: int) -> bool:
        """
        Get the majority proposed value from the current round.
        """
        true_count = 0
        false_count = 0
        
        for msg in received_messages[MessageType.PROPOSE]:
            if msg.round_number == round_num:
                if msg.value is True:
                    true_count += 1
                else:
                    false_count += 1
        
        # If equal, default to the initial proposal
        return true_count >= false_count
    
    def sync_with_network() -> None:
        """
        Try to synchronize with other nodes by requesting their state.
        This helps recover from network partitions.
        """
        sync_message = Message(
            sender_id=node_id,
            message_type=MessageType.SYNC,
            value=current_round,
            round_number=current_round,
            phase_number=0
        )
        
        broadcast_message(sync_message)
    
    def handle_sync_messages() -> None:
        """
        Handle sync messages from other nodes to help recover from partitions.
        """
        for msg in received_messages[MessageType.SYNC]:
            if msg.value > current_round:
                # We're behind, try to catch up by requesting state
                sync_response = Message(
                    sender_id=node_id,
                    message_type=MessageType.SYNC,
                    value=(current_round, current_proposal),
                    round_number=current_round,
                    phase_number=1  # Indicating a sync response
                )
                
                _ = communication_channel(msg.sender_id, sync_response)
    
    # PBFT-inspired consensus algorithm
    while current_round < max_rounds:
        # Start a new round
        print(f"Starting round {current_round} with proposal {current_proposal}")
        
        # Phase 1: Propose
        propose_message = Message(
            sender_id=node_id,
            message_type=MessageType.PROPOSE,
            value=current_proposal,
            round_number=current_round,
            phase_number=0
        )
        
        broadcast_message(propose_message)
        
        # Wait for proposals and handle retransmissions
        for _ in range(3):  # Allow multiple iterations to handle message delays
            handle_retransmissions()
            time.sleep(0.01)  # Small delay to simulate network latency
        
        # Phase 2: Prepare
        majority_value = get_majority_proposal(current_round)
        
        prepare_message = Message(
            sender_id=node_id,
            message_type=MessageType.PREPARE,
            value=majority_value,
            round_number=current_round,
            phase_number=0
        )
        
        broadcast_message(prepare_message)
        
        # Wait for prepare messages and handle retransmissions
        for _ in range(3):  # Allow multiple iterations to handle message delays
            handle_retransmissions()
            time.sleep(0.01)  # Small delay to simulate network latency
        
        # Phase 3: Commit
        if check_majority_prepare(current_round, 0, True):
            commit_value = True
        elif check_majority_prepare(current_round, 0, False):
            commit_value = False
        else:
            # Not enough prepare messages, try to sync with network
            sync_with_network()
            commit_value = majority_value  # Default to majority to make progress
        
        commit_message = Message(
            sender_id=node_id,
            message_type=MessageType.COMMIT,
            value=commit_value,
            round_number=current_round,
            phase_number=0
        )
        
        broadcast_message(commit_message)
        
        # Wait for commit messages and handle retransmissions
        for _ in range(3):  # Allow multiple iterations to handle message delays
            handle_retransmissions()
            handle_sync_messages()
            time.sleep(0.01)  # Small delay to simulate network latency
        
        # Phase 4: Decide
        if check_majority_commit(current_round, True):
            decided_value = True
            decided_values.append(True)
        elif check_majority_commit(current_round, False):
            decided_value = False
            decided_values.append(False)
        else:
            # Not enough commit messages, try another round
            current_round += 1
            continue
        
        decide_message = Message(
            sender_id=node_id,
            message_type=MessageType.DECIDE,
            value=decided_value,
            round_number=current_round,
            phase_number=0
        )
        
        broadcast_message(decide_message)
        
        # Wait for decide messages and handle retransmissions
        for _ in range(3):  # Allow multiple iterations to handle message delays
            handle_retransmissions()
            time.sleep(0.01)  # Small delay to simulate network latency
            
            # Check if we have enough decide messages to finalize
            final_decision = check_decision_messages()
            if final_decision is not None:
                return final_decision
        
        # Update proposal for next round based on decision
        current_proposal = decided_value
        current_round += 1
    
    # If we've reached maximum rounds without consensus
    if decided_values:
        # Return most common decision if we had any
        return max(set(decided_values), key=decided_values.count)
    else:
        # Default to initial proposal if no decisions were made
        return initial_proposal