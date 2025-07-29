def transform(op1, op2):
    """
    Transform the remote operation op2 based on the local operation op1.
    
    Supported operation types:
        - insert: {'type': 'insert', 'index': int, 'text': str}
        - delete: {'type': 'delete', 'index': int, 'length': int}
    
    The transformation rules assume that when op1 and op2 have the same index,
    op1 takes precedence, hence op2 is shifted right in the case of inserts,
    or adjusted accordingly in the case of deletes.
    
    Args:
        op1: The local operation that has already been applied.
        op2: The remote operation that needs transformation.
        
    Returns:
        A dictionary representing the transformed version of op2.
    """
    if op1['type'] == 'insert':
        # Handle transformation when op1 is an insert.
        shift = len(op1['text'])
        if op2['type'] == 'insert':
            # If op1 is inserted at an index less than or equal to op2 index,
            # shift op2 to the right.
            if op1['index'] < op2['index'] or op1['index'] == op2['index']:
                return {'type': 'insert', 'index': op2['index'] + shift, 'text': op2['text']}
            else:
                return op2.copy()
        elif op2['type'] == 'delete':
            # If op1 insertion occurs before or at op2 deletion index, shift op2 deletion.
            if op1['index'] <= op2['index']:
                return {'type': 'delete', 'index': op2['index'] + shift, 'length': op2['length']}
            else:
                return op2.copy()

    elif op1['type'] == 'delete':
        # Handle transformation when op1 is a delete.
        L = op1['index']
        R = op1['index'] + op1['length']
        if op2['type'] == 'insert':
            # If the insertion is after the deletion region, shift left.
            if op2['index'] >= R:
                return {'type': 'insert', 'index': op2['index'] - op1['length'], 'text': op2['text']}
            elif op2['index'] < L:
                return op2.copy()
            else:
                # op2 insertion occurs within the deleted region: set to begin at op1.index.
                return {'type': 'insert', 'index': L, 'text': op2['text']}
        elif op2['type'] == 'delete':
            start2 = op2['index']
            end2 = op2['index'] + op2['length']
            if end2 <= L:
                # op2 deletion is entirely before op1 deletion.
                return op2.copy()
            elif start2 >= R:
                # op2 deletion is entirely after op1 deletion.
                return {'type': 'delete', 'index': start2 - op1['length'], 'length': op2['length']}
            else:
                # There is an overlap between the two deletions.
                # Set new index: if op2 deletion starts before op1 deletion, keep its index, else use L.
                new_index = start2 if start2 < L else L
                # Compute overlapping length.
                overlap = max(0, min(R, end2) - max(L, start2))
                new_length = op2['length'] - overlap
                if new_length < 0:
                    new_length = 0
                return {'type': 'delete', 'index': new_index, 'length': new_length}
                
    # If none of the above conditions apply, return a shallow copy of op2.
    return op2.copy()


if __name__ == "__main__":
    # Simple interactive testing
    # This block is for manual testing and demonstration purposes.
    # For automated testing, please run the unit tests provided separately.
    
    # Example scenario:
    # Document initially: "abc"
    # Local operation: insert "X" at index 1 -> "aXbc"
    # Remote operation: delete 1 character at index 2 (intended for "abc")
    op1 = {'type': 'insert', 'index': 1, 'text': 'X'}
    op2 = {'type': 'delete', 'index': 2, 'length': 1}
    transformed = transform(op1, op2)
    print("Transformed operation:", transformed)