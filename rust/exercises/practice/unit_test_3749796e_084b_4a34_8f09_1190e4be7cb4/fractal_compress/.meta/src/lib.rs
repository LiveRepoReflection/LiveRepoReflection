pub fn compress_image(image: &Vec<Vec<u8>>, block_size: usize) -> Vec<((usize, usize), f64, f64)> {
    let height = image.len();
    let width = image[0].len();
    let mut transformations = Vec::new();

    // For every range block in the image (non-overlapping blocks of size block_size x block_size)
    for range_y in (0..height).step_by(block_size) {
        for range_x in (0..width).step_by(block_size) {
            let range_block = get_block(image, range_x, range_y, block_size);
            let (r_avg, r_std) = compute_average_std(&range_block);

            let mut best_error = f64::MAX;
            let mut best_trans = ((0, 0), 0.0, 0.0);

            // For each possible domain block (size 2B x 2B) that fully fits in the image.
            // We iterate over all positions with step 1.
            for domain_y in 0..=(height.saturating_sub(2 * block_size)) {
                for domain_x in 0..=(width.saturating_sub(2 * block_size)) {
                    let domain_block = get_block(image, domain_x, domain_y, 2 * block_size);
                    // Downsample the domain block to size block_size x block_size by averaging each 2x2 sub-block.
                    let averaged = downsample_block(&domain_block, block_size);
                    let (d_avg, d_std) = compute_average_std(&averaged);

                    let s = if d_std == 0.0 { 0.0 } else { r_std / d_std };
                    let o = r_avg - s * d_avg;
                    let transformed = apply_transformation(&averaged, s, o);
                    let error = calculate_ssd(&range_block, &transformed);
                    if error < best_error {
                        best_error = error;
                        best_trans = ((domain_x, domain_y), s, o);
                    }
                }
            }

            transformations.push(best_trans);
        }
    }
    transformations
}

pub fn decompress_image(compressed_data: &Vec<((usize, usize), f64, f64)>, width: usize, height: usize, block_size: usize) -> Vec<Vec<u8>> {
    // Number of iterations for the fixed point iteration.
    let iterations = 10;
    // Initialize the decompressed image with a default value (e.g., 128)
    let mut current = vec![vec![128u8; width]; height];

    // Pre-calculate range block positions in row-major order.
    let mut range_positions = Vec::new();
    for range_y in (0..height).step_by(block_size) {
        for range_x in (0..width).step_by(block_size) {
            range_positions.push((range_x, range_y));
        }
    }

    for _ in 0..iterations {
        let mut next = current.clone();
        // For each range block corresponding to a stored transformation.
        for (i, trans) in compressed_data.iter().enumerate() {
            let (domain_coord, s, o) = *trans;
            // Extract the domain block from the current image.
            let domain_block = get_block(&current, domain_coord.0, domain_coord.1, 2 * block_size);
            // Downsample it.
            let averaged = downsample_block(&domain_block, block_size);
            // Apply transformation.
            let transformed = apply_transformation(&averaged, s, o);
            // Get the range block position from our list (same order as compression).
            let (range_x, range_y) = range_positions[i];
            // Write the transformed block into next image.
            for j in 0..block_size {
                for k in 0..block_size {
                    if range_y + j < height && range_x + k < width {
                        next[range_y + j][range_x + k] = transformed[j][k];
                    }
                }
            }
        }
        current = next;
    }
    current
}

pub fn calculate_ssd(block1: &Vec<Vec<u8>>, block2: &Vec<Vec<u8>>) -> f64 {
    let mut ssd = 0.0;
    for i in 0..block1.len() {
        for j in 0..block1[0].len() {
            let diff = block1[i][j] as f64 - block2[i][j] as f64;
            ssd += diff * diff;
        }
    }
    ssd
}

// Helper function: Extracts a block from the image given top-left coordinate and block size.
fn get_block(image: &Vec<Vec<u8>>, start_x: usize, start_y: usize, block_size: usize) -> Vec<Vec<u8>> {
    let mut block = Vec::with_capacity(block_size);
    for y in start_y..start_y + block_size {
        let mut row = Vec::with_capacity(block_size);
        for x in start_x..start_x + block_size {
            row.push(image[y][x]);
        }
        block.push(row);
    }
    block
}

// Helper function: Downsample a domain block (2*B x 2*B) to size B x B by averaging each non-overlapping 2x2 sub-block.
fn downsample_block(domain_block: &Vec<Vec<u8>>, new_size: usize) -> Vec<Vec<u8>> {
    let mut downsampled = vec![vec![0u8; new_size]; new_size];
    let block_size = domain_block.len(); // This should be 2*new_size.
    for i in 0..new_size {
        for j in 0..new_size {
            let sum = domain_block[2*i][2*j] as u32 +
                      domain_block[2*i][2*j+1] as u32 +
                      domain_block[2*i+1][2*j] as u32 +
                      domain_block[2*i+1][2*j+1] as u32;
            let avg = (sum as f64 / 4.0).round() as u8;
            downsampled[i][j] = avg;
        }
    }
    downsampled
}

// Helper function: Compute average and standard deviation of a block.
fn compute_average_std(block: &Vec<Vec<u8>>) -> (f64, f64) {
    let mut sum = 0.0;
    let n = (block.len() * block[0].len()) as f64;
    for row in block {
        for &val in row {
            sum += val as f64;
        }
    }
    let avg = sum / n;
    let mut variance = 0.0;
    for row in block {
        for &val in row {
            let diff = val as f64 - avg;
            variance += diff * diff;
        }
    }
    let std = (variance / n).sqrt();
    (avg, std)
}

// Helper function: Apply transformation defined by scaling factor s and offset o to the block.
fn apply_transformation(block: &Vec<Vec<u8>>, s: f64, o: f64) -> Vec<Vec<u8>> {
    let mut result = vec![vec![0u8; block[0].len()]; block.len()];
    for i in 0..block.len() {
        for j in 0..block[0].len() {
            let val = s * block[i][j] as f64 + o;
            let clamped = if val < 0.0 {
                0
            } else if val > 255.0 {
                255
            } else {
                val.round() as u8
            };
            result[i][j] = clamped;
        }
    }
    result
}