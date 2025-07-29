Okay, I'm ready to create a challenging Rust coding problem. Here it is:

## Project Name

```
fractal_compression
```

## Question Description

Fractal image compression is a lossy image compression technique that uses the self-similarity of images to achieve compression. Your task is to implement a simplified version of a fractal image compressor and decompressor.

You are given a grayscale image represented as a 2D vector of `u8` values, where each value represents the pixel intensity (0-255).  The image will always have dimensions that are powers of 2 (e.g., 64x64, 128x128, 256x256).

Your compressor should recursively divide the image into non-overlapping *range blocks* of size `B x B`, where `B` is a power of 2 (e.g., 2, 4, 8, 16). For each range block, find the *domain block* within the original image (of size `2B x 2B`) that, when transformed, most closely resembles the range block.  The transformation involves:

1.  **Averaging:** Reduce the `2B x 2B` domain block to a `B x B` block by averaging the four corresponding pixels in each `2x2` sub-block.
2.  **Contrast Scaling:** Scale the contrast of the averaged domain block to match the range block. Let `Dr` and `Rr` be the average pixel intensity of the domain and range blocks, respectively. Let `Ds` and `Rs` be the standard deviation of pixel intensities of the domain and range blocks, respectively.  The scaling factor `s` is calculated as `s = Rs / Ds`. Apply this scaling factor to each pixel in the averaged domain block. If `Ds` is zero, set `s` to 0.
3.  **Brightness Offset:** Adjust the brightness of the contrast-scaled domain block by adding an offset `o` to each pixel.  The offset `o` is calculated as `o = Rr - s * Dr`.
4.  **Quantization:** Truncate pixel intensities to the range [0, 255].

The compressed image will be a vector of tuples. Each tuple represents a transformation to apply to a range block. Each tuple will consist of:

*   `(x, y)`: The coordinates of the top-left corner of the *domain block* in the original image.
*   `s`: The contrast scaling factor.
*   `o`: The brightness offset.

During decompression, for each range block in the final decompressed image, find the corresponding domain block, apply the transformation (averaging, contrast scaling, brightness offset, and quantization), and copy the transformed domain block into the range block's location in the decompressed image.

**Constraints and Requirements:**

*   **Block Size:** Your implementation must support variable block sizes (`B`).
*   **Optimization:** Finding the best domain block can be computationally expensive.  Implement a reasonably efficient search (e.g., sampling a subset of possible domain blocks, using spatial indexing to reduce the search space). Focus on algorithmic efficiency.
*   **Error Metric:** Use the Sum of Squared Differences (SSD) as the error metric to determine how well a transformed domain block matches a range block. Lower SSD indicates a better match.
*   **Edge Cases:** Handle edge cases carefully. For instance, consider the case when the standard deviation of the domain block is zero (avoid division by zero).
*   **Numerical Stability:** Be mindful of potential overflow issues when calculating sums of squares.
*   **Memory Usage:** Be mindful of allocations, especially during the compression phase.
*   **No external image processing libraries:** You are *not* allowed to use external image processing libraries (like `image` crate) for core compression/decompression logic.  You can use them for loading and saving images for testing purposes, but not for the central fractal compression algorithms.
*   **Domain Block Search:** You only need to search domain blocks within the original image, not within previously decompressed portions of the image.
*   **Grayscale only:** Assume the input images are grayscale.

**Functions to implement:**

```rust
// Compresses the image into a vector of transformation tuples.
fn compress_image(image: &Vec<Vec<u8>>, block_size: usize) -> Vec<((usize, usize), f64, f64)> {
    // Implementation here
}

// Decompresses the compressed data back into an image.
fn decompress_image(compressed_data: &Vec<((usize, usize), f64, f64)>, width: usize, height: usize, block_size: usize) -> Vec<Vec<u8>> {
    // Implementation here
}

// Calculates the Sum of Squared Differences (SSD) between two blocks.
fn calculate_ssd(block1: &Vec<Vec<u8>>, block2: &Vec<Vec<u8>>) -> f64 {
    // Implementation here
}
```

**Example Usage (for testing):**

```rust
fn main() {
    // Example usage (you'll need to create a sample image)
    let image_width = 64;
    let image_height = 64;
    let block_size = 8;

    // Create a sample grayscale image (replace with your actual image loading)
    let mut image = vec![vec![0u8; image_width]; image_height];
    // Fill the image with some data for testing
    for i in 0..image_height {
        for j in 0..image_width {
            image[i][j] = ((i + j) % 256) as u8;
        }
    }

    let compressed_data = compress_image(&image, block_size);
    let decompressed_image = decompress_image(&compressed_data, image_width, image_height, block_size);

    // Now you can compare the original and decompressed images (e.g., using calculate_ssd)
    let ssd = calculate_ssd(&image, &decompressed_image);
    println!("SSD between original and decompressed image: {}", ssd);
}
```

This problem combines algorithmic thinking, data structure considerations, optimization techniques, and careful handling of edge cases, making it a very challenging task for advanced programmers. Good luck!
