class Document:
    def __init__(self, content=""):
        self.content = content

    def insert(self, position, text):
        if position < 0:
            position = 0
        if position > len(self.content):
            position = len(self.content)
        self.content = self.content[:position] + text + self.content[position:]

    def delete(self, position, length):
        if position < 0:
            position = 0
        if position > len(self.content):
            return
        self.content = self.content[:position] + self.content[position + length:]


class InsertOperation:
    def __init__(self, position, text, op_id=None):
        self.position = position
        self.text = text
        self.op_id = op_id

    def transform(self, other):
        # Transform self (an insert op) based on other op that has already been applied.
        if isinstance(other, InsertOperation):
            # If the other insert happened at or before our position, shift right.
            if self.position > other.position or self.position == other.position:
                new_pos = self.position + len(other.text)
            else:
                new_pos = self.position
        elif isinstance(other, DeleteOperation):
            # If deletion happens completely before the insert, shift left.
            if self.position >= other.position + other.length:
                new_pos = self.position - other.length
            # If deletion covers the insert position, move to the start of deletion.
            elif self.position >= other.position:
                new_pos = other.position
            else:
                new_pos = self.position
        else:
            new_pos = self.position
        return InsertOperation(new_pos, self.text, self.op_id)

    def apply(self, document):
        document.insert(self.position, self.text)


class DeleteOperation:
    def __init__(self, position, length, op_id=None):
        self.position = position
        self.length = length
        self.op_id = op_id

    def transform(self, other):
        # Transform self (a delete op) based on other op that has already been applied.
        if isinstance(other, InsertOperation):
            # If an insert happened before the delete, shift the delete position right.
            if self.position >= other.position:
                new_pos = self.position + len(other.text)
            else:
                new_pos = self.position
            new_length = self.length
        elif isinstance(other, DeleteOperation):
            if self.position >= other.position + other.length:
                # Other deletion is entirely before self
                new_pos = self.position - other.length
                new_length = self.length
            elif self.position + self.length <= other.position:
                # Other deletion is entirely after self; no change.
                new_pos = self.position
                new_length = self.length
            else:
                # Overlap case. Adjust the deletion interval.
                start = self.position
                end = self.position + self.length
                other_start = other.position
                other_end = other.position + other.length

                # Calculate new start
                if start >= other_start and start < other_end:
                    new_start = other_start
                else:
                    new_start = start

                # Calculate new end after removal of overlapping part.
                new_end = end
                if other_start <= start:
                    overlap = min(end, other_end) - start
                    new_end = end - overlap
                else:
                    overlap = min(end, other_end) - other_start
                    new_end = end - overlap
                new_length = max(0, new_end - new_start)
                new_pos = new_start
        else:
            new_pos = self.position
            new_length = self.length
        return DeleteOperation(new_pos, new_length, self.op_id)

    def apply(self, document):
        document.delete(self.position, self.length)


class Server:
    def __init__(self, initial_document=""):
        self.document = Document(initial_document)
        self.operations = []  # List of tuples (client, operation)
        self.clients = []

    def register_client(self, client):
        self.clients.append(client)

    def add_operation(self, op, client):
        self.operations.append((client, op))

    def process_all_operations(self):
        processed_ops = []
        # Process operations in the order they were received.
        for client, op in self.operations:
            transformed_op = op
            for _, prev_op in processed_ops:
                transformed_op = transformed_op.transform(prev_op)
            transformed_op.apply(self.document)
            processed_ops.append((client, transformed_op))
        # Broadcast the updated document content to all clients.
        for client in self.clients:
            client.document.content = self.document.content
        # Clear the operation queue.
        self.operations = []


class Client:
    def __init__(self, server, client_id):
        self.server = server
        self.client_id = client_id
        # Initialize the client with a copy of the server's document.
        self.document = Document(self.server.document.content)
        self.server.register_client(self)

    def send_operation(self, op):
        self.server.add_operation(op, self)