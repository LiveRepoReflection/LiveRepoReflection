Okay, here's a challenging coding problem for a programming competition, designed to be LeetCode Hard level and incorporating the elements you requested.

### Project Name

```
FractalCompression
```

### Question Description

You are tasked with implementing a fractal image compression algorithm. Fractal compression works by finding self-similar regions within an image and representing the image as a set of transformations that, when iteratively applied to an arbitrary starting image, converge to the original image.

In this simplified problem, you are given a grayscale image represented as a 2D array of integers, where each integer represents the pixel intensity (0-255). Your goal is to find an *approximate* fractal representation of the image. This will involve identifying *domain blocks* and *range blocks* and determining the *transformation* that best maps each domain block to a corresponding range block.

**Specific Requirements:**

1.  **Block Division:** Divide the input image into non-overlapping *range blocks* of size *R x R*. *R* will be a power of 2.
2.  **Domain Pool:** Create a pool of *domain blocks* by sliding a *D x D* window (where *D = 2R*) across the entire image with a stride of *S*. Domain blocks *can* overlap. Consider boundary conditions carefully - when the sliding window goes out of bounds, ignore that domain block.
3.  **Transformation:** For each range block, search for the *best matching* domain block within the domain pool.  The "best match" is determined by the lowest Root Mean Squared Error (RMSE) *after applying the following transformations to the domain block*:

    *   **Downsampling:** Reduce the *D x D* domain block to an *R x R* block by averaging the pixel intensities of each *2x2* region within the domain block.
    *   **Rotation:** Rotate the downsampled *R x R* block by 0, 90, 180, or 270 degrees clockwise.
    *   **Flipping:** Flip the rotated *R x R* block horizontally.
    *   **Intensity Scaling & Offset:** After rotation and flipping, apply an intensity scaling factor *`s`* and an offset *`o`* to each pixel in the transformed domain block such that the RMSE with the range block is minimized.  `s` and `o` can be calculated using linear regression.  Cap `s` to the range `[-1, 1]`.
4.  **Error Metric:** The Root Mean Squared Error (RMSE) between a range block *R* and a transformed domain block *D'* is calculated as:

    ```
    RMSE = sqrt( (1 / (R*R)) * sum((R[i][j] - D'[i][j])^2) )  for all i, j in range(R)
    ```

5.  **Output:** Return a `List` of `Transformation` objects. Each `Transformation` object represents the best match for a range block and should contain:

    *   `rangeRow`: The row index of the top-left corner of the range block in the original image.
    *   `rangeCol`: The column index of the top-left corner of the range block in the original image.
    *   `domainRow`: The row index of the top-left corner of the domain block in the original image.
    *   `domainCol`: The column index of the top-left corner of the domain block in the original image.
    *   `rotation`: An integer representing the rotation applied (0, 90, 180, 270).
    *   `flip`: A boolean indicating whether a horizontal flip was applied.
    *   `scale`: The intensity scaling factor *s* applied.
    *   `offset`: The intensity offset *o* applied.

**Constraints:**

*   `1 <= image.length, image[0].length <= 256`
*   `image.length` and `image[0].length` will be powers of 2.
*   `0 <= image[i][j] <= 255`
*   `R` will be a power of 2 and `1 <= R <= min(image.length, image[0].length) / 2`
*   `D = 2 * R`
*   `1 <= S <= R`
*   The image is assumed to be rectangular (all rows have the same length).
*   Optimize for runtime.  Brute-force approaches may time out.  Consider data structures and algorithmic optimizations to speed up the search for the best matching domain block.
*   Ensure numerical stability.  Avoid potential division by zero errors.
*   Handle edge cases gracefully (e.g., empty image, invalid input parameters).
*   The `Transformation` class should be of your own making.
*   Assume the origin (0, 0) of the image is located at the top-left corner.

**Example:**

```
Input Image:
[[100, 110, 120, 130],
 [105, 115, 125, 135],
 [110, 120, 130, 140],
 [115, 125, 135, 145]]

R = 1
S = 1

Output: (Example - actual values will vary based on implementation details)

[Transformation(rangeRow=0, rangeCol=0, domainRow=0, domainCol=0, rotation=0, flip=false, scale=0.5, offset=50.0),
 Transformation(rangeRow=0, rangeCol=1, domainRow=0, domainCol=1, rotation=90, flip=true, scale=0.6, offset=45.0),
 Transformation(rangeRow=1, rangeCol=0, domainRow=1, domainCol=0, rotation=180, flip=false, scale=0.7, offset=55.0),
 Transformation(rangeRow=1, rangeCol=1, domainRow=1, domainCol=1, rotation=270, flip=true, scale=0.8, offset=60.0)]
```

**Judging Criteria:**

*   Correctness:  The returned list of `Transformation` objects must accurately represent the approximate fractal compression of the input image, minimizing the overall RMSE.
*   Efficiency: The solution must run within a reasonable time limit, even for large images.
*   Code Quality:  The code should be well-structured, readable, and maintainable.  Appropriate use of comments and meaningful variable names is expected.
*   Handling Edge Cases: The solution must handle edge cases and invalid input gracefully, without crashing or producing incorrect results.

This problem requires a good understanding of image processing concepts, data structures, algorithms, and optimization techniques. Good luck!
