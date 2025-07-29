import unittest
from fractal_explorer import FractalExplorer

class FractalExplorerTest(unittest.TestCase):
    def setUp(self):
        self.explorer = FractalExplorer()

    def test_basic_mandelbrot_region(self):
        result = self.explorer.calculate_region(
            real_start=-2.0,
            imaginary_start=1.5,
            width=3.0,
            height=3.0,
            image_width=4,
            image_height=4,
            max_iterations=50
        )
        self.assertEqual(len(result), 4)  # Check rows
        self.assertEqual(len(result[0]), 4)  # Check columns
        
    def test_zoom_iteration_scaling(self):
        # Test at normal zoom level
        result1 = self.explorer.calculate_region(
            real_start=-2.0,
            imaginary_start=1.5,
            width=3.0,
            height=3.0,
            image_width=2,
            image_height=2,
            max_iterations=50
        )
        
        # Test at 10x zoom
        result2 = self.explorer.calculate_region(
            real_start=-0.2,
            imaginary_start=0.15,
            width=0.3,
            height=0.3,
            image_width=2,
            image_height=2,
            max_iterations=50
        )
        
        # The zoomed-in region should have higher iteration counts
        max_iter1 = max(max(row) for row in result1)
        max_iter2 = max(max(row) for row in result2)
        self.assertGreater(max_iter2, max_iter1)

    def test_edge_cases(self):
        # Test very small region (high zoom)
        result = self.explorer.calculate_region(
            real_start=-0.0001,
            imaginary_start=0.0001,
            width=0.0002,
            height=0.0002,
            image_width=2,
            image_height=2,
            max_iterations=50
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 2)

        # Test region containing origin
        result = self.explorer.calculate_region(
            real_start=-0.5,
            imaginary_start=0.5,
            width=1.0,
            height=1.0,
            image_width=2,
            image_height=2,
            max_iterations=50
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 2)

    def test_invalid_inputs(self):
        # Test negative width
        with self.assertRaises(ValueError):
            self.explorer.calculate_region(
                real_start=0.0,
                imaginary_start=0.0,
                width=-1.0,
                height=1.0,
                image_width=2,
                image_height=2,
                max_iterations=50
            )

        # Test negative height
        with self.assertRaises(ValueError):
            self.explorer.calculate_region(
                real_start=0.0,
                imaginary_start=0.0,
                width=1.0,
                height=-1.0,
                image_width=2,
                image_height=2,
                max_iterations=50
            )

        # Test zero image dimensions
        with self.assertRaises(ValueError):
            self.explorer.calculate_region(
                real_start=0.0,
                imaginary_start=0.0,
                width=1.0,
                height=1.0,
                image_width=0,
                image_height=2,
                max_iterations=50
            )

        # Test negative iterations
        with self.assertRaises(ValueError):
            self.explorer.calculate_region(
                real_start=0.0,
                imaginary_start=0.0,
                width=1.0,
                height=1.0,
                image_width=2,
                image_height=2,
                max_iterations=-1
            )

    def test_cache_behavior(self):
        # Test that repeated calculations of the same point use cache
        result1 = self.explorer.calculate_region(
            real_start=-2.0,
            imaginary_start=1.5,
            width=3.0,
            height=3.0,
            image_width=2,
            image_height=2,
            max_iterations=50
        )
        
        result2 = self.explorer.calculate_region(
            real_start=-2.0,
            imaginary_start=1.5,
            width=3.0,
            height=3.0,
            image_width=2,
            image_height=2,
            max_iterations=50
        )
        
        # Results should be identical
        for i in range(len(result1)):
            self.assertEqual(result1[i], result2[i])

    def test_precision_at_high_zoom(self):
        # Test precision at very high zoom levels
        result1 = self.explorer.calculate_region(
            real_start=-0.25,
            imaginary_start=0,
            width=0.01,
            height=0.01,
            image_width=2,
            image_height=2,
            max_iterations=50
        )
        
        result2 = self.explorer.calculate_region(
            real_start=-0.25,
            imaginary_start=0,
            width=0.0001,
            height=0.0001,
            image_width=2,
            image_height=2,
            max_iterations=50
        )
        
        # Different zoom levels should produce different results
        any_different = False
        for i in range(len(result1)):
            for j in range(len(result1[i])):
                if result1[i][j] != result2[i][j]:
                    any_different = True
                    break
        self.assertTrue(any_different)

if __name__ == '__main__':
    unittest.main()