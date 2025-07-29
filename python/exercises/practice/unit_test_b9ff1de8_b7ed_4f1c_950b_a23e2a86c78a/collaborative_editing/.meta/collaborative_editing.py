INSERT = 0
DELETE = 1

def apply_operations(current_document, operations):
    # Add an index to each operation to restore original order later.
    # Each operation: (original_index, user_id, position, text, op_type)
    ops_with_index = [(i, op[0], op[1], op[2], op[3]) for i, op in enumerate(operations)]
    
    # Sort operations based on position and then user_id (lower user_id wins)
    ops_sorted = sorted(ops_with_index, key=lambda op: (op[2], op[1]))
    
    # List to track applied operations for transformation adjustments.
    # Each element: (applied_position, op_type, length)
    applied_ops = []
    
    # Dictionary to store transformed operations indexed by original index.
    transformed_dict = {}
    
    # Current document that is being updated.
    doc = current_document
    
    # Function to transform a given original position based on applied operations.
    def transform_position(original_position, applied_ops_list):
        new_pos = original_position
        for applied_pos, op_type, length in applied_ops_list:
            if op_type == INSERT:
                if applied_pos <= new_pos:
                    new_pos += length
            elif op_type == DELETE:
                if applied_pos < new_pos:
                    # Only subtract up to the difference between new_pos and applied_pos.
                    delta = min(length, new_pos - applied_pos)
                    new_pos -= delta
        return new_pos

    # Process each operation in the sorted order.
    for idx, user_id, pos, text, op_type in ops_sorted:
        # Transform the given operation's position.
        new_pos = transform_position(pos, applied_ops)
        # Clip the new_pos to valid range.
        if new_pos < 0:
            new_pos = 0
        elif new_pos > len(doc):
            new_pos = len(doc)
        
        # Store the transformed operation.
        transformed_dict[idx] = (user_id, new_pos, text, op_type)
        
        # Apply the operation to the document.
        if op_type == INSERT:
            # Insertion: insert text at new_pos.
            doc = doc[:new_pos] + text + doc[new_pos:]
            # Record this applied operation.
            applied_ops.append((new_pos, INSERT, len(text)))
        elif op_type == DELETE:
            # Deletion: remove substring with length equal to len(text) starting from new_pos.
            delete_length = len(text)
            # Adjust delete_length if it goes beyond current document.
            if new_pos + delete_length > len(doc):
                delete_length = len(doc) - new_pos
            doc = doc[:new_pos] + doc[new_pos + delete_length:]
            applied_ops.append((new_pos, DELETE, delete_length))
    
    # Reconstruct the transformed operations in the original input order.
    transformed_operations = [transformed_dict[i] for i in range(len(operations))]
    
    return doc, transformed_operations