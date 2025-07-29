def transform_operation(local_operation, remote_operation):
    # Transform a local operation in the context of a remote operation that has already been applied.
    # Two operation types are supported: "insert" and "delete".
    #
    # local_operation:
    #   For insert: ("insert", position, text)
    #   For delete: ("delete", position, length)
    # remote_operation is of the same format.
    #
    # The transformation logic is as follows:
    #
    # 1. When both operations are inserts:
    #    - If the local insert's position is greater than or equal to the remote insert's position,
    #      then shift the local position to the right by the length of the remote text.
    #
    # 2. When the local operation is insert and the remote operation is delete:
    #    - If the local insert's position is greater than or equal to remote deletion's end,
    #      then shift the local position to the left by the remote deletion length.
    #    - If the local insert's position falls within the remote deletion region,
    #      then set the insertion position to the start of the deletion region.
    #    - Otherwise, leave the local insert unchanged.
    #
    # 3. When the local operation is delete and the remote operation is insert:
    #    - If the remote insertion occurs before or at the local deletion start,
    #      then shift the local deletion start to the right by the length of the inserted text.
    #    - Otherwise, leave the deletion unchanged.
    #
    # 4. When both operations are deletes:
    #    - If the remote delete occurs before the local delete, shift the local delete start left by
    #      the number of characters deleted before the local operation.
    #    - Then, calculate the overlap between the original local deletion range and the remote deletion range.
    #    - Reduce the deletion length by the size of the overlap (ensuring it doesn't become negative).
    
    op_local = local_operation[0]
    op_remote = remote_operation[0]

    if op_local == "insert":
        lpos, ltext = local_operation[1], local_operation[2]
        if op_remote == "insert":
            rpos, rtext = remote_operation[1], remote_operation[2]
            if lpos >= rpos:
                lpos += len(rtext)
            return ("insert", lpos, ltext)
        elif op_remote == "delete":
            rpos, rlength = remote_operation[1], remote_operation[2]
            if lpos >= rpos + rlength:
                new_pos = lpos - rlength
            elif rpos <= lpos < rpos + rlength:
                new_pos = rpos
            else:
                new_pos = lpos
            return ("insert", new_pos, ltext)

    elif op_local == "delete":
        lpos, llength = local_operation[1], local_operation[2]
        if op_remote == "insert":
            rpos, rtext = remote_operation[1], remote_operation[2]
            if rpos <= lpos:
                lpos += len(rtext)
            return ("delete", lpos, llength)
        elif op_remote == "delete":
            rpos, rlength = remote_operation[1], remote_operation[2]
            # Adjust local start if remote deletion was before local deletion.
            if rpos < lpos:
                shift = min(rlength, lpos - rpos)
                lpos -= shift

            # Calculate the overlap between the original local deletion and the remote deletion.
            original_lpos = local_operation[1]
            local_end = original_lpos + llength
            remote_end = rpos + rlength
            overlap = max(0, min(local_end, remote_end) - max(original_lpos, rpos))
            new_length = llength - overlap
            if new_length < 0:
                new_length = 0
            return ("delete", lpos, new_length)

    return local_operation