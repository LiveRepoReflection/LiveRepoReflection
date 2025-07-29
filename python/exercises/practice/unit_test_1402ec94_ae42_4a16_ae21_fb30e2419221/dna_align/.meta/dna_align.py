def max_alignment_score(seq1, seq2):
    GAP = -2
    MATCH = 2
    MISMATCH = -1

    n = len(seq1)
    m = len(seq2)

    # If both sequences are empty, return 0
    if n == 0 and m == 0:
        return 0

    # Initialize the first row of the DP table.
    prev = [j * GAP for j in range(m + 1)]
    current = [0] * (m + 1)

    # Fill the DP table using a rolling array approach to optimize space.
    for i in range(1, n + 1):
        current[0] = i * GAP  # Gap penalty for sequence2 gap
        for j in range(1, m + 1):
            # Calculate match/mismatch score
            diag = prev[j - 1] + (MATCH if seq1[i - 1] == seq2[j - 1] else MISMATCH)
            # Calculate score if seq1[i-1] aligns with a gap
            up = prev[j] + GAP
            # Calculate score if seq2[j-1] aligns with a gap
            left = current[j - 1] + GAP
            current[j] = max(diag, up, left)
        # Swap the rows for next iteration
        prev, current = current, prev

    # The optimal alignment score is now in the last cell of the previous row.
    return prev[m]