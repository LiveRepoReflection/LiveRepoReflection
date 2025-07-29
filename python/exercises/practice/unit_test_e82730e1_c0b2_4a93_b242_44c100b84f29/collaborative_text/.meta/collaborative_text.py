class Document:
    def __init__(self):
        # Store operations by their unique op_id to ensure idempotency.
        self.ops = {}

    def apply_operation(self, op):
        op_id = op["op_id"]
        if op_id in self.ops:
            return
        # Store a shallow copy of the operation.
        self.ops[op_id] = {
            "type": op["type"],
            "pos": op["pos"],
            "op_id": op["op_id"],
            "user": op.get("user"),
            "char": op.get("char")
        }

    def get_text(self):
        # Reconstruct the document state by applying operations sorted by op_id.
        # For insert operations, use a transformation rule based on the original position.
        # We will maintain a list of tuples for inserted characters:
        # Each tuple is (character, original_pos, op_id)
        state = []
        # Process operations in sorted order by op_id.
        sorted_ops = sorted(self.ops.values(), key=lambda op: op["op_id"])
        for op in sorted_ops:
            if op["type"] == "insert":
                # Compute effective index as:
                # count the number of items already in state with:
                #   (item's original position < current op's pos) OR
                #   (item's original position == current op's pos AND item.op_id < current op.op_id)
                count = 0
                for item in state:
                    if item[1] < op["pos"] or (item[1] == op["pos"] and item[2] < op["op_id"]):
                        count += 1
                # Effective index is count, but it cannot exceed current length.
                effective_index = count if count <= len(state) else len(state)
                state.insert(effective_index, (op["char"], op["pos"], op["op_id"]))
            elif op["type"] == "delete":
                # For deletion, use the pos as provided.
                effective_index = op["pos"]
                if 0 <= effective_index < len(state):
                    # Remove the element at effective_index.
                    state.pop(effective_index)
        # Return the final text by concatenating the characters in order.
        return "".join(item[0] for item in state)