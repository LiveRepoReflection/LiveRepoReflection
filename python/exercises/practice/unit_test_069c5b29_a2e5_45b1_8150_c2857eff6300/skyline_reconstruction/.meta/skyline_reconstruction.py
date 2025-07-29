def min_effort(skyline, initial_grid, construction_cost, max_height):
    # If the initial grid is empty, no cells exist to modify.
    if not initial_grid:
        return 0

    rows = len(initial_grid)
    existing_cols = len(initial_grid[0])

    # Determine the city width based on the initial grid and the skyline.
    if skyline:
        skyline_end = skyline[-1][0]
    else:
        skyline_end = 0

    new_width = max(existing_cols, skyline_end)

    # Precompute the target height for each column.
    targets = []
    if skyline:
        for c in range(new_width):
            target = 0
            found = False
            # Check each segment defined by the skyline.
            for i in range(len(skyline) - 1):
                start, height = skyline[i]
                end = skyline[i + 1][0]
                if start <= c < end:
                    target = height
                    found = True
                    break
            if not found and c >= skyline[-1][0]:
                target = 0
            targets.append(target)
    else:
        targets = [0] * new_width

    total_diff = 0
    # Loop through each cell in the grid (or virtual cell if column exceeds initial grid)
    for r in range(rows):
        for c in range(new_width):
            # If the column exists in the original grid, use its value; otherwise, assume a zero (virtual column).
            initial_val = initial_grid[r][c] if c < existing_cols else 0
            total_diff += abs(initial_val - targets[c])

    return total_diff * construction_cost