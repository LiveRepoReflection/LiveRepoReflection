def process_operations(operations):
    """
    Processes a list of operations on a collaborative document and returns the final document.
    Each operation is a dictionary containing:
        - user_id: int
        - timestamp: int
        - type: "insert", "delete", or "edit"
        - index: int
        - content: string for "insert" and "edit" (None for "delete")
    
    The conflict resolution strategy is as follows:
      1. For simultaneous insertions (same timestamp) at the same index, the operation with the lower user_id wins.
      2. For conflicting operations on the same paragraph (edit vs. delete), edit (non-destructive)
         takes precedence over delete.
      3. Operations are applied in sorted order (by timestamp then by user_id) to simulate out-of-order arrival.
    
    The document is represented as a list of paragraphs. Each paragraph is stored as a dictionary with metadata:
        - content: the paragraph text
        - insert_timestamp: timestamp of the insert operation
        - insert_user: the user_id who performed the insert
        - protected: a boolean flag set to True if an edit operation has been applied successfully
                     (thus preventing subsequent deletion).
    """
    # Sort operations by timestamp, then by user_id.
    sorted_ops = sorted(operations, key=lambda op: (op["timestamp"], op["user_id"]))
    document = []  # List of paragraph dictionaries

    for op in sorted_ops:
        op_type = op["type"]
        idx = op["index"]
        if op_type == "insert":
            # Create new paragraph record.
            new_paragraph = {
                "content": op["content"],
                "insert_timestamp": op["timestamp"],
                "insert_user": op["user_id"],
                "protected": False
            }
            # If index is greater than current document length, append.
            if idx > len(document):
                document.append(new_paragraph)
            elif idx == len(document):
                document.insert(idx, new_paragraph)
            else:
                # When inserting at an existing index, check for simultaneous insert conflict.
                existing = document[idx]
                if ("insert_timestamp" in existing and 
                    existing["insert_timestamp"] == op["timestamp"]):
                    # Conflict: lower user_id wins.
                    if existing["insert_user"] <= op["user_id"]:
                        continue
                    else:
                        document[idx] = new_paragraph
                else:
                    # Normal insert shifting subsequent paragraphs.
                    document.insert(idx, new_paragraph)
        elif op_type == "edit":
            # If the index is invalid, ignore the edit.
            if idx < 0 or idx >= len(document):
                continue
            # Apply edit: update content and mark as protected.
            document[idx]["content"] = op["content"]
            document[idx]["protected"] = True
        elif op_type == "delete":
            # Verify valid index.
            if idx < 0 or idx >= len(document):
                continue
            # If the paragraph is protected (edited), do not delete.
            if document[idx].get("protected", False):
                continue
            # Otherwise, delete the paragraph.
            document.pop(idx)
    # Construct the final document as a list of paragraph texts.
    return [paragraph["content"] for paragraph in document]

if __name__ == '__main__':
    # Example usage:
    operations = [
        {"user_id": 1, "timestamp": 1000, "type": "insert", "index": 0, "content": "First Paragraph"},
        {"user_id": 2, "timestamp": 1000, "type": "insert", "index": 0, "content": "Second Paragraph"},
        {"user_id": 1, "timestamp": 2000, "type": "edit", "index": 0, "content": "Edited Paragraph"},
        {"user_id": 2, "timestamp": 3000, "type": "delete", "index": 0, "content": None},
    ]
    final_document = process_operations(operations)
    print(final_document)