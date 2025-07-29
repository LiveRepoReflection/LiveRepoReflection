import unittest
import math
from region_align import find_optimal_alignment

class RegionAlignTest(unittest.TestCase):
    
    def test_perfect_match(self):
        # Simple case: identical regions should have perfect correlation
        image_a = [[100, 110, 120],
                   [130, 140, 150],
                   [160, 170, 180]]
        
        image_b = [[100, 110, 120],
                   [130, 140, 150],
                   [160, 170, 180]]
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 2, 2, 0
        )
        
        self.assertEqual(row_offset, 0)
        self.assertEqual(col_offset, 0)
        self.assertAlmostEqual(similarity_score, 1.0)
    
    def test_simple_offset(self):
        # Test case where the region is shifted
        image_a = [[10, 20, 30],
                   [40, 50, 60],
                   [70, 80, 90]]
        
        image_b = [[0, 0, 0, 0, 0],
                   [0, 10, 20, 30, 0],
                   [0, 40, 50, 60, 0],
                   [0, 70, 80, 90, 0],
                   [0, 0, 0, 0, 0]]
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 3, 3, 2
        )
        
        self.assertEqual(row_offset, 1)
        self.assertEqual(col_offset, 1)
        self.assertAlmostEqual(similarity_score, 1.0)
    
    def test_scaled_intensities(self):
        # Test case where regions match but with scaled intensities
        image_a = [[10, 20, 30],
                   [40, 50, 60],
                   [70, 80, 90]]
        
        # Doubled intensities
        image_b = [[20, 40, 60],
                   [80, 100, 120],
                   [140, 160, 180]]
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 3, 3, 0
        )
        
        self.assertEqual(row_offset, 0)
        self.assertEqual(col_offset, 0)
        self.assertAlmostEqual(similarity_score, 1.0)
    
    def test_with_noise(self):
        # Test with noise added
        image_a = [[100, 110, 120],
                   [130, 140, 150],
                   [160, 170, 180]]
        
        # Same image with some noise
        image_b = [[105, 108, 122],
                   [128, 142, 148],
                   [163, 167, 183]]
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 3, 3, 1
        )
        
        self.assertEqual(row_offset, 0)
        self.assertEqual(col_offset, 0)
        self.assertTrue(similarity_score > 0.95)  # Should have high correlation despite noise
    
    def test_search_radius(self):
        # Test if search radius is respected
        image_a = [[10, 20],
                   [30, 40]]
        
        # image_a is at offset (2, 2) in image_b
        image_b = [[0, 0, 0, 0],
                   [0, 0, 0, 0],
                   [0, 0, 10, 20],
                   [0, 0, 30, 40]]
        
        # With search_radius = 1, shouldn't find the match
        row_offset_small, col_offset_small, score_small = find_optimal_alignment(
            image_a, image_b, 2, 2, 1
        )
        
        # With search_radius = 2, should find the match
        row_offset_large, col_offset_large, score_large = find_optimal_alignment(
            image_a, image_b, 2, 2, 2
        )
        
        self.assertNotEqual((row_offset_small, col_offset_small), (2, 2))
        self.assertEqual((row_offset_large, col_offset_large), (2, 2))
        self.assertTrue(score_large > score_small)
    
    def test_no_valid_alignment(self):
        # Test when region is larger than image
        image_a = [[10, 20],
                   [30, 40]]
        
        image_b = [[50, 60],
                   [70, 80]]
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 3, 3, 1
        )
        
        self.assertEqual(row_offset, 0)
        self.assertEqual(col_offset, 0)
        self.assertEqual(similarity_score, -float('inf'))
    
    def test_empty_images(self):
        # Test with empty images
        image_a = []
        image_b = []
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 1, 1, 1
        )
        
        self.assertEqual(row_offset, 0)
        self.assertEqual(col_offset, 0)
        self.assertEqual(similarity_score, -float('inf'))
    
    def test_zero_search_radius(self):
        # Test with search radius of 0
        image_a = [[10, 20, 30],
                   [40, 50, 60],
                   [70, 80, 90]]
        
        image_b = [[10, 20, 30],
                   [40, 50, 60],
                   [70, 80, 90]]
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 2, 2, 0
        )
        
        self.assertEqual(row_offset, 0)
        self.assertEqual(col_offset, 0)
        self.assertAlmostEqual(similarity_score, 1.0)
    
    def test_inverse_correlation(self):
        # Test with inversely correlated images
        image_a = [[10, 20],
                   [30, 40]]
        
        # Inverse of image_a
        image_b = [[40, 30],
                   [20, 10]]
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 2, 2, 0
        )
        
        self.assertEqual(row_offset, 0)
        self.assertEqual(col_offset, 0)
        self.assertTrue(similarity_score < 0)  # Should have negative correlation
    
    def test_zero_std_dev(self):
        # Test with constant intensity (zero standard deviation)
        image_a = [[50, 50],
                   [50, 50]]
        
        image_b = [[50, 50],
                   [50, 50]]
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 2, 2, 0
        )
        
        # When std_dev is 0, similarity score should be either -1 or handled specially
        self.assertEqual(row_offset, 0)
        self.assertEqual(col_offset, 0)
        self.assertEqual(similarity_score, -1.0)
    
    def test_larger_images(self):
        # Test with larger images
        image_a = [
            [i*j for j in range(10)] 
            for i in range(10)
        ]
        
        # Same pattern but shifted by (2, 3)
        image_b = [
            [0] * 15 for _ in range(2)
        ] + [
            [0, 0, 0] + [i*j for j in range(10)] + [0, 0]
            for i in range(10)
        ] + [
            [0] * 15 for _ in range(3)
        ]
        
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 10, 10, 5
        )
        
        self.assertEqual(row_offset, 2)
        self.assertEqual(col_offset, 3)
        self.assertAlmostEqual(similarity_score, 1.0)
    
    def test_boundary_conditions(self):
        # Test alignment at image boundaries
        image_a = [[10, 20],
                   [30, 40]]
        
        image_b = [[10, 20, 0],
                   [30, 40, 0],
                   [0, 0, 0]]
        
        # Region at top-left corner
        row_offset, col_offset, similarity_score = find_optimal_alignment(
            image_a, image_b, 2, 2, 1
        )
        
        self.assertEqual(row_offset, 0)
        self.assertEqual(col_offset, 0)
        self.assertAlmostEqual(similarity_score, 1.0)

if __name__ == '__main__':
    unittest.main()