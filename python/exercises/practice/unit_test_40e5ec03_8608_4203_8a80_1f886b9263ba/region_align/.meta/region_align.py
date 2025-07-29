import math
import numpy as np
from statistics import median

def find_optimal_alignment(image_a, image_b, region_width, region_height, search_radius):
    """
    Find the optimal alignment of a rectangular region within ImageA to a corresponding region within ImageB,
    maximizing a specific similarity score while ensuring the alignment is robust to noise and minor distortions.

    Args:
        image_a: A 2D list of integers representing the first grayscale image.
        image_b: A 2D list of integers representing the second grayscale image.
        region_width: The width of the rectangular region to be aligned.
        region_height: The height of the rectangular region to be aligned.
        search_radius: Maximum horizontal and vertical distance to search for alignment.

    Returns:
        A tuple (row_offset, col_offset, similarity_score) representing the optimal alignment.
    """
    # Handle edge cases
    if not image_a or not image_b or not image_a[0] or not image_b[0]:
        return 0, 0, -float('inf')
    
    image_a_height = len(image_a)
    image_a_width = len(image_a[0])
    image_b_height = len(image_b)
    image_b_width = len(image_b[0])
    
    # Check if the region is larger than the images
    if region_width > image_a_width or region_height > image_a_height or \
       region_width > image_b_width or region_height > image_b_height:
        return 0, 0, -float('inf')
    
    # Extract the region from image_a
    region_a = []
    for i in range(region_height):
        row = []
        for j in range(region_width):
            row.append(image_a[i][j])
        region_a.append(row)
    
    # Precompute statistics for region_a
    region_a_flat = [pixel for row in region_a for pixel in row]
    region_a_median = median(region_a_flat)
    normalized_region_a = [[pixel - region_a_median for pixel in row] for row in region_a]
    
    mean_a = sum(sum(row) for row in normalized_region_a) / (region_width * region_height)
    
    # Calculate std_dev_a carefully to avoid numerical issues
    squared_diff_sum_a = sum(sum((pixel - mean_a) ** 2 for pixel in row) for row in normalized_region_a)
    std_dev_a = math.sqrt(squared_diff_sum_a / (region_width * region_height))
    
    # Initialize variables to track the best alignment
    best_row_offset = 0
    best_col_offset = 0
    best_score = -float('inf')
    
    # Calculate NCC for all possible offsets within the search radius
    for row_offset in range(-search_radius, search_radius + 1):
        for col_offset in range(-search_radius, search_radius + 1):
            # Check if the aligned region is within the bounds of image_b
            if (row_offset < 0 or col_offset < 0 or
                row_offset + region_height > image_b_height or
                col_offset + region_width > image_b_width):
                continue
            
            # Extract the candidate region from image_b
            region_b = []
            for i in range(region_height):
                row = []
                for j in range(region_width):
                    row.append(image_b[row_offset + i][col_offset + j])
                region_b.append(row)
            
            # Normalize region_b by subtracting the median
            region_b_flat = [pixel for row in region_b for pixel in row]
            region_b_median = median(region_b_flat)
            normalized_region_b = [[pixel - region_b_median for pixel in row] for row in region_b]
            
            # Calculate mean and std_dev for normalized_region_b
            mean_b = sum(sum(row) for row in normalized_region_b) / (region_width * region_height)
            
            squared_diff_sum_b = sum(sum((pixel - mean_b) ** 2 for pixel in row) for row in normalized_region_b)
            std_dev_b = math.sqrt(squared_diff_sum_b / (region_width * region_height))
            
            # Check for zero standard deviation
            if std_dev_a == 0 or std_dev_b == 0:
                score = -1.0
            else:
                # Calculate the normalized cross-correlation (NCC)
                numerator = 0
                for i in range(region_height):
                    for j in range(region_width):
                        a_term = normalized_region_a[i][j] - mean_a
                        b_term = normalized_region_b[i][j] - mean_b
                        numerator += a_term * b_term
                
                denominator = std_dev_a * std_dev_b * region_width * region_height
                score = numerator / denominator
            
            # Update best alignment if the current score is better
            if score > best_score:
                best_score = score
                best_row_offset = row_offset
                best_col_offset = col_offset
    
    return best_row_offset, best_col_offset, best_score

def find_optimal_alignment_optimized(image_a, image_b, region_width, region_height, search_radius):
    """
    Optimized version using NumPy for faster calculations.
    """
    # Handle edge cases
    if not image_a or not image_b or not image_a[0] or not image_b[0]:
        return 0, 0, -float('inf')
    
    # Convert to numpy arrays for more efficient processing
    image_a = np.array(image_a, dtype=float)
    image_b = np.array(image_b, dtype=float)
    
    image_a_height, image_a_width = image_a.shape
    image_b_height, image_b_width = image_b.shape
    
    # Check if the region is larger than the images
    if region_width > image_a_width or region_height > image_a_height or \
       region_width > image_b_width or region_height > image_b_height:
        return 0, 0, -float('inf')
    
    # Extract the region from image_a
    region_a = image_a[:region_height, :region_width]
    
    # Precompute statistics for region_a
    region_a_median = np.median(region_a)
    normalized_region_a = region_a - region_a_median
    
    mean_a = np.mean(normalized_region_a)
    std_dev_a = np.std(normalized_region_a)
    
    # Initialize variables to track the best alignment
    best_row_offset = 0
    best_col_offset = 0
    best_score = -float('inf')
    
    # Calculate NCC for all possible offsets within the search radius
    for row_offset in range(-search_radius, search_radius + 1):
        for col_offset in range(-search_radius, search_radius + 1):
            # Check if the aligned region is within the bounds of image_b
            if (row_offset < 0 or col_offset < 0 or
                row_offset + region_height > image_b_height or
                col_offset + region_width > image_b_width):
                continue
            
            # Extract the candidate region from image_b
            region_b = image_b[row_offset:row_offset+region_height, 
                               col_offset:col_offset+region_width]
            
            # Normalize region_b by subtracting the median
            region_b_median = np.median(region_b)
            normalized_region_b = region_b - region_b_median
            
            # Calculate mean and std_dev for normalized_region_b
            mean_b = np.mean(normalized_region_b)
            std_dev_b = np.std(normalized_region_b)
            
            # Check for zero standard deviation
            if std_dev_a == 0 or std_dev_b == 0:
                score = -1.0
            else:
                # Calculate the normalized cross-correlation (NCC)
                numerator = np.sum((normalized_region_a - mean_a) * (normalized_region_b - mean_b))
                denominator = std_dev_a * std_dev_b * region_width * region_height
                score = numerator / denominator
            
            # Update best alignment if the current score is better
            if score > best_score:
                best_score = score
                best_row_offset = row_offset
                best_col_offset = col_offset
    
    return best_row_offset, best_col_offset, best_score

# Use the optimized version as the main function
def find_optimal_alignment(image_a, image_b, region_width, region_height, search_radius):
    """
    Main function that calls the optimized implementation.
    
    Args:
        image_a: A 2D list of integers representing the first grayscale image.
        image_b: A 2D list of integers representing the second grayscale image.
        region_width: The width of the rectangular region to be aligned.
        region_height: The height of the rectangular region to be aligned.
        search_radius: Maximum horizontal and vertical distance to search for alignment.

    Returns:
        A tuple (row_offset, col_offset, similarity_score) representing the optimal alignment.
    """
    try:
        # Try using the optimized NumPy implementation
        import numpy as np
        return find_optimal_alignment_optimized(image_a, image_b, region_width, region_height, search_radius)
    except ImportError:
        # Fall back to pure Python implementation if NumPy is not available
        return find_optimal_alignment_pure_python(image_a, image_b, region_width, region_height, search_radius)

# Rename the original function for use as a fallback
find_optimal_alignment_pure_python = find_optimal_alignment_optimized