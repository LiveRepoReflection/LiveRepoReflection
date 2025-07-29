import math
from collections import OrderedDict
from functools import lru_cache
from typing import List, Union

class FractalExplorer:
    def __init__(self, cache_size: int = 10000):
        """Initialize the FractalExplorer with a specified cache size."""
        self._calculate_escape_time = lru_cache(maxsize=cache_size)(self._calculate_escape_time_uncached)
        self._initial_width = 3.0
        
    def calculate_region(
        self,
        real_start: float,
        imaginary_start: float,
        width: float,
        height: float,
        image_width: int,
        image_height: int,
        max_iterations: int
    ) -> List[List[int]]:
        """Calculate the fractal values for a specified region."""
        # Validate inputs
        self._validate_inputs(real_start, imaginary_start, width, height, 
                            image_width, image_height, max_iterations)
        
        # Calculate zoom factor and adjust iterations
        zoom_factor = self._initial_width / width
        adjusted_max_iterations = self._adjust_iterations(max_iterations, zoom_factor)
        
        # Initialize the result matrix
        result = [[0 for _ in range(image_width)] for _ in range(image_height)]
        
        # Calculate pixel size in complex plane
        dx = width / (image_width - 1) if image_width > 1 else width
        dy = height / (image_height - 1) if image_height > 1 else height
        
        # Calculate fractal values for each pixel
        for y in range(image_height):
            for x in range(image_width):
                # Map pixel coordinates to complex plane coordinates
                real = real_start + x * dx
                imag = imaginary_start - y * dy
                
                # Calculate escape time for this point
                result[y][x] = self._calculate_escape_time(
                    real, imag, adjusted_max_iterations)
                
        return result

    def _validate_inputs(
        self,
        real_start: float,
        imaginary_start: float,
        width: float,
        height: float,
        image_width: int,
        image_height: int,
        max_iterations: int
    ) -> None:
        """Validate input parameters."""
        if width <= 0:
            raise ValueError("Width must be positive")
        if height <= 0:
            raise ValueError("Height must be positive")
        if image_width <= 0:
            raise ValueError("Image width must be positive")
        if image_height <= 0:
            raise ValueError("Image height must be positive")
        if max_iterations <= 0:
            raise ValueError("Maximum iterations must be positive")

    def _adjust_iterations(self, base_iterations: int, zoom_factor: float) -> int:
        """Adjust iteration count based on zoom factor."""
        if zoom_factor <= 1:
            return base_iterations
        
        # Logarithmic scaling of iterations with zoom
        return int(base_iterations * (1 + math.log(zoom_factor, 2) / 2))

    def _calculate_escape_time_uncached(
        self,
        real: float,
        imag: float,
        max_iterations: int
    ) -> int:
        """Calculate the escape time for a given complex number."""
        c = complex(real, imag)
        z = complex(0, 0)
        
        # To handle precision issues at high zoom levels
        threshold = 2.0
        
        for i in range(max_iterations):
            # Check for overflow potential
            if abs(z.real) > threshold or abs(z.imag) > threshold:
                return i
            
            try:
                z = z * z + c
            except OverflowError:
                return i
                
            # Use squared magnitude for efficiency
            if (z.real * z.real + z.imag * z.imag) > 4.0:
                return i
                
        return max_iterations

    def clear_cache(self) -> None:
        """Clear the calculation cache."""
        self._calculate_escape_time.cache_clear()
