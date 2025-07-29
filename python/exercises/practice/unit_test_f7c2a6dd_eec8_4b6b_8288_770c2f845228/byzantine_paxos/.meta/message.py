class Message:
    def __init__(self, sender, message_type, slot, value):
        self.sender = sender
        self.type = message_type
        self.slot = slot
        self.value = value

    def __str__(self):
        return f"Message(sender={self.sender}, type={self.type}, slot={self.slot}, value={self.value})"