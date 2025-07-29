class Peer:
    def __init__(self, peer_id, initial_document=""):
        self.peer_id = peer_id
        self.document = initial_document

    def local_insert(self, position, char):
        # Ensure insert position is not negative and append if beyond document length.
        if position < 0:
            position = 0
        if position > len(self.document):
            position = len(self.document)
        self.document = self.document[:position] + char + self.document[position:]
        # In a real system, this operation would be broadcast to other peers.

    def local_delete(self, position):
        # Delete character only if the position is within the document.
        if position < 0 or position >= len(self.document):
            return
        self.document = self.document[:position] + self.document[position + 1:]
        # In a real system, this operation would be broadcast to other peers.

    def receive_operation(self, operation, sender_id):
        # Apply an operation received from another peer.
        op_type = operation.get("type")
        position = operation.get("position", 0)
        if op_type == "insert":
            char = operation.get("char")
            if char is None:
                raise ValueError("Insert operation must include a 'char'")
            if position < 0:
                position = 0
            if position > len(self.document):
                position = len(self.document)
            self.document = self.document[:position] + char + self.document[position:]
        elif op_type == "delete":
            if position < 0 or position >= len(self.document):
                return
            self.document = self.document[:position] + self.document[position + 1:]
        else:
            raise ValueError("Unknown operation type: " + str(op_type))

    def get_document(self):
        return self.document