use fractal_compress::{compress_image, decompress_image, calculate_ssd};

#[test]
fn test_calculate_ssd_identical_blocks() {
    let block1 = vec![
        vec![1u8, 2, 3],
        vec![4, 5, 6],
    ];
    let block2 = vec![
        vec![1u8, 2, 3],
        vec![4, 5, 6],
    ];
    let ssd = calculate_ssd(&block1, &block2);
    assert_eq!(ssd, 0.0);
}

#[test]
fn test_calculate_ssd_different_blocks() {
    let block1 = vec![
        vec![10u8, 20, 30],
        vec![40, 50, 60],
    ];
    let block2 = vec![
        vec![12u8, 22, 28],
        vec![38, 52, 63],
    ];
    let ssd = calculate_ssd(&block1, &block2);
    // Differences: [2, 2, 2, 2, 2, 3] squared: [4, 4, 4, 4, 4, 9] sum = 29
    assert_eq!(ssd, 29.0);
}

#[test]
fn test_constant_image() {
    let width = 16;
    let height = 16;
    let block_size = 4;
    let constant_value = 128u8;

    // Create a constant image.
    let image: Vec<Vec<u8>> = vec![vec![constant_value; width]; height];

    let compressed_data = compress_image(&image, block_size);
    let decompressed_image = decompress_image(&compressed_data, width, height, block_size);

    // Expect the decompressed image to match the original exactly since the image is constant.
    for i in 0..height {
        for j in 0..width {
            assert_eq!(image[i][j], decompressed_image[i][j]);
        }
    }

    let ssd = calculate_ssd(&image, &decompressed_image);
    assert_eq!(ssd, 0.0);
}

#[test]
fn test_gradient_image() {
    let width = 32;
    let height = 32;
    let block_size = 4;

    // Generate a gradient image: each pixel is (i+j) mod 256.
    let image: Vec<Vec<u8>> = (0..height)
        .map(|i| {
            (0..width)
                .map(|j| ((i + j) % 256) as u8)
                .collect::<Vec<u8>>()
        })
        .collect();

    let compressed_data = compress_image(&image, block_size);
    let decompressed_image = decompress_image(&compressed_data, width, height, block_size);

    // Ensure dimensions are preserved.
    assert_eq!(decompressed_image.len(), height);
    for row in decompressed_image.iter() {
        assert_eq!(row.len(), width);
    }

    // Calculate the SSD between original and decompressed images.
    let ssd = calculate_ssd(&image, &decompressed_image);

    // For gradient images, some deviation is expected.
    // We set an arbitrary threshold for acceptable SSD.
    let threshold = 5000.0;
    assert!(ssd < threshold, "SSD {} exceeds threshold {}", ssd, threshold);
}